from fastapi import FastAPI, APIRouter, HTTPException, Query, Request, Header, Depends, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
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
import shutil
import aiofiles

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

# Create upload directories
UPLOAD_DIR = Path(__file__).parent / "uploads"
AUDIO_DIR = UPLOAD_DIR / "audio"
IMAGES_DIR = UPLOAD_DIR / "images"

# Create directories if they don't exist
UPLOAD_DIR.mkdir(exist_ok=True)
AUDIO_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(exist_ok=True)

# Mount static files for serving uploaded content
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

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

# Musician Community Models
class MusicianProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    stage_name: str
    bio: Optional[str] = None
    instruments: List[str] = []
    genres: List[str] = []
    experience_level: str = "Intermédiaire"  # Débutant, Intermédiaire, Avancé, Professionnel
    region: str = "International"
    city: Optional[str] = None
    looking_for: List[str] = []  # Collaboration, Jam Session, Apprentissage, Performance
    social_links: Optional[Dict[str, str]] = {}
    profile_image: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True

class CommunityPost(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    content: str
    post_type: str = "idea"  # idea, collaboration, question, event, showcase
    tags: List[str] = []
    media_urls: List[str] = []
    likes_count: int = 0
    comments_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True

class PostComment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    post_id: str
    user_id: str
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PostLike(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    post_id: str
    user_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MusicianMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str
    recipient_id: str
    subject: Optional[str] = None
    content: str
    is_read: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Request/Response Models for Community
class MusicianProfileCreate(BaseModel):
    stage_name: str
    bio: Optional[str] = None
    instruments: List[str] = []
    genres: List[str] = []
    experience_level: str = "Intermédiaire"
    region: str = "International"
    city: Optional[str] = None
    looking_for: List[str] = []
    social_links: Optional[Dict[str, str]] = {}

class PostCreate(BaseModel):
    title: str
    content: str
    post_type: str = "idea"
    tags: List[str] = []

class CommentCreate(BaseModel):
    content: str

class MessageCreate(BaseModel):
    recipient_id: str
    subject: Optional[str] = None
    content: str

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

# File Upload Models
class FileUploadResponse(BaseModel):
    filename: str
    file_url: str
    file_type: str
    size: int

class TrackUploadRequest(BaseModel):
    title: str
    artist: str = "Simon Messela (fifi Ribana)"
    region: str
    style: str
    instrument: Optional[str] = None
    duration: int
    bpm: Optional[int] = None
    mood: Optional[str] = None
    price: float
    description: Optional[str] = None

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

def prepare_from_mongo(item):
    """Prepare MongoDB document for response by removing MongoDB _id and converting ObjectId to string"""
    if isinstance(item, dict):
        # Remove MongoDB _id field if present
        if '_id' in item:
            del item['_id']
        # Convert any remaining ObjectId fields to strings if needed
        for key, value in item.items():
            if hasattr(value, '__str__') and 'ObjectId' in str(type(value)):
                item[key] = str(value)
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

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
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

# File Upload Routes
@api_router.post("/upload/audio", response_model=FileUploadResponse)
async def upload_audio_file(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    """Upload an audio file"""
    if not file.content_type or not file.content_type.startswith('audio/'):
        raise HTTPException(status_code=400, detail="File must be an audio file")
    
    # Generate unique filename
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'mp3'
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = AUDIO_DIR / unique_filename
    
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        file_url = f"/uploads/audio/{unique_filename}"
        file_size = len(content)
        
        return FileUploadResponse(
            filename=unique_filename,
            file_url=file_url,
            file_type=file.content_type,
            size=file_size
        )
    except Exception as e:
        logger.error(f"Error uploading audio file: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload audio file")

@api_router.post("/upload/image", response_model=FileUploadResponse)
async def upload_image_file(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    """Upload an image file"""
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image file")
    
    # Generate unique filename
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = IMAGES_DIR / unique_filename
    
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        file_url = f"/uploads/images/{unique_filename}"
        file_size = len(content)
        
        return FileUploadResponse(
            filename=unique_filename,
            file_url=file_url,
            file_type=file.content_type,
            size=file_size
        )
    except Exception as e:
        logger.error(f"Error uploading image file: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload image file")

# Track upload form data parser
async def parse_track_form_data(
    title: str = Form(...),
    artist: str = Form(...),
    region: str = Form(...),
    style: str = Form(...),
    instrument: Optional[str] = Form(None),
    duration: int = Form(...),
    bpm: int = Form(...),
    mood: str = Form(...),
    price: float = Form(...),
    description: Optional[str] = Form(None)
) -> TrackUploadRequest:
    """Parse and validate track form data"""
    try:
        return TrackUploadRequest(
            title=title,
            artist=artist,
            region=region,
            style=style,
            instrument=instrument,
            duration=duration,
            bpm=bpm,
            mood=mood,
            price=price,
            description=description
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid form data: {str(e)}")

@api_router.post("/tracks/upload", response_model=Track)
async def create_track_with_files(
    audio_file: UploadFile = File(...),
    image_file: UploadFile = File(...),
    preview_file: Optional[UploadFile] = File(None),
    track_data: TrackUploadRequest = Depends(parse_track_form_data),
    current_user: User = Depends(get_current_user)
):
    """Create a new track with file uploads"""
    try:
        # Upload audio file
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="Audio file must be an audio file")
        
        audio_extension = audio_file.filename.split('.')[-1] if '.' in audio_file.filename else 'mp3'
        audio_filename = f"audio_{uuid.uuid4()}.{audio_extension}"
        audio_path = AUDIO_DIR / audio_filename
        
        async with aiofiles.open(audio_path, 'wb') as f:
            audio_content = await audio_file.read()
            await f.write(audio_content)
        
        audio_url = f"/uploads/audio/{audio_filename}"
        
        # Upload image file
        if not image_file.content_type or not image_file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Image file must be an image file")
        
        image_extension = image_file.filename.split('.')[-1] if '.' in image_file.filename else 'jpg'
        image_filename = f"cover_{uuid.uuid4()}.{image_extension}"
        image_path = IMAGES_DIR / image_filename
        
        async with aiofiles.open(image_path, 'wb') as f:
            image_content = await image_file.read()
            await f.write(image_content)
        
        image_url = f"/uploads/images/{image_filename}"
        
        # Upload preview file if provided
        preview_url = None
        if preview_file:
            if not preview_file.content_type or not preview_file.content_type.startswith('audio/'):
                raise HTTPException(status_code=400, detail="Preview file must be an audio file")
            
            preview_extension = preview_file.filename.split('.')[-1] if '.' in preview_file.filename else 'mp3'
            preview_filename = f"preview_{uuid.uuid4()}.{preview_extension}"
            preview_path = AUDIO_DIR / preview_filename
            
            async with aiofiles.open(preview_path, 'wb') as f:
                preview_content = await preview_file.read()
                await f.write(preview_content)
            
            preview_url = f"/uploads/audio/{preview_filename}"
        
        # Create track with uploaded files
        track = Track(
            **track_data.dict(),
            audio_url=audio_url,
            artwork_url=image_url,
            preview_url=preview_url or audio_url
        )
        
        await db.tracks.insert_one(prepare_for_mongo(track.dict()))
        return track
        
    except Exception as e:
        logger.error(f"Error creating track with files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create track: {str(e)}")

# Admin Routes for Simon Messela
@api_router.get("/admin/my-tracks")
async def get_my_tracks(current_user: User = Depends(get_current_user)):
    """Get tracks by Simon Messela"""
    tracks = await db.tracks.find({
        "$or": [
            {"artist": {"$regex": "Simon Messela", "$options": "i"}},
            {"artist": {"$regex": "fifi Ribana", "$options": "i"}}
        ]
    }).to_list(100)
    return [Track(**parse_from_mongo(track)) for track in tracks]

@api_router.delete("/admin/tracks/{track_id}")
async def delete_my_track(track_id: str, current_user: User = Depends(get_current_user)):
    """Delete a track (admin only)"""
    track = await db.tracks.find_one({"id": track_id})
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    
    # Only allow deletion of Simon Messela tracks for security
    if "Simon Messela" not in track.get("artist", "") and "fifi Ribana" not in track.get("artist", ""):
        raise HTTPException(status_code=403, detail="Not authorized to delete this track")
    
    await db.tracks.delete_one({"id": track_id})
    return {"message": "Track deleted successfully"}

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
        
        # Add comprehensive global music catalog
        additional_tracks = [
            # Afrique
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
                artwork_url="https://images.unsplash.com/photo-1565719178004-420e3480e2b5?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzh8MHwxfHNlYXJjaHwxfHx3b3JsZCUyMG11c2ljJTIwaW5zdHJ1bWVudHN8ZW58MHx8fHwxNzU3MDI2ODgyfDA&ixlib=rb-4.1.0&q=85",
                price=3.29,
                description="Rythmes endiablés du Bikutsi camerounais traditionnel avec balafons authentiques"
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
                artwork_url="https://images.unsplash.com/photo-1556484687-30636164638b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwxfHxjdWx0dXJhbCUyMGRpdmVyc2l0eXxlbnwwfHx8fDE3NTcwMjY4ODl8MA&ixlib=rb-4.1.0&q=85",
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
                artwork_url="https://images.unsplash.com/photo-1516146544193-b54a65682f16?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwyfHxjdWx0dXJhbCUyMGRpdmVyc2l0eXxlbnwwfHx8fDE3NTcwMjY4ODl8MA&ixlib=rb-4.1.0&q=85",
                price=4.19,
                description="Les mélodies ensorcelantes du Soukous congolais"
            ),
            TrackCreate(
                title="Desert Winds",
                artist="Aminata Traoré",
                region="Afrique",
                style="Touareg Blues",
                instrument="Guitare électrique",
                duration=385,
                bpm=95,
                mood="Hypnotique",
                audio_url="https://example.com/desert-winds.mp3",
                preview_url="https://example.com/previews/desert-winds-preview.mp3",
                artwork_url="https://images.pexels.com/photos/29333488/pexels-photo-29333488.jpeg",
                price=4.99,
                description="Blues du désert avec guitares électriques et percussions traditionnelles"
            ),
            
            # Asie
            TrackCreate(
                title="Chennai Nights",
                artist="Ravi Shankar Jr.",
                region="Asie",
                style="Carnatic Fusion",
                instrument="Sitar",
                duration=420,
                bpm=120,
                mood="Spirituel",
                audio_url="https://example.com/chennai-nights.mp3",
                preview_url="https://example.com/previews/chennai-nights-preview.mp3",
                artwork_url="https://images.unsplash.com/photo-1651931802891-1e200feafefe?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzh8MHwxfHNlYXJjaHwyfHx3b3JsZCUyMG11c2ljJTIwaW5zdHJ1bWVudHN8ZW58MHx8fHwxNzU3MDI2ODgyfDA&ixlib=rb-4.1.0&q=85",
                price=5.29,
                description="Fusion moderne de la musique carnatique du Tamil Nadu"
            ),
            TrackCreate(
                title="Tokyo Rain",
                artist="Yuki Tanaka",
                region="Asie",
                style="J-Pop Traditionnel",
                instrument="Shamisen",
                duration=240,
                bpm=110,
                mood="Mélancolique",
                audio_url="https://example.com/tokyo-rain.mp3",
                preview_url="https://example.com/previews/tokyo-rain-preview.mp3",
                artwork_url="https://images.unsplash.com/photo-1624352545753-7001a44a0f19?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzh8MHwxfHNlYXJjaHw0fHx3b3JsZCUyMG11c2ljJTIwaW5zdHJ1bWVudHN8ZW58MHx8fHwxNzU3MDI2ODgyfDA&ixlib=rb-4.1.0&q=85",
                price=4.49,
                description="Pop japonaise moderne mêlée aux sonorités traditionnelles du shamisen"
            ),
            
            # Europe
            TrackCreate(
                title="Andalusian Fire",
                artist="Carmen Delgado",
                region="Europe",
                style="Flamenco",
                instrument="Guitare flamenca",
                duration=320,
                bpm=160,
                mood="Passionné",
                audio_url="https://example.com/andalusian-fire.mp3",
                preview_url="https://example.com/previews/andalusian-fire-preview.mp3",
                artwork_url="https://images.pexels.com/photos/33710402/pexels-photo-33710402.jpeg",
                price=4.79,
                description="Flamenco traditionnel d'Andalousie avec guitares et castagnettes"
            ),
            TrackCreate(
                title="Celtic Dreams",
                artist="Siobhan O'Brien",
                region="Europe",
                style="Folk Celtique",
                instrument="Tin Whistle",
                duration=280,
                bpm=90,
                mood="Nostalgique",
                audio_url="https://example.com/celtic-dreams.mp3",
                preview_url="https://example.com/previews/celtic-dreams-preview.mp3",
                artwork_url="https://images.pexels.com/photos/33714882/pexels-photo-33714882.jpeg",
                price=3.99,
                description="Mélodies celtiques irlandaises aux sonorités mystiques"
            ),
            
            # Amérique du Sud
            TrackCreate(
                title="Rio Carnival",
                artist="Carlos Santos",
                region="Amérique du Sud",
                style="Samba",
                instrument="Cuíca",
                duration=265,
                bpm=180,
                mood="Festif",
                audio_url="https://example.com/rio-carnival.mp3",
                preview_url="https://example.com/previews/rio-carnival-preview.mp3",
                artwork_url="https://images.unsplash.com/photo-1565719178004-420e3480e2b5?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzh8MHwxfHNlYXJjaHwxfHx3b3JsZCUyMG11c2ljJTIwaW5zdHJ1bWVudHN8ZW58MHx8fHwxNzU3MDI2ODgyfDA&ixlib=rb-4.1.0&q=85",
                price=3.99,
                description="Samba authentique du carnaval de Rio avec percussions brésiliennes"
            ),
            TrackCreate(
                title="Tango Midnight",
                artist="Isabella Rodriguez",
                region="Amérique du Sud",
                style="Tango",
                instrument="Bandoneón",
                duration=315,
                bpm=100,
                mood="Romantique",
                audio_url="https://example.com/tango-midnight.mp3",
                preview_url="https://example.com/previews/tango-midnight-preview.mp3",
                artwork_url="https://images.unsplash.com/photo-1556484687-30636164638b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwxfHxjdWx0dXJhbCUyMGRpdmVyc2l0eXxlbnwwfHx8fDE3NTcwMjY4ODl8MA&ixlib=rb-4.1.0&q=85",
                price=4.59,
                description="Tango argentin passionné avec bandoneón traditionnel"
            ),
            
            # Océanie
            TrackCreate(
                title="Dreamtime Echoes",
                artist="Billy Kooljarra",
                region="Océanie",
                style="Aborigène Contemporain",
                instrument="Didgeridoo",
                duration=390,
                bpm=70,
                mood="Spirituel",
                audio_url="https://example.com/dreamtime-echoes.mp3",
                preview_url="https://example.com/previews/dreamtime-echoes-preview.mp3",
                artwork_url="https://images.unsplash.com/photo-1651931802891-1e200feafefe?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzh8MHwxfHNlYXJjaHwyfHx3b3JsZCUyMG11c2ljJTIwaW5zdHJ1bWVudHN8ZW58MHx8fHwxNzU3MDI2ODgyfDA&ixlib=rb-4.1.0&q=85",
                price=5.99,
                description="Musique aborigène australienne moderne avec didgeridoo authentique"
            ),
            
            # Simon Messela tracks
            TrackCreate(
                title="Universal Pulse",
                artist="Simon Messela (fifi Ribana)",
                region="Global Fusion",
                style="World Electronic",
                instrument="Synthétiseur + Balafon",
                duration=355,
                bpm=128,
                mood="Énergique",
                audio_url="https://example.com/universal-pulse.mp3",
                preview_url="https://example.com/previews/universal-pulse-preview.mp3",
                artwork_url="https://images.pexels.com/photos/29333488/pexels-photo-29333488.jpeg",
                price=6.99,
                description="Fusion électronique mondiale par le fondateur d'US EXPLO, mêlant balafon et synthés modernes"
            ),
            TrackCreate(
                title="Bikutsi 2025",
                artist="Simon Messela (fifi Ribana)",
                region="Afrique",
                style="Bikutsi Moderne",
                instrument="Balafon + Synthétiseur",
                duration=285,
                bpm=145,
                mood="Énergique",
                audio_url="https://example.com/bikutsi-2025.mp3",
                preview_url="https://example.com/previews/bikutsi-2025-preview.mp3",
                artwork_url="https://images.unsplash.com/photo-1516146544193-b54a65682f16?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwyfHxjdWx0dXJhbCUyMGRpdmVyc2l0eXxlbnwwfHx8fDE3NTcwMjY4ODl8MA&ixlib=rb-4.1.0&q=85",
                price=5.99,
                description="Réinterprétation moderne du Bikutsi traditionnel camerounais"
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
        
        # Add featured collections
        collection_count = await db.collections.count_documents({})
        if collection_count < 5:
            logger.info("Adding featured collections...")
            
            sample_collections = [
                CollectionCreate(
                    title="Rythmes d'Afrique",
                    description="Une exploration des rythmes africains traditionnels et modernes, du Bikutsi au Soukous",
                    tracks=[],  # Will be populated with actual track IDs
                    image_url="https://images.unsplash.com/photo-1565719178004-420e3480e2b5?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzh8MHwxfHNlYXJjaHwxfHx3b3JsZCUyMG11c2ljJTIwaW5zdHJ1bWVudHN8ZW58MHx8fHwxNzU3MDI2ODgyfDA&ixlib=rb-4.1.0&q=85",
                    featured=True
                ),
                CollectionCreate(
                    title="Sonorités Asiatiques",
                    description="Du sitar indien au shamisen japonais, découvrez la richesse musicale de l'Asie",
                    tracks=[],
                    image_url="https://images.unsplash.com/photo-1651931802891-1e200feafefe?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzh8MHwxfHNlYXJjaHwyfHx3b3JsZCUyMG11c2ljJTIwaW5zdHJ1bWVudHN8ZW58MHx8fHwxNzU3MDI2ODgyfDA&ixlib=rb-4.1.0&q=85",
                    featured=True
                ),
                CollectionCreate(
                    title="Simon Messela Universe",
                    description="L'univers musical complet du fondateur d'US EXPLO, de l'Afrique au monde entier",
                    tracks=[],
                    image_url="https://images.pexels.com/photos/29333488/pexels-photo-29333488.jpeg",
                    featured=True
                ),
                CollectionCreate(
                    title="Fusion Mondiale",
                    description="Quand les traditions se rencontrent avec la modernité : fusion électronique mondiale",
                    tracks=[],
                    image_url="https://images.unsplash.com/photo-1556484687-30636164638b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwxfHxjdWx0dXJhbCUyMGRpdmVyc2l0eXxlbnwwfHx8fDE3NTcwMjY4ODl8MA&ixlib=rb-4.1.0&q=85",
                    featured=True
                ),
                CollectionCreate(
                    title="Découvertes du Mois",
                    description="Notre sélection mensuelle des nouveautés musicales du monde entier",
                    tracks=[],
                    image_url="https://images.unsplash.com/photo-1516146544193-b54a65682f16?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwyfHxjdWx0dXJhbCUyMGRpdmVyc2l0eXxlbnwwfHx8fDE3NTcwMjY4ODl8MA&ixlib=rb-4.1.0&q=85",
                    featured=True
                )
            ]
            
            for collection_data in sample_collections:
                existing = await db.collections.find_one({"title": collection_data.title})
                if not existing:
                    collection = Collection(**collection_data.dict())
                    await db.collections.insert_one(prepare_for_mongo(collection.dict()))

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    logger.info("Database connection closed")