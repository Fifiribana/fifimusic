from fastapi import FastAPI, APIRouter, HTTPException, Query, Request, Header, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import uuid
from datetime import datetime, timezone
import jwt
from passlib.context import CryptContext
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security setup
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.environ.get('SECRET_KEY', 'us-explo-secret-key-2025')
ALGORITHM = "HS256"

# Stripe setup
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY', '')

# Create the main app without a prefix
app = FastAPI(title="US EXPLO API", description="Universal Sound Exploration API", version="2.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models for US EXPLO

# User Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    username: str
    hashed_password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    preferences: Optional[List[str]] = []
    favorite_regions: Optional[List[str]] = []
    is_active: bool = True

class UserCreate(BaseModel):
    email: str
    username: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    created_at: datetime
    preferences: Optional[List[str]] = []
    favorite_regions: Optional[List[str]] = []

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Music Track Models
class Track(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    artist: str
    region: str
    style: str
    instrument: Optional[str] = None
    duration: int  # in seconds
    bpm: Optional[int] = None
    mood: Optional[str] = None
    audio_url: str
    preview_url: Optional[str] = None  # 30-second preview
    artwork_url: str
    price: float
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    downloads: int = 0
    likes: int = 0
    is_featured: bool = False

class TrackCreate(BaseModel):
    title: str
    artist: str
    region: str
    style: str
    instrument: Optional[str] = None
    duration: int
    bpm: Optional[int] = None
    mood: Optional[str] = None
    audio_url: str
    preview_url: Optional[str] = None
    artwork_url: str
    price: float
    description: Optional[str] = None

# Collection Models
class Collection(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    tracks: List[str]  # Track IDs
    image_url: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    featured: bool = False

class CollectionCreate(BaseModel):
    title: str
    description: str
    tracks: List[str]
    image_url: str
    featured: bool = False

# Payment Models
class PaymentTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    track_ids: List[str]
    amount: float
    currency: str = "eur"
    payment_status: str = "pending"  # pending, completed, failed, cancelled
    stripe_status: str = "initiated"
    metadata: Optional[Dict] = {}
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PurchaseRequest(BaseModel):
    track_ids: List[str]
    user_email: Optional[str] = None

class CheckoutRequest(BaseModel):
    host_url: str
    track_ids: List[str]
    user_email: Optional[str] = None

# Search Models
class SearchResult(BaseModel):
    tracks: List[Track]
    total: int
    page: int
    per_page: int

# Original status check models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

# Helper functions
def prepare_for_mongo(data):
    """Convert datetime objects to ISO strings for MongoDB storage"""
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
    return data

def parse_from_mongo(item):
    """Convert ISO strings back to datetime objects from MongoDB"""
    if isinstance(item, dict):
        for key, value in item.items():
            if key in ['created_at', 'timestamp', 'updated_at'] and isinstance(value, str):
                try:
                    item[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except ValueError:
                    pass
    return item

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.now(timezone.utc).timestamp() + 86400})  # 24 hours
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = security):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user = await db.users.find_one({"id": user_id})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return User(**parse_from_mongo(user))

# Routes

# Original routes
@api_router.get("/")
async def root():
    return {"message": "US EXPLO API v2.0 - Universal Sound Exploration with Audio & Payments"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    await db.status_checks.insert_one(prepare_for_mongo(status_obj.dict()))
    return status_obj

# Authentication Routes
@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    existing_username = await db.users.find_one({"username": user_data.username})
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password
    )
    
    await db.users.insert_one(prepare_for_mongo(user.dict()))
    
    # Create token
    access_token = create_access_token(data={"sub": user.id})
    user_response = UserResponse(**user.dict())
    
    return Token(access_token=access_token, token_type="bearer", user=user_response)

@api_router.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin):
    user = await db.users.find_one({"email": user_data.email})
    if not user or not verify_password(user_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user_obj = User(**parse_from_mongo(user))
    access_token = create_access_token(data={"sub": user_obj.id})
    user_response = UserResponse(**user_obj.dict())
    
    return Token(access_token=access_token, token_type="bearer", user=user_response)

@api_router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse(**current_user.dict())

# Music Track Routes
@api_router.get("/tracks", response_model=List[Track])
async def get_tracks(
    region: Optional[str] = Query(None, description="Filter by region"),
    style: Optional[str] = Query(None, description="Filter by style"),
    instrument: Optional[str] = Query(None, description="Filter by instrument"),
    mood: Optional[str] = Query(None, description="Filter by mood"),
    featured: Optional[bool] = Query(None, description="Filter by featured status"),
    limit: int = Query(20, ge=1, le=100, description="Number of tracks to return"),
    offset: int = Query(0, ge=0, description="Number of tracks to skip")
):
    """Get tracks with optional filtering"""
    query = {}
    if region:
        query["region"] = {"$regex": region, "$options": "i"}
    if style:
        query["style"] = {"$regex": style, "$options": "i"}
    if instrument:
        query["instrument"] = {"$regex": instrument, "$options": "i"}
    if mood:
        query["mood"] = {"$regex": mood, "$options": "i"}
    if featured is not None:
        query["is_featured"] = featured
    
    tracks = await db.tracks.find(query).skip(offset).limit(limit).to_list(limit)
    return [Track(**parse_from_mongo(track)) for track in tracks]

@api_router.get("/tracks/{track_id}", response_model=Track)
async def get_track(track_id: str):
    """Get a single track by ID"""
    track = await db.tracks.find_one({"id": track_id})
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    return Track(**parse_from_mongo(track))

@api_router.post("/tracks", response_model=Track)
async def create_track(track_data: TrackCreate):
    """Create a new track"""
    track = Track(**track_data.dict())
    await db.tracks.insert_one(prepare_for_mongo(track.dict()))
    return track

@api_router.put("/tracks/{track_id}/like")
async def like_track(track_id: str):
    """Increment track likes"""
    result = await db.tracks.update_one(
        {"id": track_id},
        {"$inc": {"likes": 1}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Track not found")
    return {"message": "Track liked successfully"}

@api_router.put("/tracks/{track_id}/download")
async def download_track(track_id: str):
    """Increment track downloads"""
    result = await db.tracks.update_one(
        {"id": track_id},
        {"$inc": {"downloads": 1}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Track not found")
    return {"message": "Download recorded successfully"}

# Collection Routes
@api_router.get("/collections", response_model=List[Collection])
async def get_collections(featured: Optional[bool] = Query(None, description="Filter by featured status")):
    """Get collections, optionally filtered by featured status"""
    query = {}
    if featured is not None:
        query["featured"] = featured
    
    collections = await db.collections.find(query).to_list(100)
    return [Collection(**parse_from_mongo(collection)) for collection in collections]

@api_router.get("/collections/{collection_id}", response_model=Collection)
async def get_collection(collection_id: str):
    """Get a single collection by ID"""
    collection = await db.collections.find_one({"id": collection_id})
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return Collection(**parse_from_mongo(collection))

@api_router.post("/collections", response_model=Collection)
async def create_collection(collection_data: CollectionCreate):
    """Create a new collection"""
    collection = Collection(**collection_data.dict())
    await db.collections.insert_one(prepare_for_mongo(collection.dict()))
    return collection

# Payment Routes
@api_router.post("/checkout/create")
async def create_checkout_session(request: CheckoutRequest):
    """Create a Stripe checkout session for purchasing tracks"""
    try:
        # Validate tracks exist and get pricing
        tracks = []
        total_amount = 0.0
        
        for track_id in request.track_ids:
            track = await db.tracks.find_one({"id": track_id})
            if not track:
                raise HTTPException(status_code=404, detail=f"Track {track_id} not found")
            tracks.append(track)
            total_amount += track["price"]
        
        if total_amount <= 0:
            raise HTTPException(status_code=400, detail="Invalid total amount")
        
        # Initialize Stripe checkout
        webhook_url = f"{request.host_url}/api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
        
        # Create checkout session request
        success_url = f"{request.host_url}/success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{request.host_url}/cancel"
        
        metadata = {
            "track_ids": ",".join(request.track_ids),
            "user_email": request.user_email or "",
            "source": "us_explo_music_purchase"
        }
        
        checkout_request = CheckoutSessionRequest(
            amount=total_amount,
            currency="eur",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata
        )
        
        # Create session with Stripe
        session: CheckoutSessionResponse = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Store transaction in database
        transaction = PaymentTransaction(
            session_id=session.session_id,
            user_email=request.user_email,
            track_ids=request.track_ids,
            amount=total_amount,
            currency="eur",
            payment_status="pending",
            stripe_status="initiated",
            metadata=metadata
        )
        
        await db.payment_transactions.insert_one(prepare_for_mongo(transaction.dict()))
        
        return {"checkout_url": session.url, "session_id": session.session_id}
        
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create checkout session: {str(e)}")

@api_router.get("/checkout/status/{session_id}")
async def get_checkout_status(session_id: str):
    """Get the status of a checkout session"""
    try:
        # Get transaction from database
        transaction = await db.payment_transactions.find_one({"session_id": session_id})
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Check with Stripe if not already completed
        if transaction["payment_status"] != "completed":
            stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
            status_response: CheckoutStatusResponse = await stripe_checkout.get_checkout_status(session_id)
            
            # Update transaction status
            new_payment_status = "completed" if status_response.payment_status == "paid" else "pending"
            if status_response.status == "expired":
                new_payment_status = "cancelled"
            
            # Update only if status changed
            if new_payment_status != transaction["payment_status"]:
                await db.payment_transactions.update_one(
                    {"session_id": session_id},
                    {
                        "$set": {
                            "payment_status": new_payment_status,
                            "stripe_status": status_response.status,
                            "updated_at": datetime.now(timezone.utc).isoformat()
                        }
                    }
                )
                
                # If payment completed, increment download counts
                if new_payment_status == "completed":
                    for track_id in transaction["track_ids"]:
                        await db.tracks.update_one(
                            {"id": track_id},
                            {"$inc": {"downloads": 1}}
                        )
            
            return {
                "status": status_response.status,
                "payment_status": status_response.payment_status,
                "amount_total": status_response.amount_total,
                "currency": status_response.currency
            }
        
        return {
            "status": "complete",
            "payment_status": "paid",
            "amount_total": int(transaction["amount"] * 100),  # Convert to cents
            "currency": transaction["currency"]
        }
        
    except Exception as e:
        logger.error(f"Error checking checkout status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to check status: {str(e)}")

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    try:
        body = await request.body()
        stripe_signature = request.headers.get("Stripe-Signature")
        
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
        webhook_response = await stripe_checkout.handle_webhook(body, stripe_signature)
        
        if webhook_response.event_type in ["checkout.session.completed", "payment_intent.succeeded"]:
            # Update transaction status
            await db.payment_transactions.update_one(
                {"session_id": webhook_response.session_id},
                {
                    "$set": {
                        "payment_status": "completed",
                        "stripe_status": "completed",
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            # Get transaction to update download counts
            transaction = await db.payment_transactions.find_one({"session_id": webhook_response.session_id})
            if transaction:
                for track_id in transaction["track_ids"]:
                    await db.tracks.update_one(
                        {"id": track_id},
                        {"$inc": {"downloads": 1}}
                    )
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=400, detail="Webhook processing failed")

# User Purchase History
@api_router.get("/purchases/history")
async def get_purchase_history(current_user: User = Depends(get_current_user)):
    """Get user's purchase history"""
    transactions = await db.payment_transactions.find({
        "user_email": current_user.email,
        "payment_status": "completed"
    }).to_list(100)
    
    return [PaymentTransaction(**parse_from_mongo(transaction)) for transaction in transactions]

# Search Route
@api_router.get("/search", response_model=SearchResult)
async def search_tracks(
    q: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page")
):
    """Search tracks by title, artist, region, style, or instrument"""
    query = {
        "$or": [
            {"title": {"$regex": q, "$options": "i"}},
            {"artist": {"$regex": q, "$options": "i"}},
            {"region": {"$regex": q, "$options": "i"}},
            {"style": {"$regex": q, "$options": "i"}},
            {"instrument": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}}
        ]
    }
    
    total = await db.tracks.count_documents(query)
    offset = (page - 1) * per_page
    
    tracks = await db.tracks.find(query).skip(offset).limit(per_page).to_list(per_page)
    
    return SearchResult(
        tracks=[Track(**parse_from_mongo(track)) for track in tracks],
        total=total,
        page=page,
        per_page=per_page
    )

# Region Statistics Route
@api_router.get("/regions/stats")
async def get_region_stats():
    """Get statistics about tracks by region"""
    pipeline = [
        {"$group": {"_id": "$region", "count": {"$sum": 1}, "total_likes": {"$sum": "$likes"}}},
        {"$sort": {"count": -1}}
    ]
    
    stats = await db.tracks.aggregate(pipeline).to_list(100)
    return [{"region": stat["_id"], "track_count": stat["count"], "total_likes": stat["total_likes"]} for stat in stats]

# Style Statistics Route
@api_router.get("/styles/stats")
async def get_style_stats():
    """Get statistics about tracks by style"""
    pipeline = [
        {"$group": {"_id": "$style", "count": {"$sum": 1}, "avg_price": {"$avg": "$price"}}},
        {"$sort": {"count": -1}}
    ]
    
    stats = await db.tracks.aggregate(pipeline).to_list(100)
    return [{"style": stat["_id"], "track_count": stat["count"], "avg_price": round(stat["avg_price"], 2)} for stat in stats]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Startup event to initialize sample data
@app.on_event("startup")
async def startup_event():
    """Initialize the database with sample data"""
    logger.info("Starting US EXPLO API v2.0...")
    
    # Check if we already have sample data
    track_count = await db.tracks.count_documents({})
    if track_count < 10:  # Add more sample data
        logger.info("Adding additional sample data...")
        
        # Add preview URLs to existing sample tracks
        additional_tracks = [
            TrackCreate(
                title="Éboué Éboué",
                artist="Charlotte Mbango",
                region="Afrique",
                style="Bikutsi",
                instrument="Balafon",
                duration=298,
                bpm=140,
                mood="Énergique",
                audio_url="https://example.com/eboue-eboue.mp3",
                preview_url="https://example.com/previews/eboue-eboue-preview.mp3",
                artwork_url="https://images.unsplash.com/photo-1565719178004-420e3480e2b5?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NjZ8MHwxfHNlYXJjaHw0fHxnbG9iYWwlMjBpbnN0cnVtZW50c3xlbnwwfHx8fDE3NTcwMTE1NDZ8MA&ixlib=rb-4.1.0&q=85",
                price=3.29,
                description="Rythmes endiablés du Bikutsi camerounais traditionnel"
            ),
            TrackCreate(
                title="Soul Makossa",
                artist="Emmanuel Ndongo",
                region="Afrique",
                style="Makossa",
                instrument="Saxophone",
                duration=275,
                bpm=125,
                mood="Festif",
                audio_url="https://example.com/soul-makossa.mp3",
                preview_url="https://example.com/previews/soul-makossa-preview.mp3",
                artwork_url="https://images.unsplash.com/photo-1556484687-30636164638b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODB8MHwxfHNlYXJjaHwxfHxjdWx0dXJhbCUyMGRpdmVyc2l0eXxlbnwwfHx8fDE3NTcwMTE1NTJ8MA&ixlib=rb-4.1.0&q=85",
                price=3.79,
                description="Le groove irrésistible du Makossa de Douala"
            ),
            TrackCreate(
                title="Kinshasa Dreams",
                artist="Papa Wemba Jr.",
                region="Afrique",
                style="Soukous",
                instrument="Guitare",
                duration=342,
                bpm=135,
                mood="Dansant",
                audio_url="https://example.com/kinshasa-dreams.mp3",
                preview_url="https://example.com/previews/kinshasa-dreams-preview.mp3",
                artwork_url="https://images.unsplash.com/photo-1516146544193-b54a65682f16?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODB8MHwxfHNlYXJjaHwyfHxjdWx0dXJhbCUyMGRpdmVyc2l0eXxlbnwwfHx8fDE3NTcwMTE1NTJ8MA&ixlib=rb-4.1.0&q=85",
                price=4.19,
                description="Les mélodies ensorcelantes du Soukous congolais"
            )
        ]
        
        # Insert additional sample tracks
        for track_data in additional_tracks:
            # Check if track already exists
            existing = await db.tracks.find_one({"title": track_data.title})
            if not existing:
                track = Track(**track_data.dict())
                await db.tracks.insert_one(prepare_for_mongo(track.dict()))
        
        logger.info("Additional sample data initialized successfully!")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    logger.info("Database connection closed")