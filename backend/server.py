from fastapi import FastAPI, APIRouter, HTTPException, Query, Request, Depends, UploadFile, File, Form, Header
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
import time
import jwt
from passlib.context import CryptContext
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest
from emergentintegrations.llm.chat import LlmChat, UserMessage
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

# Subscription System Models
class SubscriptionPlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  # Basic, Pro, Premium
    description: str
    price_monthly: float
    price_yearly: float
    features: List[str] = []
    max_uploads_per_month: int = 5
    max_groups: int = 3
    can_sell_music: bool = False
    can_create_events: bool = False
    priority_support: bool = False
    analytics_access: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True

class UserSubscription(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    plan_id: str
    stripe_subscription_id: Optional[str] = None
    status: str = "active"  # active, canceled, past_due, unpaid
    billing_cycle: str = "monthly"  # monthly, yearly
    current_period_start: datetime
    current_period_end: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Music Marketplace Models
class MusicListing(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    seller_id: str  # user_id of the seller
    track_id: str
    listing_type: str = "sale"  # sale, license, both
    sale_price: Optional[float] = None
    license_price: Optional[float] = None
    license_terms: Optional[str] = None  # commercial, non-commercial, etc.
    royalty_percentage: float = 0.0  # for ongoing royalties
    is_exclusive: bool = False
    status: str = "active"  # active, sold, suspended
    commission_rate: float = 0.15  # US EXPLO commission (15%)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MusicSale(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    listing_id: str
    buyer_id: str
    seller_id: str
    sale_type: str  # purchase, license
    amount: float
    commission_amount: float
    seller_earnings: float
    stripe_payment_intent_id: Optional[str] = None
    status: str = "pending"  # pending, completed, refunded
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Community Groups Models
class CommunityGroup(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    group_type: str = "public"  # public, private, family, friends
    admin_id: str  # creator/admin user_id
    max_members: int = 50
    tags: List[str] = []
    group_image: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class GroupMember(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    group_id: str
    user_id: str
    role: str = "member"  # admin, moderator, member
    joined_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True

class GroupMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    group_id: str
    sender_id: str
    content: str
    message_type: str = "text"  # text, image, audio, file
    media_url: Optional[str] = None
    reply_to_message_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    edited_at: Optional[datetime] = None
    is_deleted: bool = False

# AI System Models
class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    user_id: str
    message_type: str = "user"  # user, assistant, system
    content: str
    metadata: Optional[Dict] = {}
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str = "Nouvelle conversation"
    context_data: Optional[Dict] = {}  # User context (subscription, preferences, etc.)
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AutomationTask(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    task_type: str  # recommendation, playlist_update, notification, analysis
    task_name: str
    description: str
    schedule: str = "daily"  # daily, weekly, monthly, on_demand
    is_active: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    config: Optional[Dict] = {}
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AIRecommendation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    recommendation_type: str  # track, artist, style, collaboration
    content: Dict  # The recommended content
    reason: str  # AI explanation for the recommendation
    confidence_score: float = 0.0
    is_viewed: bool = False
    is_liked: Optional[bool] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Song Creation Models
class SongCreation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    inspiration_phrase: str
    musical_style: str
    language: str = "français"
    mood: str = "énergique"
    tempo: str = "modéré"
    lyrics: str
    song_structure: Dict
    chord_suggestions: List[str] = []
    arrangement_notes: str = ""
    production_tips: str = ""
    ai_analysis: str = ""
    is_favorite: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SongCreationRequest(BaseModel):
    inspiration_phrase: str
    musical_style: str = "Afrobeat"
    language: str = "français"
    mood: str = "énergique"
    tempo: str = "modéré"
    song_title: Optional[str] = None

# Solidarity & Support Models
class MusicianCampaign(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str
    title: str
    description: str
    project_type: str = "album"  # album, concert, equipment, studio, emergency
    goal_amount: float
    current_amount: float = 0.0
    currency: str = "EUR"
    deadline: datetime
    story: str
    needs: List[str] = []  # What they need help with
    region: str = "International"
    music_style: str = "Divers"
    status: str = "active"  # active, completed, paused, cancelled
    featured: bool = False
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    updates: List[Dict] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Donation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    campaign_id: str
    donor_id: Optional[str] = None  # Anonymous if None
    donor_name: str = "Anonyme"
    amount: float
    currency: str = "EUR"
    message: Optional[str] = None
    is_anonymous: bool = False
    payment_status: str = "pending"  # pending, completed, failed
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SupportAdvice(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    advisor_id: str
    category: str  # physical, spiritual, creative, technical, business
    title: str
    content: str
    advice_type: str = "general"  # general, personal_response
    target_audience: str = "all"  # all, beginners, professionals, struggling
    tags: List[str] = []
    likes_count: int = 0
    is_featured: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SupportRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    requester_id: str
    category: str  # same as above
    title: str
    description: str
    urgency: str = "normal"  # low, normal, high, urgent
    status: str = "open"  # open, in_progress, resolved, closed
    responses: List[Dict] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Request Models for Solidarity
class CampaignCreateRequest(BaseModel):
    title: str
    description: str
    project_type: str = "album"
    goal_amount: float
    deadline_days: int = 30  # Days from now
    story: str
    needs: List[str] = []
    region: str = "International"
    music_style: str = "Divers"
    image_url: Optional[str] = None
    video_url: Optional[str] = None

class DonationCreateRequest(BaseModel):
    campaign_id: str
    amount: float
    donor_name: str = "Anonyme"
    message: Optional[str] = None
    is_anonymous: bool = False

class AdviceCreateRequest(BaseModel):
    category: str
    title: str
    content: str
    advice_type: str = "general"
    target_audience: str = "all"
    tags: List[str] = []

class SupportRequestCreate(BaseModel):
    category: str
    title: str
    description: str
    urgency: str = "normal"

# Request/Response Models for AI
class ChatMessageCreate(BaseModel):
    content: str
    session_id: Optional[str] = None

class ChatMessageResponse(BaseModel):
    message_id: str
    session_id: str
    content: str
    message_type: str
    created_at: datetime

class AutomationTaskCreate(BaseModel):
    task_type: str
    task_name: str
    description: str
    schedule: str = "daily"
    config: Optional[Dict] = {}

# Request/Response Models for new features
class SubscriptionCreateRequest(BaseModel):
    plan_id: str
    billing_cycle: str = "monthly"

class MusicListingCreate(BaseModel):
    track_id: str
    listing_type: str = "sale"
    sale_price: Optional[float] = None
    license_price: Optional[float] = None
    license_terms: Optional[str] = None
    royalty_percentage: float = 0.0
    is_exclusive: bool = False

class GroupCreate(BaseModel):
    name: str
    description: Optional[str] = None
    group_type: str = "public"
    max_members: int = 50
    tags: List[str] = []

class GroupMessageCreate(BaseModel):
    content: str
    message_type: str = "text"
    media_url: Optional[str] = None
    reply_to_message_id: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Music Track Models
class Track(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    artist: str
    user_id: Optional[str] = None  # Owner of the track
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
            elif isinstance(value, dict):
                # Recursively process nested dictionaries
                item[key] = prepare_from_mongo(value)
            elif isinstance(value, list):
                # Process lists that might contain dictionaries
                item[key] = [prepare_from_mongo(v) if isinstance(v, dict) else v for v in value]
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
            user_id=current_user.id,  # Set owner
            audio_url=audio_url,
            artwork_url=image_url,
            preview_url=preview_url or audio_url
        )
        
        await db.tracks.insert_one(prepare_for_mongo(track.dict()))
        return track
        
    except Exception as e:
        logger.error(f"Error creating track with files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create track: {str(e)}")

# Admin Routes for track management
@api_router.get("/admin/my-tracks")
async def get_my_tracks(current_user: User = Depends(get_current_user)):
    """Get tracks created by current user"""
    tracks = await db.tracks.find({
        "$or": [
            {"user_id": current_user.id},  # Tracks owned by user
            {"artist": current_user.username},  # Legacy tracks by username
            {"artist": {"$regex": "Simon Messela", "$options": "i"}},  # Legacy Simon Messela tracks
            {"artist": {"$regex": "fifi Ribana", "$options": "i"}}  # Legacy fifi Ribana tracks
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

# ===== MUSICIAN COMMUNITY ENDPOINTS =====

@api_router.post("/community/profile", response_model=MusicianProfile)
async def create_musician_profile(
    profile_data: MusicianProfileCreate, 
    current_user: User = Depends(get_current_user)
):
    """Create or update musician profile"""
    try:
        # Check if profile already exists
        existing_profile = await db.musician_profiles.find_one({"user_id": current_user.id})
        
        if existing_profile:
            # Update existing profile
            profile_dict = profile_data.dict()
            profile_dict["updated_at"] = datetime.now(timezone.utc)
            
            await db.musician_profiles.update_one(
                {"user_id": current_user.id},
                {"$set": profile_dict}
            )
            
            updated_profile = await db.musician_profiles.find_one({"user_id": current_user.id})
            return MusicianProfile(**prepare_from_mongo(updated_profile))
        else:
            # Create new profile
            profile = MusicianProfile(
                user_id=current_user.id,
                **profile_data.dict()
            )
            
            await db.musician_profiles.insert_one(prepare_for_mongo(profile.dict()))
            return profile
            
    except Exception as e:
        logger.error(f"Error creating musician profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create musician profile")

@api_router.get("/community/profile/me", response_model=MusicianProfile)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """Get current user's musician profile"""
    profile = await db.musician_profiles.find_one({"user_id": current_user.id})
    if not profile:
        raise HTTPException(status_code=404, detail="Musician profile not found")
    return MusicianProfile(**prepare_from_mongo(profile))

@api_router.get("/community/musicians")
async def search_musicians(
    region: Optional[str] = None,
    genre: Optional[str] = None,
    instrument: Optional[str] = None,
    experience_level: Optional[str] = None,
    looking_for: Optional[str] = None,
    limit: int = Query(20, le=100),
    skip: int = Query(0, ge=0)
):
    """Search musicians by criteria"""
    try:
        pipeline = []
        
        # Build match stage
        match_conditions = {"is_active": True}
        
        if region:
            match_conditions["region"] = {"$regex": region, "$options": "i"}
        if genre:
            match_conditions["genres"] = {"$in": [genre]}
        if instrument:
            match_conditions["instruments"] = {"$in": [instrument]}
        if experience_level:
            match_conditions["experience_level"] = experience_level
        if looking_for:
            match_conditions["looking_for"] = {"$in": [looking_for]}
            
        pipeline.append({"$match": match_conditions})
        
        # Add user info
        pipeline.extend([
            {
                "$lookup": {
                    "from": "users",
                    "localField": "user_id",
                    "foreignField": "id",
                    "as": "user_info"
                }
            },
            {"$unwind": "$user_info"},
            {
                "$project": {
                    "id": 1,
                    "stage_name": 1,
                    "bio": 1,
                    "instruments": 1,
                    "genres": 1,
                    "experience_level": 1,
                    "region": 1,
                    "city": 1,
                    "looking_for": 1,
                    "profile_image": 1,
                    "created_at": 1,
                    "username": "$user_info.username"
                }
            },
            {"$sort": {"created_at": -1}},
            {"$skip": skip},
            {"$limit": limit}
        ])
        
        musicians = await db.musician_profiles.aggregate(pipeline).to_list(limit)
        return [prepare_from_mongo(musician) for musician in musicians]
        
    except Exception as e:
        logger.error(f"Error searching musicians: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search musicians")

@api_router.post("/community/posts", response_model=CommunityPost)
async def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new community post"""
    try:
        post = CommunityPost(
            user_id=current_user.id,
            **post_data.dict()
        )
        
        await db.community_posts.insert_one(prepare_for_mongo(post.dict()))
        return post
        
    except Exception as e:
        logger.error(f"Error creating post: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create post")

@api_router.get("/community/posts")
async def get_community_feed(
    post_type: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = Query(20, le=100),
    skip: int = Query(0, ge=0)
):
    """Get community feed posts"""
    try:
        pipeline = []
        
        # Build match stage
        match_conditions = {"is_active": True}
        
        if post_type:
            match_conditions["post_type"] = post_type
        if tag:
            match_conditions["tags"] = {"$in": [tag]}
            
        pipeline.append({"$match": match_conditions})
        
        # Add user info
        pipeline.extend([
            {
                "$lookup": {
                    "from": "users",
                    "localField": "user_id",
                    "foreignField": "id",
                    "as": "user_info"
                }
            },
            {"$unwind": "$user_info"},
            {
                "$lookup": {
                    "from": "musician_profiles",
                    "localField": "user_id",
                    "foreignField": "user_id",
                    "as": "musician_info"
                }
            },
            {
                "$project": {
                    "id": 1,
                    "title": 1,
                    "content": 1,
                    "post_type": 1,
                    "tags": 1,
                    "media_urls": 1,
                    "likes_count": 1,
                    "comments_count": 1,
                    "created_at": 1,
                    "author": {
                        "username": "$user_info.username",
                        "stage_name": {"$arrayElemAt": ["$musician_info.stage_name", 0]},
                        "profile_image": {"$arrayElemAt": ["$musician_info.profile_image", 0]}
                    }
                }
            },
            {"$sort": {"created_at": -1}},
            {"$skip": skip},
            {"$limit": limit}
        ])
        
        posts = await db.community_posts.aggregate(pipeline).to_list(limit)
        return [prepare_from_mongo(post) for post in posts]
        
    except Exception as e:
        logger.error(f"Error getting community feed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get community feed")

@api_router.post("/community/posts/{post_id}/like")
async def like_post(
    post_id: str,
    current_user: User = Depends(get_current_user)
):
    """Like or unlike a post"""
    try:
        # Check if already liked
        existing_like = await db.post_likes.find_one({
            "post_id": post_id,
            "user_id": current_user.id
        })
        
        if existing_like:
            # Unlike
            await db.post_likes.delete_one({"id": existing_like["id"]})
            await db.community_posts.update_one(
                {"id": post_id},
                {"$inc": {"likes_count": -1}}
            )
            return {"message": "Post unliked", "liked": False}
        else:
            # Like
            like = PostLike(
                post_id=post_id,
                user_id=current_user.id
            )
            await db.post_likes.insert_one(prepare_for_mongo(like.dict()))
            await db.community_posts.update_one(
                {"id": post_id},
                {"$inc": {"likes_count": 1}}
            )
            return {"message": "Post liked", "liked": True}
            
    except Exception as e:
        logger.error(f"Error liking post: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to like post")

@api_router.post("/community/posts/{post_id}/comments", response_model=PostComment)
async def add_comment(
    post_id: str,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user)
):
    """Add comment to a post"""
    try:
        comment = PostComment(
            post_id=post_id,
            user_id=current_user.id,
            **comment_data.dict()
        )
        
        await db.post_comments.insert_one(prepare_for_mongo(comment.dict()))
        await db.community_posts.update_one(
            {"id": post_id},
            {"$inc": {"comments_count": 1}}
        )
        
        return comment
        
    except Exception as e:
        logger.error(f"Error adding comment: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add comment")

@api_router.get("/community/posts/{post_id}/comments")
async def get_post_comments(
    post_id: str,
    limit: int = Query(50, le=100),
    skip: int = Query(0, ge=0)
):
    """Get comments for a post"""
    try:
        pipeline = [
            {"$match": {"post_id": post_id}},
            {
                "$lookup": {
                    "from": "users",
                    "localField": "user_id",
                    "foreignField": "id",
                    "as": "user_info"
                }
            },
            {"$unwind": "$user_info"},
            {
                "$lookup": {
                    "from": "musician_profiles",
                    "localField": "user_id",
                    "foreignField": "user_id",
                    "as": "musician_info"
                }
            },
            {
                "$project": {
                    "id": 1,
                    "content": 1,
                    "created_at": 1,
                    "author": {
                        "username": "$user_info.username",
                        "stage_name": {"$arrayElemAt": ["$musician_info.stage_name", 0]},
                        "profile_image": {"$arrayElemAt": ["$musician_info.profile_image", 0]}
                    }
                }
            },
            {"$sort": {"created_at": 1}},
            {"$skip": skip},
            {"$limit": limit}
        ]
        
        comments = await db.post_comments.aggregate(pipeline).to_list(limit)
        return [prepare_from_mongo(comment) for comment in comments]
        
    except Exception as e:
        logger.error(f"Error getting comments: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get comments")

@api_router.post("/community/messages", response_model=MusicianMessage)
async def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user)
):
    """Send a private message to another musician"""
    try:
        message = MusicianMessage(
            sender_id=current_user.id,
            **message_data.dict()
        )
        
        await db.musician_messages.insert_one(prepare_for_mongo(message.dict()))
        return message
        
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send message")

@api_router.get("/community/messages")
async def get_my_messages(
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, le=100),
    skip: int = Query(0, ge=0)
):
    """Get user's private messages"""
    try:
        pipeline = [
            {
                "$match": {
                    "$or": [
                        {"sender_id": current_user.id},
                        {"recipient_id": current_user.id}
                    ]
                }
            },
            {
                "$lookup": {
                    "from": "users",
                    "localField": "sender_id",
                    "foreignField": "id",
                    "as": "sender_info"
                }
            },
            {
                "$lookup": {
                    "from": "users",
                    "localField": "recipient_id",
                    "foreignField": "id",
                    "as": "recipient_info"
                }
            },
            {"$unwind": "$sender_info"},
            {"$unwind": "$recipient_info"},
            {
                "$project": {
                    "id": 1,
                    "subject": 1,
                    "content": 1,
                    "is_read": 1,
                    "created_at": 1,
                    "sender": {
                        "id": "$sender_info.id",
                        "username": "$sender_info.username"
                    },
                    "recipient": {
                        "id": "$recipient_info.id",
                        "username": "$recipient_info.username"
                    }
                }
            },
            {"$sort": {"created_at": -1}},
            {"$skip": skip},
            {"$limit": limit}
        ]
        
        messages = await db.musician_messages.aggregate(pipeline).to_list(limit)
        return [prepare_from_mongo(message) for message in messages]
        
    except Exception as e:
        logger.error(f"Error getting messages: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get messages")

# ===== SUBSCRIPTION SYSTEM ENDPOINTS =====

@api_router.get("/subscriptions/plans")
async def get_subscription_plans():
    """Get all available subscription plans"""
    try:
        plans = await db.subscription_plans.find({"is_active": True}).to_list(100)
        return [prepare_from_mongo(plan) for plan in plans]
    except Exception as e:
        logger.error(f"Error getting subscription plans: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get subscription plans")

@api_router.post("/subscriptions/subscribe")
async def create_subscription(
    subscription_data: SubscriptionCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a new subscription for user"""
    try:
        # Check if plan exists
        plan = await db.subscription_plans.find_one({"id": subscription_data.plan_id, "is_active": True})
        if not plan:
            raise HTTPException(status_code=404, detail="Subscription plan not found")
        
        # Check if user already has an active subscription
        existing_sub = await db.user_subscriptions.find_one({
            "user_id": current_user.id,
            "status": "active"
        })
        
        if existing_sub:
            raise HTTPException(status_code=400, detail="User already has an active subscription")
        
        # Calculate period dates
        start_date = datetime.now(timezone.utc)
        if subscription_data.billing_cycle == "yearly":
            end_date = start_date.replace(year=start_date.year + 1)
        else:
            # Monthly billing
            if start_date.month == 12:
                end_date = start_date.replace(year=start_date.year + 1, month=1)
            else:
                end_date = start_date.replace(month=start_date.month + 1)
        
        # Create subscription
        subscription = UserSubscription(
            user_id=current_user.id,
            plan_id=subscription_data.plan_id,
            billing_cycle=subscription_data.billing_cycle,
            current_period_start=start_date,
            current_period_end=end_date
        )
        
        await db.user_subscriptions.insert_one(prepare_for_mongo(subscription.dict()))
        return subscription
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating subscription: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create subscription")

@api_router.get("/subscriptions/my-subscription")
async def get_user_subscription(current_user: User = Depends(get_current_user)):
    """Get current user's subscription details"""
    try:
        pipeline = [
            {"$match": {"user_id": current_user.id, "status": "active"}},
            {
                "$lookup": {
                    "from": "subscription_plans",
                    "localField": "plan_id",
                    "foreignField": "id",
                    "as": "plan_info"
                }
            },
            {"$unwind": "$plan_info"},
            {
                "$project": {
                    "id": 1,
                    "status": 1,
                    "billing_cycle": 1,
                    "current_period_start": 1,
                    "current_period_end": 1,
                    "created_at": 1,
                    "plan": "$plan_info"
                }
            }
        ]
        
        subscription_list = await db.user_subscriptions.aggregate(pipeline).to_list(1)
        if not subscription_list:
            return None
        
        return prepare_from_mongo(subscription_list[0])
        
    except Exception as e:
        logger.error(f"Error getting user subscription: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user subscription")

# ===== MUSIC MARKETPLACE ENDPOINTS =====

@api_router.post("/marketplace/list", response_model=MusicListing)
async def create_music_listing(
    listing_data: MusicListingCreate,
    current_user: User = Depends(get_current_user)
):
    """List music for sale/license in the marketplace"""
    try:
        # Verify user owns the track
        track = await db.tracks.find_one({
            "id": listing_data.track_id,
            "$or": [
                {"user_id": current_user.id},
                {"artist": current_user.username}  # Legacy compatibility
            ]
        })
        if not track:
            raise HTTPException(status_code=404, detail="Track not found or not owned by user")
        
        # Check if track is already listed
        existing_listing = await db.music_listings.find_one({
            "track_id": listing_data.track_id,
            "seller_id": current_user.id,
            "status": "active"
        })
        
        if existing_listing:
            raise HTTPException(status_code=400, detail="Track is already listed in marketplace")
        
        # Check user subscription for selling privileges
        user_subscription = await db.user_subscriptions.find_one({
            "user_id": current_user.id,
            "status": "active"
        })
        
        if user_subscription:
            plan = await db.subscription_plans.find_one({"id": user_subscription["plan_id"]})
            if not plan or not plan.get("can_sell_music", False):
                raise HTTPException(status_code=403, detail="Subscription plan does not allow selling music")
        else:
            raise HTTPException(status_code=403, detail="Active subscription required to sell music")
        
        # Create listing
        listing = MusicListing(
            seller_id=current_user.id,
            **listing_data.dict()
        )
        
        await db.music_listings.insert_one(prepare_for_mongo(listing.dict()))
        return listing
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating music listing: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create music listing")

@api_router.get("/marketplace/listings")
async def get_marketplace_listings(
    genre: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    listing_type: Optional[str] = None,
    limit: int = Query(20, le=100),
    skip: int = Query(0, ge=0)
):
    """Get marketplace listings with filters"""
    try:
        pipeline = []
        
        # Build match stage
        match_conditions = {"status": "active"}
        
        if listing_type:
            match_conditions["listing_type"] = {"$in": [listing_type, "both"]}
        
        pipeline.append({"$match": match_conditions})
        
        # Join with tracks and users
        pipeline.extend([
            {
                "$lookup": {
                    "from": "tracks",
                    "localField": "track_id",
                    "foreignField": "id",
                    "as": "track_info"
                }
            },
            {"$unwind": "$track_info"},
            {
                "$lookup": {
                    "from": "users",
                    "localField": "seller_id",
                    "foreignField": "id",
                    "as": "seller_info"
                }
            },
            {"$unwind": "$seller_info"},
            {
                "$lookup": {
                    "from": "musician_profiles",
                    "localField": "seller_id",
                    "foreignField": "user_id",
                    "as": "musician_info"
                }
            }
        ])
        
        # Add genre filter after joining with tracks
        additional_match = {}
        if genre:
            additional_match["track_info.style"] = {"$regex": genre, "$options": "i"}
        if price_min or price_max:
            price_conditions = {}
            if price_min:
                price_conditions["$gte"] = price_min
            if price_max:
                price_conditions["$lte"] = price_max
            
            price_or_conditions = []
            if not listing_type or listing_type == "sale" or listing_type == "both":
                price_or_conditions.append({"sale_price": price_conditions})
            if not listing_type or listing_type == "license" or listing_type == "both":
                price_or_conditions.append({"license_price": price_conditions})
                
            if price_or_conditions:
                additional_match["$or"] = price_or_conditions
        
        if additional_match:
            pipeline.append({"$match": additional_match})
        
        # Project final structure
        pipeline.extend([
            {
                "$project": {
                    "id": 1,
                    "listing_type": 1,
                    "sale_price": 1,
                    "license_price": 1,
                    "license_terms": 1,
                    "royalty_percentage": 1,
                    "is_exclusive": 1,
                    "created_at": 1,
                    "track": {
                        "id": "$track_info.id",
                        "title": "$track_info.title",
                        "style": "$track_info.style",
                        "region": "$track_info.region",
                        "duration": "$track_info.duration",
                        "artwork_url": "$track_info.artwork_url",
                        "preview_url": "$track_info.preview_url"
                    },
                    "seller": {
                        "username": "$seller_info.username",
                        "stage_name": {"$arrayElemAt": ["$musician_info.stage_name", 0]}
                    }
                }
            },
            {"$sort": {"created_at": -1}},
            {"$skip": skip},
            {"$limit": limit}
        ])
        
        listings = await db.music_listings.aggregate(pipeline).to_list(limit)
        return [prepare_from_mongo(listing) for listing in listings]
        
    except Exception as e:
        logger.error(f"Error getting marketplace listings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get marketplace listings")

@api_router.get("/marketplace/my-listings")
async def get_my_listings(
    current_user: User = Depends(get_current_user),
    limit: int = Query(20, le=100),
    skip: int = Query(0, ge=0)
):
    """Get current user's marketplace listings"""
    try:
        pipeline = [
            {"$match": {"seller_id": current_user.id}},
            {
                "$lookup": {
                    "from": "tracks",
                    "localField": "track_id",
                    "foreignField": "id",
                    "as": "track_info"
                }
            },
            {"$unwind": "$track_info"},
            {
                "$project": {
                    "id": 1,
                    "listing_type": 1,
                    "sale_price": 1,
                    "license_price": 1,
                    "status": 1,
                    "created_at": 1,
                    "track": {
                        "id": "$track_info.id",
                        "title": "$track_info.title",
                        "style": "$track_info.style",
                        "artwork_url": "$track_info.artwork_url"
                    }
                }
            },
            {"$sort": {"created_at": -1}},
            {"$skip": skip},
            {"$limit": limit}
        ]
        
        listings = await db.music_listings.aggregate(pipeline).to_list(limit)
        return [prepare_from_mongo(listing) for listing in listings]
        
    except Exception as e:
        logger.error(f"Error getting user listings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user listings")

# ===== COMMUNITY GROUPS ENDPOINTS =====

@api_router.post("/community/groups", response_model=CommunityGroup)
async def create_group(
    group_data: GroupCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new community group"""
    try:
        # Check user subscription for group creation limits
        user_subscription = await db.user_subscriptions.find_one({
            "user_id": current_user.id,
            "status": "active"
        })
        
        if user_subscription:
            plan = await db.subscription_plans.find_one({"id": user_subscription["plan_id"]})
            if plan:
                # Check how many groups user has created
                user_groups_count = await db.community_groups.count_documents({
                    "admin_id": current_user.id,
                    "is_active": True
                })
                
                if user_groups_count >= plan.get("max_groups", 3):
                    raise HTTPException(
                        status_code=403, 
                        detail=f"Maximum group limit reached for your plan ({plan.get('max_groups', 3)} groups)"
                    )
        else:
            # Free users can create 1 group
            user_groups_count = await db.community_groups.count_documents({
                "admin_id": current_user.id,
                "is_active": True
            })
            
            if user_groups_count >= 1:
                raise HTTPException(status_code=403, detail="Free users can only create 1 group. Upgrade to create more.")
        
        # Create group
        group = CommunityGroup(
            admin_id=current_user.id,
            **group_data.dict()
        )
        
        await db.community_groups.insert_one(prepare_for_mongo(group.dict()))
        
        # Add creator as first member with admin role
        admin_member = GroupMember(
            group_id=group.id,
            user_id=current_user.id,
            role="admin"
        )
        
        await db.group_members.insert_one(prepare_for_mongo(admin_member.dict()))
        
        return group
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating group: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create group")

@api_router.get("/community/groups")
async def get_groups(
    group_type: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(20, le=100),
    skip: int = Query(0, ge=0)
):
    """Get community groups with filters"""
    try:
        pipeline = []
        
        # Build match stage
        match_conditions = {"is_active": True}
        
        if group_type and group_type != "all":
            match_conditions["group_type"] = group_type
        
        if search:
            match_conditions["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
                {"tags": {"$in": [search]}}
            ]
        
        pipeline.append({"$match": match_conditions})
        
        # Add admin info and member count
        pipeline.extend([
            {
                "$lookup": {
                    "from": "users",
                    "localField": "admin_id",
                    "foreignField": "id",
                    "as": "admin_info"
                }
            },
            {"$unwind": "$admin_info"},
            {
                "$lookup": {
                    "from": "group_members",
                    "localField": "id",
                    "foreignField": "group_id",
                    "as": "members"
                }
            },
            {
                "$addFields": {
                    "member_count": {"$size": "$members"}
                }
            },
            {
                "$project": {
                    "id": 1,
                    "name": 1,
                    "description": 1,
                    "group_type": 1,
                    "max_members": 1,
                    "tags": 1,
                    "group_image": 1,
                    "created_at": 1,
                    "member_count": 1,
                    "admin": {
                        "username": "$admin_info.username"
                    }
                }
            },
            {"$sort": {"created_at": -1}},
            {"$skip": skip},
            {"$limit": limit}
        ])
        
        groups = await db.community_groups.aggregate(pipeline).to_list(limit)
        return [prepare_from_mongo(group) for group in groups]
        
    except Exception as e:
        logger.error(f"Error getting groups: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get groups")

@api_router.post("/community/groups/{group_id}/join")
async def join_group(
    group_id: str,
    current_user: User = Depends(get_current_user)
):
    """Join a community group"""
    try:
        # Check if group exists
        group = await db.community_groups.find_one({"id": group_id, "is_active": True})
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        # Check if already a member
        existing_member = await db.group_members.find_one({
            "group_id": group_id,
            "user_id": current_user.id,
            "is_active": True
        })
        
        if existing_member:
            return {"message": "Already a member of this group", "member": True}
        
        # Check if group is full
        member_count = await db.group_members.count_documents({
            "group_id": group_id,
            "is_active": True
        })
        
        if member_count >= group["max_members"]:
            raise HTTPException(status_code=400, detail="Group is full")
        
        # Add as member
        member = GroupMember(
            group_id=group_id,
            user_id=current_user.id
        )
        
        await db.group_members.insert_one(prepare_for_mongo(member.dict()))
        
        return {"message": "Successfully joined the group", "member": True}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error joining group: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to join group")

@api_router.get("/community/groups/{group_id}/messages")
async def get_group_messages(
    group_id: str,
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, le=100),
    skip: int = Query(0, ge=0)
):
    """Get messages from a group (if user is a member)"""
    try:
        # Verify user is a member of the group
        member = await db.group_members.find_one({
            "group_id": group_id,
            "user_id": current_user.id,
            "is_active": True
        })
        
        if not member:
            raise HTTPException(status_code=403, detail="You must be a member to view group messages")
        
        # Get messages with sender info
        pipeline = [
            {"$match": {"group_id": group_id, "is_deleted": False}},
            {
                "$lookup": {
                    "from": "users",
                    "localField": "sender_id",
                    "foreignField": "id",
                    "as": "sender_info"
                }
            },
            {"$unwind": "$sender_info"},
            {
                "$lookup": {
                    "from": "musician_profiles",
                    "localField": "sender_id",
                    "foreignField": "user_id",
                    "as": "musician_info"
                }
            },
            {
                "$project": {
                    "id": 1,
                    "content": 1,
                    "message_type": 1,
                    "media_url": 1,
                    "reply_to_message_id": 1,
                    "created_at": 1,
                    "edited_at": 1,
                    "sender": {
                        "id": "$sender_info.id",
                        "username": "$sender_info.username",
                        "stage_name": {"$arrayElemAt": ["$musician_info.stage_name", 0]}
                    }
                }
            },
            {"$sort": {"created_at": -1}},
            {"$skip": skip},
            {"$limit": limit}
        ]
        
        messages = await db.group_messages.aggregate(pipeline).to_list(limit)
        return [prepare_from_mongo(message) for message in messages]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting group messages: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get group messages")

@api_router.post("/community/groups/{group_id}/messages")
async def send_group_message(
    group_id: str,
    message_data: GroupMessageCreate,
    current_user: User = Depends(get_current_user)
):
    """Send a message to a group"""
    try:
        # Verify user is a member of the group
        member = await db.group_members.find_one({
            "group_id": group_id,
            "user_id": current_user.id,
            "is_active": True
        })
        
        if not member:
            raise HTTPException(status_code=403, detail="You must be a member to send messages")
        
        # Create message
        message = GroupMessage(
            group_id=group_id,
            sender_id=current_user.id,
            **message_data.dict()
        )
        
        await db.group_messages.insert_one(prepare_for_mongo(message.dict()))
        
        return {"message": "Message sent successfully", "id": message.id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending group message: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send group message")

# ===== AI SYSTEM ENDPOINTS =====

# Initialize AI with environment variables
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')

async def get_user_context(user_id: str) -> Dict:
    """Get user context for AI conversations"""
    try:
        # Get user info
        user = await db.users.find_one({"id": user_id})
        if not user:
            return {}
        
        # Get subscription info
        subscription = await db.user_subscriptions.find_one({
            "user_id": user_id,
            "status": "active"
        })
        
        # Get musician profile
        musician_profile = await db.musician_profiles.find_one({"user_id": user_id})
        
        # Get recent activity (tracks liked, purchased, etc.)
        recent_likes = await db.post_likes.find({"user_id": user_id}).limit(10).to_list(10)
        recent_purchases = await db.payment_transactions.find({
            "user_email": user.get("email"),
            "payment_status": "completed"
        }).limit(5).to_list(5)
        
        context = {
            "user": {
                "username": user.get("username"),
                "email": user.get("email"),
                "preferences": user.get("preferences", []),
                "favorite_regions": user.get("favorite_regions", [])
            },
            "subscription": subscription,
            "musician_profile": musician_profile,
            "activity": {
                "recent_likes_count": len(recent_likes),
                "recent_purchases_count": len(recent_purchases)
            }
        }
        
        return context
        
    except Exception as e:
        logger.error(f"Error getting user context: {str(e)}")
        return {}

@api_router.post("/ai/chat", response_model=ChatMessageResponse)
async def chat_with_ai(
    message_data: ChatMessageCreate,
    current_user: User = Depends(get_current_user)
):
    """Chat with AI assistant"""
    try:
        # Get or create session
        session_id = message_data.session_id
        if not session_id:
            # Create new session
            session = ChatSession(
                user_id=current_user.id,
                title=f"Chat - {datetime.now().strftime('%d/%m %H:%M')}"
            )
            await db.chat_sessions.insert_one(prepare_for_mongo(session.dict()))
            session_id = session.id
        else:
            # Verify session belongs to user
            session = await db.chat_sessions.find_one({
                "id": session_id,
                "user_id": current_user.id
            })
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
        
        # Get user context for personalized responses
        user_context = await get_user_context(current_user.id)
        
        # Create system message with context
        system_message = f"""Tu es l'assistant IA de US EXPLO (Universal Sound Exploration), une plateforme de musique mondiale moderne.

CONTEXTE UTILISATEUR:
- Nom d'utilisateur: {user_context.get('user', {}).get('username', 'Inconnu')}
- Abonnement: {'Actif' if user_context.get('subscription') else 'Aucun'}
- Profil musicien: {'Oui' if user_context.get('musician_profile') else 'Non'}

TES MISSIONS:
1. Aider avec les fonctionnalités de US EXPLO (recherche musique, abonnements, communauté, marketplace)
2. Recommander de la musique basée sur les préférences utilisateur  
3. Expliquer comment utiliser la plateforme
4. Aider avec les problèmes techniques simples
5. Promouvoir la découverte musicale mondiale

STYLE DE RÉPONSE:
- Toujours en français
- Ton amical et professionnel
- Émojis musicaux appropriés (🎵, 🌍, 🎶)
- Réponses concises mais complètes
- Encourager l'exploration musicale mondiale

Si tu ne peux pas aider avec quelque chose, oriente vers le support technique."""

        # Initialize LLM chat
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=session_id,
            system_message=system_message
        ).with_model("openai", "gpt-4o")
        
        # Save user message
        user_message = ChatMessage(
            session_id=session_id,
            user_id=current_user.id,
            message_type="user",
            content=message_data.content
        )
        await db.chat_messages.insert_one(prepare_for_mongo(user_message.dict()))
        
        # Send message to AI
        user_msg = UserMessage(text=message_data.content)
        ai_response = await chat.send_message(user_msg)
        
        # Save AI response
        ai_message = ChatMessage(
            session_id=session_id,
            user_id=current_user.id,
            message_type="assistant",
            content=ai_response,
            metadata={"model": "gpt-4o"}
        )
        await db.chat_messages.insert_one(prepare_for_mongo(ai_message.dict()))
        
        # Update session
        await db.chat_sessions.update_one(
            {"id": session_id},
            {"$set": {"updated_at": datetime.now(timezone.utc)}}
        )
        
        return ChatMessageResponse(
            message_id=ai_message.id,
            session_id=session_id,
            content=ai_response,
            message_type="assistant",
            created_at=ai_message.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in AI chat: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process AI chat")

@api_router.get("/ai/sessions")
async def get_chat_sessions(
    current_user: User = Depends(get_current_user),
    limit: int = Query(20, le=100)
):
    """Get user's chat sessions"""
    try:
        sessions = await db.chat_sessions.find({
            "user_id": current_user.id,
            "is_active": True
        }).sort("updated_at", -1).limit(limit).to_list(limit)
        
        return [prepare_from_mongo(session) for session in sessions]
        
    except Exception as e:
        logger.error(f"Error getting chat sessions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get chat sessions")

@api_router.get("/ai/sessions/{session_id}/messages")
async def get_chat_messages(
    session_id: str,
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, le=100)
):
    """Get messages from a chat session"""
    try:
        # Verify session belongs to user
        session = await db.chat_sessions.find_one({
            "id": session_id,
            "user_id": current_user.id
        })
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        messages = await db.chat_messages.find({
            "session_id": session_id
        }).sort("created_at", 1).limit(limit).to_list(limit)
        
        return [prepare_from_mongo(message) for message in messages]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat messages: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get chat messages")

@api_router.delete("/ai/sessions/{session_id}")
async def delete_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a chat session"""
    try:
        # Verify session belongs to user
        session = await db.chat_sessions.find_one({
            "id": session_id,
            "user_id": current_user.id
        })
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Soft delete session
        await db.chat_sessions.update_one(
            {"id": session_id},
            {"$set": {"is_active": False}}
        )
        
        return {"message": "Session deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting chat session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete session")

# ===== AI AUTOMATION ENDPOINTS =====

@api_router.post("/ai/automation/tasks", response_model=AutomationTask)
async def create_automation_task(
    task_data: AutomationTaskCreate,
    current_user: User = Depends(get_current_user)
):
    """Create an AI automation task"""
    try:
        task = AutomationTask(
            user_id=current_user.id,
            **task_data.dict()
        )
        
        await db.automation_tasks.insert_one(prepare_for_mongo(task.dict()))
        return task
        
    except Exception as e:
        logger.error(f"Error creating automation task: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create automation task")

@api_router.get("/ai/automation/tasks")
async def get_automation_tasks(
    current_user: User = Depends(get_current_user)
):
    """Get user's automation tasks"""
    try:
        tasks = await db.automation_tasks.find({
            "user_id": current_user.id
        }).sort("created_at", -1).to_list(100)
        
        return [prepare_from_mongo(task) for task in tasks]
        
    except Exception as e:
        logger.error(f"Error getting automation tasks: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get automation tasks")

@api_router.put("/ai/automation/tasks/{task_id}/toggle")
async def toggle_automation_task(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """Toggle automation task active status"""
    try:
        task = await db.automation_tasks.find_one({
            "id": task_id,
            "user_id": current_user.id
        })
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        new_status = not task["is_active"]
        await db.automation_tasks.update_one(
            {"id": task_id},
            {"$set": {"is_active": new_status, "updated_at": datetime.now(timezone.utc)}}
        )
        
        return {"message": f"Task {'activated' if new_status else 'deactivated'} successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling automation task: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to toggle task")

@api_router.post("/ai/recommendations/generate")
async def generate_ai_recommendations(
    current_user: User = Depends(get_current_user)
):
    """Generate AI recommendations for user"""
    try:
        # Get user context
        user_context = await get_user_context(current_user.id)
        
        # Get user's listening history/preferences
        user_preferences = user_context.get('user', {}).get('preferences', [])
        favorite_regions = user_context.get('user', {}).get('favorite_regions', [])
        
        # Get some tracks for recommendations
        query = {}
        if favorite_regions:
            query["region"] = {"$in": favorite_regions}
        
        tracks = await db.tracks.find(query).limit(10).to_list(10)
        
        if not tracks:
            tracks = await db.tracks.find({}).limit(10).to_list(10)
        
        # Generate AI recommendations using LLM
        system_message = """Tu es un expert en recommandation musicale mondiale. 
        Analyse les préférences utilisateur et recommande des pistes musicales pertinentes avec des explications courtes et engageantes."""
        
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"recommendations_{current_user.id}",
            system_message=system_message
        ).with_model("openai", "gpt-4o")
        
        prompt = f"""Utilisateur: {user_context.get('user', {}).get('username')}
        Préférences: {', '.join(user_preferences) if user_preferences else 'Aucune spécifiée'}
        Régions favorites: {', '.join(favorite_regions) if favorite_regions else 'Toutes'}
        
        Parmi ces pistes disponibles, recommande les 3 meilleures avec une raison courte pour chacune:
        {[{'titre': t['title'], 'artiste': t['artist'], 'style': t['style'], 'région': t['region']} for t in tracks[:5]]}
        
        Format: Pour chaque recommandation, donne juste le titre et une phrase d'explication engageante."""
        
        user_msg = UserMessage(text=prompt)
        ai_response = await chat.send_message(user_msg)
        
        # Create recommendations (simplified for MVP)
        recommendations = []
        for i, track in enumerate(tracks[:3]):
            recommendation = AIRecommendation(
                user_id=current_user.id,
                recommendation_type="track",
                content={
                    "track_id": track["id"],
                    "title": track["title"],
                    "artist": track["artist"],
                    "style": track["style"],
                    "region": track["region"]
                },
                reason=f"Recommandé pour votre goût musical - {track['style']} de {track['region']}",
                confidence_score=0.8 + (i * 0.1)
            )
            await db.ai_recommendations.insert_one(prepare_for_mongo(recommendation.dict()))
            recommendations.append(recommendation)
        
        return {
            "message": "Recommendations generated successfully",
            "ai_analysis": ai_response,
            "recommendations": [prepare_from_mongo(r.dict()) for r in recommendations]
        }
        
    except Exception as e:
        logger.error(f"Error generating AI recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate recommendations")

@api_router.get("/ai/recommendations")
async def get_ai_recommendations(
    current_user: User = Depends(get_current_user),
    limit: int = Query(20, le=100)
):
    """Get user's AI recommendations"""
    try:
        recommendations = await db.ai_recommendations.find({
            "user_id": current_user.id
        }).sort("created_at", -1).limit(limit).to_list(limit)
        
        return [prepare_from_mongo(rec) for rec in recommendations]
        
    except Exception as e:
        logger.error(f"Error getting AI recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get recommendations")

# ===== AI SONG CREATION ENDPOINTS =====

@api_router.post("/ai/songs/create", response_model=SongCreation)
async def create_song_with_ai(
    song_request: SongCreationRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a complete song from inspiration phrase using AI"""
    try:
        # Create AI prompt for song generation
        system_message = f"""Tu es un compositeur et parolier expert spécialisé dans la musique mondiale, particulièrement la musique africaine.

MISSION: Créer une chanson complète à partir d'une phrase d'inspiration.

STYLE MUSICAL: {song_request.musical_style}
LANGUE: {song_request.language}
HUMEUR: {song_request.mood}
TEMPO: {song_request.tempo}

CONSIGNES IMPORTANTES:
1. Utilise la phrase d'inspiration comme thème central
2. Crée des paroles authentiques dans le style demandé
3. Propose une structure claire (Intro, Couplet, Refrain, Pont, Outro)
4. Suggère des accords appropriés au style
5. Donne des conseils d'arrangement et production
6. Respecte la culture musicale du style choisi

FORMAT DE RÉPONSE:
```
TITRE: [Titre créatif]

PAROLES:
[Intro]
[Paroles d'intro]

[Couplet 1]
[Paroles couplet 1]

[Refrain]
[Paroles refrain]

[Couplet 2]
[Paroles couplet 2]

[Refrain]
[Paroles refrain]

[Pont]
[Paroles pont]

[Refrain Final]
[Paroles refrain final]

[Outro]
[Paroles outro]

STRUCTURE: Intro - Couplet - Refrain - Couplet - Refrain - Pont - Refrain - Outro

ACCORDS SUGGÉRÉS: [Progression d'accords]

ARRANGEMENT: [Suggestions d'instruments et arrangements]

PRODUCTION: [Conseils de production et enregistrement]
```

Crée une chanson originale et inspirante !"""

        # Initialize LLM chat for song creation
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"song_creation_{current_user.id}_{int(time.time())}",
            system_message=system_message
        ).with_model("openai", "gpt-4o")
        
        # Create the prompt
        user_prompt = f"""Phrase d'inspiration: "{song_request.inspiration_phrase}"

Crée une chanson complète en {song_request.language} dans le style {song_request.musical_style}, avec une humeur {song_request.mood} et un tempo {song_request.tempo}.

La chanson doit être authentique, émotionnelle et refléter l'esprit de {song_request.musical_style}."""

        # Send message to AI
        user_msg = UserMessage(text=user_prompt)
        ai_response = await chat.send_message(user_msg)
        
        # Parse AI response to extract components
        response_parts = ai_response.split('\n\n')
        
        # Extract title
        title = song_request.song_title or "Chanson Générée"
        for part in response_parts:
            if part.startswith('TITRE:'):
                title = part.replace('TITRE:', '').strip()
                break
        
        # Extract lyrics (everything between PAROLES: and STRUCTURE:)
        lyrics = ""
        structure_info = ""
        chord_suggestions = []
        arrangement_notes = ""
        production_tips = ""
        
        # Parse the response more intelligently
        lines = ai_response.split('\n')
        current_section = ""
        
        for line in lines:
            line = line.strip()
            if line.startswith('TITRE:'):
                title = line.replace('TITRE:', '').strip()
            elif line.startswith('PAROLES:'):
                current_section = "lyrics"
            elif line.startswith('STRUCTURE:'):
                current_section = "structure"
            elif line.startswith('ACCORDS SUGGÉRÉS:'):
                current_section = "chords"
            elif line.startswith('ARRANGEMENT:'):
                current_section = "arrangement"
            elif line.startswith('PRODUCTION:'):
                current_section = "production"
            elif line and current_section == "lyrics":
                lyrics += line + "\n"
            elif line and current_section == "structure":
                structure_info += line + " "
            elif line and current_section == "chords":
                if line:
                    chord_suggestions.append(line)
            elif line and current_section == "arrangement":
                arrangement_notes += line + " "
            elif line and current_section == "production":
                production_tips += line + " "
        
        # Create song structure dictionary
        song_structure = {
            "structure": structure_info.strip(),
            "sections": ["Intro", "Couplet", "Refrain", "Pont", "Outro"],
            "estimated_duration": "3-4 minutes",
            "key_signature": "À déterminer selon les accords suggérés"
        }
        
        # Create the song creation record
        song_creation = SongCreation(
            user_id=current_user.id,
            title=title,
            inspiration_phrase=song_request.inspiration_phrase,
            musical_style=song_request.musical_style,
            language=song_request.language,
            mood=song_request.mood,
            tempo=song_request.tempo,
            lyrics=lyrics.strip(),
            song_structure=song_structure,
            chord_suggestions=chord_suggestions,
            arrangement_notes=arrangement_notes.strip(),
            production_tips=production_tips.strip(),
            ai_analysis=f"Chanson générée dans le style {song_request.musical_style} avec GPT-4o"
        )
        
        # Save to database
        await db.song_creations.insert_one(prepare_for_mongo(song_creation.dict()))
        
        return song_creation
        
    except Exception as e:
        logger.error(f"Error creating song with AI: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create song with AI")

@api_router.get("/ai/songs/my-creations")
async def get_my_song_creations(
    current_user: User = Depends(get_current_user),
    limit: int = Query(20, le=100)
):
    """Get user's song creations"""
    try:
        songs = await db.song_creations.find({
            "user_id": current_user.id
        }).sort("created_at", -1).limit(limit).to_list(limit)
        
        return [prepare_from_mongo(song) for song in songs]
        
    except Exception as e:
        logger.error(f"Error getting song creations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get song creations")

@api_router.get("/ai/songs/{song_id}")
async def get_song_creation(
    song_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific song creation"""
    try:
        song = await db.song_creations.find_one({
            "id": song_id,
            "user_id": current_user.id
        })
        
        if not song:
            raise HTTPException(status_code=404, detail="Song not found")
        
        return prepare_from_mongo(song)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting song creation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get song creation")

@api_router.put("/ai/songs/{song_id}/favorite")
async def toggle_song_favorite(
    song_id: str,
    current_user: User = Depends(get_current_user)
):
    """Toggle favorite status of a song creation"""
    try:
        song = await db.song_creations.find_one({
            "id": song_id,
            "user_id": current_user.id
        })
        
        if not song:
            raise HTTPException(status_code=404, detail="Song not found")
        
        new_favorite_status = not song.get("is_favorite", False)
        
        await db.song_creations.update_one(
            {"id": song_id},
            {
                "$set": {
                    "is_favorite": new_favorite_status,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        return {"message": f"Song {'added to' if new_favorite_status else 'removed from'} favorites"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling song favorite: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to toggle favorite")

@api_router.delete("/ai/songs/{song_id}")
async def delete_song_creation(
    song_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a song creation"""
    try:
        result = await db.song_creations.delete_one({
            "id": song_id,
            "user_id": current_user.id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Song not found")
        
        return {"message": "Song deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting song creation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete song")

# ===== SOLIDARITY & SUPPORT ENDPOINTS =====

@api_router.post("/solidarity/campaigns", response_model=MusicianCampaign)
async def create_campaign(
    campaign_data: CampaignCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a new musician support campaign"""
    try:
        # Calculate deadline
        deadline = datetime.now(timezone.utc) + timedelta(days=campaign_data.deadline_days)
        
        campaign = MusicianCampaign(
            creator_id=current_user.id,
            title=campaign_data.title,
            description=campaign_data.description,
            project_type=campaign_data.project_type,
            goal_amount=campaign_data.goal_amount,
            deadline=deadline,
            story=campaign_data.story,
            needs=campaign_data.needs,
            region=campaign_data.region,
            music_style=campaign_data.music_style,
            image_url=campaign_data.image_url,
            video_url=campaign_data.video_url
        )
        
        await db.musician_campaigns.insert_one(prepare_for_mongo(campaign.dict()))
        return campaign
        
    except Exception as e:
        logger.error(f"Error creating campaign: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create campaign")

@api_router.get("/solidarity/campaigns")
async def get_campaigns(
    status: str = Query("active"),
    limit: int = Query(20, le=100),
    featured: bool = Query(False),
    project_type: Optional[str] = Query(None),
    region: Optional[str] = Query(None)
):
    """Get musician campaigns with filters"""
    try:
        filter_query = {"status": status}
        
        if featured:
            filter_query["featured"] = True
        if project_type:
            filter_query["project_type"] = project_type
        if region and region != "all":
            filter_query["region"] = region
            
        campaigns = await db.musician_campaigns.find(filter_query).sort("created_at", -1).limit(limit).to_list(limit)
        
        # Add donation stats for each campaign
        for campaign in campaigns:
            donations = await db.donations.find({
                "campaign_id": campaign["id"],
                "payment_status": "completed"
            }).to_list(1000)
            
            total_amount = sum(d.get("amount", 0) for d in donations)
            campaign["current_amount"] = total_amount
            campaign["donors_count"] = len(donations)
            campaign["progress_percentage"] = min(100, (total_amount / campaign["goal_amount"]) * 100) if campaign["goal_amount"] > 0 else 0
        
        return [prepare_from_mongo(campaign) for campaign in campaigns]
        
    except Exception as e:
        logger.error(f"Error getting campaigns: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get campaigns")

@api_router.get("/solidarity/campaigns/{campaign_id}")
async def get_campaign_details(campaign_id: str):
    """Get detailed campaign information"""
    try:
        campaign = await db.musician_campaigns.find_one({"id": campaign_id})
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Get donations for this campaign
        donations = await db.donations.find({
            "campaign_id": campaign_id,
            "payment_status": "completed"
        }).sort("created_at", -1).to_list(100)
        
        # Calculate stats
        total_amount = sum(d.get("amount", 0) for d in donations)
        campaign["current_amount"] = total_amount
        campaign["donors_count"] = len(donations)
        campaign["progress_percentage"] = min(100, (total_amount / campaign["goal_amount"]) * 100) if campaign["goal_amount"] > 0 else 0
        
        # Get recent donations (non-anonymous)
        recent_donations = [
            {
                "donor_name": d.get("donor_name", "Anonyme"),
                "amount": d.get("amount", 0),
                "message": d.get("message"),
                "created_at": d.get("created_at")
            }
            for d in donations[:10] if not d.get("is_anonymous", False)
        ]
        
        campaign["recent_donations"] = recent_donations
        
        return prepare_from_mongo(campaign)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting campaign details: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get campaign details")

@api_router.post("/solidarity/donate")
async def make_donation(
    donation_data: DonationCreateRequest,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Make a donation to a campaign"""
    try:
        # Verify campaign exists
        campaign = await db.musician_campaigns.find_one({"id": donation_data.campaign_id})
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        if campaign["status"] != "active":
            raise HTTPException(status_code=400, detail="Campaign is not active")
        
        # Create donation record
        donation = Donation(
            campaign_id=donation_data.campaign_id,
            donor_id=current_user.id if current_user else None,
            donor_name=donation_data.donor_name,
            amount=donation_data.amount,
            message=donation_data.message,
            is_anonymous=donation_data.is_anonymous,
            payment_status="completed"  # Simplified for MVP - in production integrate with payment gateway
        )
        
        await db.donations.insert_one(prepare_for_mongo(donation.dict()))
        
        # Update campaign current amount
        total_donations = await db.donations.find({
            "campaign_id": donation_data.campaign_id,
            "payment_status": "completed"
        }).to_list(1000)
        
        new_total = sum(d.get("amount", 0) for d in total_donations)
        
        await db.musician_campaigns.update_one(
            {"id": donation_data.campaign_id},
            {
                "$set": {
                    "current_amount": new_total,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        return {"message": "Donation successful", "donation_id": donation.id, "new_total": new_total}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error making donation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process donation")

@api_router.get("/solidarity/my-campaigns")
async def get_my_campaigns(
    current_user: User = Depends(get_current_user)
):
    """Get current user's campaigns"""
    try:
        campaigns = await db.musician_campaigns.find({
            "creator_id": current_user.id
        }).sort("created_at", -1).to_list(100)
        
        # Add stats for each campaign
        for campaign in campaigns:
            donations = await db.donations.find({
                "campaign_id": campaign["id"],
                "payment_status": "completed"
            }).to_list(1000)
            
            total_amount = sum(d.get("amount", 0) for d in donations)
            campaign["current_amount"] = total_amount
            campaign["donors_count"] = len(donations)
        
        return [prepare_from_mongo(campaign) for campaign in campaigns]
        
    except Exception as e:
        logger.error(f"Error getting user campaigns: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get campaigns")

# ===== SUPPORT & ADVICE ENDPOINTS =====

@api_router.post("/solidarity/advice", response_model=SupportAdvice)
async def create_advice(
    advice_data: AdviceCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a support advice post"""
    try:
        advice = SupportAdvice(
            advisor_id=current_user.id,
            category=advice_data.category,
            title=advice_data.title,
            content=advice_data.content,
            advice_type=advice_data.advice_type,
            target_audience=advice_data.target_audience,
            tags=advice_data.tags
        )
        
        await db.support_advice.insert_one(prepare_for_mongo(advice.dict()))
        return advice
        
    except Exception as e:
        logger.error(f"Error creating advice: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create advice")

@api_router.get("/solidarity/advice")
async def get_advice(
    category: Optional[str] = Query(None),
    target_audience: str = Query("all"),
    featured: bool = Query(False),
    limit: int = Query(20, le=100)
):
    """Get support advice with filters"""
    try:
        filter_query = {}
        
        if category:
            filter_query["category"] = category
        if target_audience != "all":
            filter_query["target_audience"] = {"$in": [target_audience, "all"]}
        if featured:
            filter_query["is_featured"] = True
            
        advice_list = await db.support_advice.find(filter_query).sort("created_at", -1).limit(limit).to_list(limit)
        
        # Add advisor info
        for advice in advice_list:
            advisor = await db.users.find_one({"id": advice["advisor_id"]})
            if advisor:
                advice["advisor_name"] = advisor.get("username", "Anonyme")
            else:
                advice["advisor_name"] = "Anonyme"
        
        return [prepare_from_mongo(advice) for advice in advice_list]
        
    except Exception as e:
        logger.error(f"Error getting advice: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get advice")

@api_router.post("/solidarity/support-request", response_model=SupportRequest)
async def create_support_request(
    request_data: SupportRequestCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a support request"""
    try:
        support_request = SupportRequest(
            requester_id=current_user.id,
            category=request_data.category,
            title=request_data.title,
            description=request_data.description,
            urgency=request_data.urgency
        )
        
        await db.support_requests.insert_one(prepare_for_mongo(support_request.dict()))
        return support_request
        
    except Exception as e:
        logger.error(f"Error creating support request: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create support request")

@api_router.get("/solidarity/support-requests")
async def get_support_requests(
    category: Optional[str] = Query(None),
    status: str = Query("open"),
    urgency: Optional[str] = Query(None),
    limit: int = Query(20, le=100)
):
    """Get support requests with filters"""
    try:
        filter_query = {"status": status}
        
        if category:
            filter_query["category"] = category
        if urgency:
            filter_query["urgency"] = urgency
            
        requests = await db.support_requests.find(filter_query).sort("created_at", -1).limit(limit).to_list(limit)
        
        # Add requester info (anonymized)
        for request in requests:
            requester = await db.users.find_one({"id": request["requester_id"]})
            if requester:
                request["requester_name"] = requester.get("username", "Anonyme")
            else:
                request["requester_name"] = "Anonyme"
        
        return [prepare_from_mongo(request) for request in requests]
        
    except Exception as e:
        logger.error(f"Error getting support requests: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get support requests")

@api_router.get("/solidarity/stats")
async def get_solidarity_stats():
    """Get global solidarity statistics"""
    try:
        # Campaign stats
        total_campaigns = await db.musician_campaigns.count_documents({})
        active_campaigns = await db.musician_campaigns.count_documents({"status": "active"})
        completed_campaigns = await db.musician_campaigns.count_documents({"status": "completed"})
        
        # Donation stats
        all_donations = await db.donations.find({"payment_status": "completed"}).to_list(10000)
        total_donated = sum(d.get("amount", 0) for d in all_donations)
        total_donors = len(set(d.get("donor_id") for d in all_donations if d.get("donor_id")))
        
        # Advice stats
        total_advice = await db.support_advice.count_documents({})
        total_support_requests = await db.support_requests.count_documents({})
        
        # Success stories (completed campaigns)
        success_campaigns = await db.musician_campaigns.find({
            "status": "completed"
        }).limit(3).to_list(3)
        
        return {
            "campaigns": {
                "total": total_campaigns,
                "active": active_campaigns,
                "completed": completed_campaigns
            },
            "donations": {
                "total_amount": total_donated,
                "total_donors": total_donors,
                "total_transactions": len(all_donations)
            },
            "community": {
                "total_advice": total_advice,
                "total_support_requests": total_support_requests
            },
            "success_stories": [prepare_from_mongo(story) for story in success_campaigns]
        }
        
    except Exception as e:
        logger.error(f"Error getting solidarity stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")

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
    
    # Initialize subscription plans if not exist
    subscription_count = await db.subscription_plans.count_documents({})
    if subscription_count == 0:
        logger.info("Initializing subscription plans...")
        
        subscription_plans = [
            SubscriptionPlan(
                name="Basique",
                description="Plan parfait pour les musiciens débutants qui découvrent la communauté US EXPLO",
                price_monthly=9.99,
                price_yearly=99.99,
                features=[
                    "Upload jusqu'à 5 pistes par mois",
                    "Accès à la communauté musicale",
                    "Création de 3 groupes maximum",
                    "Messages privés illimités",
                    "Lecteur audio standard",
                    "Support email"
                ],
                max_uploads_per_month=5,
                max_groups=3,
                can_sell_music=False,
                can_create_events=False,
                priority_support=False,
                analytics_access=False
            ),
            SubscriptionPlan(
                name="Pro",
                description="Plan idéal pour les musiciens sérieux qui veulent vendre leur musique et développer leur carrière",
                price_monthly=24.99,
                price_yearly=249.99,
                features=[
                    "Upload jusqu'à 25 pistes par mois",
                    "Vente de musique dans la marketplace",
                    "Commission réduite (10% au lieu de 15%)",
                    "Création de 10 groupes maximum",
                    "Statistiques détaillées",
                    "Création d'événements",
                    "Support prioritaire",
                    "Badge professionnel"
                ],
                max_uploads_per_month=25,
                max_groups=10,
                can_sell_music=True,
                can_create_events=True,
                priority_support=True,
                analytics_access=True
            ),
            SubscriptionPlan(
                name="Premium",
                description="Plan complet pour les professionnels de la musique et labels indépendants",
                price_monthly=49.99,
                price_yearly=499.99,
                features=[
                    "Uploads illimités",
                    "Vente de musique avec commission minimale (5%)",
                    "Groupes illimités",
                    "Analytics avancés et insights",
                    "Support téléphonique prioritaire",
                    "API d'intégration",
                    "Promotion sur la page d'accueil",
                    "Accès anticipé aux nouvelles fonctionnalités",
                    "Badge premium exclusif"
                ],
                max_uploads_per_month=999999,  # Unlimited
                max_groups=999999,  # Unlimited
                can_sell_music=True,
                can_create_events=True,
                priority_support=True,
                analytics_access=True
            )
        ]
        
        for plan_data in subscription_plans:
            plan = SubscriptionPlan(**plan_data.dict())
            await db.subscription_plans.insert_one(prepare_for_mongo(plan.dict()))
        
        logger.info(f"Initialized {len(subscription_plans)} subscription plans")
    
    logger.info("US EXPLO API fully initialized and ready! 🎵🌍")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    logger.info("Database connection closed")