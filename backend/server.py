from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import hashlib
import jwt
from emergentintegrations.llm.chat import LlmChat, UserMessage
import json
import asyncio

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="TuneMe (TM) API - Advanced Video Platform")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()
JWT_SECRET = os.environ.get('JWT_SECRET', 'tuneme-secret-key-2025')

# AI Integration
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', 'sk-emergent-57116C1DaE9573f533')

# ==================== MODELS ====================

# User Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    password_hash: str
    display_name: str
    bio: Optional[str] = ""
    avatar_url: Optional[str] = ""
    banner_url: Optional[str] = ""
    subscribers_count: int = 0
    total_views: int = 0
    total_revenue: float = 0.0
    verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    social_links: Dict[str, str] = Field(default_factory=dict)
    preferences: Dict[str, Any] = Field(default_factory=dict)

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    display_name: str
    bio: Optional[str] = ""

class UserLogin(BaseModel):
    email: str
    password: str

class UserProfile(BaseModel):
    id: str
    username: str
    display_name: str
    bio: str
    avatar_url: str
    banner_url: str
    subscribers_count: int
    total_views: int
    verified: bool
    created_at: datetime
    social_links: Dict[str, str]

# Video Models
class Video(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    creator_id: str
    creator_username: str
    thumbnail_url: str
    video_url: str
    duration: int  # in seconds
    views_count: int = 0
    likes_count: int = 0
    dislikes_count: int = 0
    comments_count: int = 0
    category: str
    tags: List[str] = Field(default_factory=list)
    ai_generated_tags: List[str] = Field(default_factory=list)
    is_ad: bool = False
    ad_type: Optional[str] = None  # "tv_commercial", "social_media", "corporate", "product_demo"
    target_audience: List[str] = Field(default_factory=list)
    budget_spent: float = 0.0
    revenue_generated: float = 0.0
    engagement_rate: float = 0.0
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    published: bool = True
    monetized: bool = False
    cpm_rate: float = 2.5  # Cost per thousand impressions
    ai_analysis: Dict[str, Any] = Field(default_factory=dict)

class VideoCreate(BaseModel):
    title: str
    description: str
    category: str
    tags: List[str] = Field(default_factory=list)
    is_ad: bool = False
    ad_type: Optional[str] = None
    target_audience: List[str] = Field(default_factory=list)

class VideoResponse(BaseModel):
    id: str
    title: str
    description: str
    creator_username: str
    thumbnail_url: str
    video_url: str
    duration: int
    views_count: int
    likes_count: int
    dislikes_count: int
    comments_count: int
    category: str
    tags: List[str]
    ai_generated_tags: List[str]
    is_ad: bool
    ad_type: Optional[str]
    upload_date: datetime
    engagement_rate: float
    ai_analysis: Dict[str, Any]

# Comment Models
class Comment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    video_id: str
    user_id: str
    username: str
    avatar_url: str
    content: str
    likes_count: int = 0
    replies_count: int = 0
    parent_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    ai_sentiment: Optional[str] = None  # "positive", "negative", "neutral"

class CommentCreate(BaseModel):
    video_id: str
    content: str
    parent_id: Optional[str] = None

# Analytics Models
class VideoAnalytics(BaseModel):
    video_id: str
    date: datetime
    views: int = 0
    unique_views: int = 0
    watch_time: int = 0  # in seconds
    likes: int = 0
    comments: int = 0
    shares: int = 0
    retention_rate: float = 0.0
    click_through_rate: float = 0.0
    revenue: float = 0.0

class ChannelAnalytics(BaseModel):
    user_id: str
    total_videos: int = 0
    total_views: int = 0
    total_subscribers: int = 0
    total_revenue: float = 0.0
    avg_engagement_rate: float = 0.0
    top_performing_videos: List[str] = Field(default_factory=list)
    audience_demographics: Dict[str, Any] = Field(default_factory=dict)
    trending_topics: List[str] = Field(default_factory=list)

# Subscription Models
class Subscription(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    subscriber_id: str
    channel_id: str
    subscribed_at: datetime = Field(default_factory=datetime.utcnow)
    notifications_enabled: bool = True

# Revenue Models
class Revenue(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    video_id: str
    amount: float
    revenue_type: str  # "ad_revenue", "sponsorship", "premium_views"
    date: datetime = Field(default_factory=datetime.utcnow)
    processed: bool = False

# Recommendation Models
class Recommendation(BaseModel):
    user_id: str
    recommended_videos: List[str]
    algorithm_version: str = "ai_v1"
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    relevance_scores: Dict[str, float] = Field(default_factory=dict)

# ==================== UTILITY FUNCTIONS ====================

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == hashed

def create_jwt_token(user_id: str, username: str) -> str:
    """Create JWT token for user"""
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def verify_jwt_token(token: str) -> Dict[str, str]:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    payload = verify_jwt_token(credentials.credentials)
    user = await db.users.find_one({"id": payload['user_id']})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user)

# AI Analysis Functions
async def analyze_video_content(title: str, description: str, tags: List[str]) -> Dict[str, Any]:
    """Analyze video content using AI"""
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"video_analysis_{uuid.uuid4()}",
            system_message="You are an AI video content analyzer for TuneMe platform. Analyze video content and provide insights."
        ).with_model("openai", "gpt-4o-mini")
        
        content = f"""
        Title: {title}
        Description: {description}
        Tags: {', '.join(tags)}
        
        Please analyze this video content and provide:
        1. Content category (Entertainment, Education, Technology, Business, etc.)
        2. Target audience (age group, interests)
        3. Engagement prediction score (1-10)
        4. Suggested additional tags (max 5)
        5. Content quality assessment
        6. Monetization potential (High/Medium/Low)
        
        Respond in JSON format only.
        """
        
        user_message = UserMessage(text=content)
        response = await chat.send_message(user_message)
        
        # Try to parse as JSON, fallback to basic analysis
        try:
            analysis = json.loads(response)
        except:
            analysis = {
                "category": "General",
                "target_audience": ["General Audience"],
                "engagement_prediction": 7.0,
                "suggested_tags": [],
                "content_quality": "Good",
                "monetization_potential": "Medium"
            }
        
        return analysis
        
    except Exception as e:
        logging.error(f"AI Analysis error: {str(e)}")
        return {
            "category": "General",
            "target_audience": ["General Audience"],
            "engagement_prediction": 5.0,
            "suggested_tags": [],
            "content_quality": "Pending Analysis",
            "monetization_potential": "Medium"
        }

async def generate_recommendations(user_id: str, user_history: List[str]) -> List[str]:
    """Generate video recommendations using AI"""
    try:
        # Get user's viewing history and preferences
        recent_videos = await db.videos.find({"id": {"$in": user_history}}).to_list(20)
        
        # Analyze preferences
        categories = [v.get('category', 'General') for v in recent_videos]
        tags = []
        for v in recent_videos:
            tags.extend(v.get('tags', []))
        
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"recommendations_{user_id}",
            system_message="You are a recommendation engine for TuneMe video platform."
        ).with_model("openai", "gpt-4o-mini")
        
        prompt = f"""
        User viewing history shows interest in:
        Categories: {', '.join(set(categories))}
        Tags: {', '.join(set(tags[:20]))}
        
        Based on this data, what video categories and tags should we prioritize for recommendations?
        Respond with JSON containing recommended_categories and recommended_tags arrays.
        """
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        try:
            ai_prefs = json.loads(response)
            recommended_categories = ai_prefs.get('recommended_categories', categories[:3])
            recommended_tags = ai_prefs.get('recommended_tags', tags[:10])
        except:
            recommended_categories = list(set(categories))[:3]
            recommended_tags = list(set(tags))[:10]
        
        # Find videos matching preferences
        query = {
            "$or": [
                {"category": {"$in": recommended_categories}},
                {"tags": {"$in": recommended_tags}}
            ],
            "id": {"$nin": user_history},  # Exclude already watched
            "published": True
        }
        
        recommended_videos = await db.videos.find(query).sort("views_count", -1).limit(20).to_list(20)
        return [v['id'] for v in recommended_videos]
        
    except Exception as e:
        logging.error(f"Recommendation error: {str(e)}")
        # Fallback to popular videos
        popular_videos = await db.videos.find({"published": True}).sort("views_count", -1).limit(10).to_list(10)
        return [v['id'] for v in popular_videos]

# ==================== AUTH ROUTES ====================

@api_router.post("/auth/register", response_model=Dict[str, Any])
async def register_user(user_data: UserCreate):
    """Register a new user"""
    # Check if user exists
    existing_user = await db.users.find_one({
        "$or": [
            {"email": user_data.email},
            {"username": user_data.username}
        ]
    })
    
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create user
    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        display_name=user_data.display_name,
        bio=user_data.bio
    )
    
    await db.users.insert_one(user.dict())
    
    # Create JWT token
    token = create_jwt_token(user.id, user.username)
    
    return {
        "message": "User registered successfully",
        "token": token,
        "user": UserProfile(**user.dict())
    }

@api_router.post("/auth/login", response_model=Dict[str, Any])
async def login_user(login_data: UserLogin):
    """Login user"""
    user = await db.users.find_one({"email": login_data.email})
    
    if not user or not verify_password(login_data.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_jwt_token(user['id'], user['username'])
    
    return {
        "message": "Login successful",
        "token": token,
        "user": UserProfile(**user)
    }

# ==================== USER ROUTES ====================

@api_router.get("/users/me", response_model=UserProfile)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return UserProfile(**current_user.dict())

@api_router.get("/users/{username}", response_model=UserProfile)
async def get_user_profile(username: str):
    """Get user profile by username"""
    user = await db.users.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserProfile(**user)

@api_router.post("/users/{user_id}/subscribe")
async def subscribe_to_channel(user_id: str, current_user: User = Depends(get_current_user)):
    """Subscribe to a channel"""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot subscribe to yourself")
    
    # Check if already subscribed
    existing_sub = await db.subscriptions.find_one({
        "subscriber_id": current_user.id,
        "channel_id": user_id
    })
    
    if existing_sub:
        raise HTTPException(status_code=400, detail="Already subscribed")
    
    # Create subscription
    subscription = Subscription(
        subscriber_id=current_user.id,
        channel_id=user_id
    )
    
    await db.subscriptions.insert_one(subscription.dict())
    
    # Update subscriber count
    await db.users.update_one(
        {"id": user_id},
        {"$inc": {"subscribers_count": 1}}
    )
    
    return {"message": "Subscribed successfully"}

# ==================== VIDEO ROUTES ====================

@api_router.post("/videos/upload", response_model=VideoResponse)
async def upload_video(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    tags: str = Form(""),
    is_ad: bool = Form(False),
    ad_type: Optional[str] = Form(None),
    target_audience: str = Form(""),
    current_user: User = Depends(get_current_user)
):
    """Upload a new video"""
    
    # Parse tags and target audience
    tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
    audience_list = [aud.strip() for aud in target_audience.split(",") if aud.strip()]
    
    # Use demo video URLs for testing (in real app, upload to cloud storage)
    video_id = str(uuid.uuid4())
    
    # Demo videos for testing - these are real accessible URLs
    demo_videos = [
        {
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            "thumbnail_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/images/BigBuckBunny.jpg"
        },
        {
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4", 
            "thumbnail_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/images/ElephantsDream.jpg"
        },
        {
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
            "thumbnail_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/images/ForBiggerBlazes.jpg"
        },
        {
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
            "thumbnail_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/images/Sintel.jpg"
        }
    ]
    
    # Randomly select a demo video
    import random
    selected_demo = random.choice(demo_videos)
    video_url = selected_demo["video_url"]
    thumbnail_url = selected_demo["thumbnail_url"]
    
    # AI Analysis
    ai_analysis = await analyze_video_content(title, description, tags_list)
    
    # Create video
    video = Video(
        id=video_id,
        title=title,
        description=description,
        creator_id=current_user.id,
        creator_username=current_user.username,
        thumbnail_url=thumbnail_url,
        video_url=video_url,
        duration=180,  # Simulated duration
        category=category,
        tags=tags_list,
        ai_generated_tags=ai_analysis.get('suggested_tags', []),
        is_ad=is_ad,
        ad_type=ad_type,
        target_audience=audience_list,
        ai_analysis=ai_analysis
    )
    
    await db.videos.insert_one(video.dict())
    
    return VideoResponse(**video.dict())

@api_router.get("/videos", response_model=List[VideoResponse])
async def get_videos(
    category: Optional[str] = None,
    is_ad: Optional[bool] = None,
    limit: int = Query(20, le=100),
    skip: int = Query(0, ge=0)
):
    """Get videos with filtering"""
    query = {"published": True}
    
    if category:
        query["category"] = category
    if is_ad is not None:
        query["is_ad"] = is_ad
    
    videos = await db.videos.find(query).sort("upload_date", -1).skip(skip).limit(limit).to_list(limit)
    return [VideoResponse(**video) for video in videos]

@api_router.get("/videos/{video_id}", response_model=VideoResponse)
async def get_video(video_id: str):
    """Get video by ID"""
    video = await db.videos.find_one({"id": video_id})
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Increment view count
    await db.videos.update_one(
        {"id": video_id},
        {"$inc": {"views_count": 1}}
    )
    
    return VideoResponse(**video)

@api_router.post("/videos/{video_id}/like")
async def like_video(video_id: str, current_user: User = Depends(get_current_user)):
    """Like a video"""
    # Check if video exists
    video = await db.videos.find_one({"id": video_id})
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Check if already liked
    existing_like = await db.likes.find_one({
        "user_id": current_user.id,
        "video_id": video_id
    })
    
    if existing_like:
        # Unlike
        await db.likes.delete_one({"user_id": current_user.id, "video_id": video_id})
        await db.videos.update_one({"id": video_id}, {"$inc": {"likes_count": -1}})
        return {"message": "Video unliked"}
    else:
        # Like
        like_data = {
            "id": str(uuid.uuid4()),
            "user_id": current_user.id,
            "video_id": video_id,
            "created_at": datetime.utcnow()
        }
        await db.likes.insert_one(like_data)
        await db.videos.update_one({"id": video_id}, {"$inc": {"likes_count": 1}})
        return {"message": "Video liked"}

# ==================== COMMENT ROUTES ====================

@api_router.post("/comments", response_model=Comment)
async def create_comment(comment_data: CommentCreate, current_user: User = Depends(get_current_user)):
    """Create a comment"""
    # Verify video exists
    video = await db.videos.find_one({"id": comment_data.video_id})
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # AI Sentiment Analysis
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"sentiment_{uuid.uuid4()}",
            system_message="Analyze sentiment of comments. Respond with only: positive, negative, or neutral"
        ).with_model("openai", "gpt-4o-mini")
        
        user_message = UserMessage(text=f"Analyze sentiment: {comment_data.content}")
        sentiment_response = await chat.send_message(user_message)
        sentiment = sentiment_response.strip().lower()
        
        if sentiment not in ['positive', 'negative', 'neutral']:
            sentiment = 'neutral'
            
    except Exception as e:
        sentiment = 'neutral'
    
    comment = Comment(
        video_id=comment_data.video_id,
        user_id=current_user.id,
        username=current_user.username,
        avatar_url=current_user.avatar_url,
        content=comment_data.content,
        parent_id=comment_data.parent_id,
        ai_sentiment=sentiment
    )
    
    await db.comments.insert_one(comment.dict())
    
    # Update comment count
    await db.videos.update_one(
        {"id": comment_data.video_id},
        {"$inc": {"comments_count": 1}}
    )
    
    return comment

@api_router.get("/videos/{video_id}/comments", response_model=List[Comment])
async def get_video_comments(video_id: str, limit: int = Query(50, le=100)):
    """Get comments for a video"""
    comments = await db.comments.find({"video_id": video_id, "parent_id": None}).sort("created_at", -1).limit(limit).to_list(limit)
    return [Comment(**comment) for comment in comments]

# ==================== ANALYTICS ROUTES ====================

@api_router.get("/analytics/channel/{user_id}", response_model=ChannelAnalytics)
async def get_channel_analytics(user_id: str, current_user: User = Depends(get_current_user)):
    """Get channel analytics"""
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get user's videos
    user_videos = await db.videos.find({"creator_id": user_id}).to_list(1000)
    
    total_views = sum(v.get('views_count', 0) for v in user_videos)
    total_revenue = sum(v.get('revenue_generated', 0) for v in user_videos)
    
    # Get subscriber count
    subscriber_count = await db.subscriptions.count_documents({"channel_id": user_id})
    
    # Calculate engagement rate
    total_interactions = sum(
        v.get('likes_count', 0) + v.get('comments_count', 0) 
        for v in user_videos
    )
    avg_engagement_rate = (total_interactions / total_views * 100) if total_views > 0 else 0
    
    # Top performing videos
    sorted_videos = sorted(user_videos, key=lambda x: x.get('views_count', 0), reverse=True)
    top_videos = [v['id'] for v in sorted_videos[:5]]
    
    analytics = ChannelAnalytics(
        user_id=user_id,
        total_videos=len(user_videos),
        total_views=total_views,
        total_subscribers=subscriber_count,
        total_revenue=total_revenue,
        avg_engagement_rate=round(avg_engagement_rate, 2),
        top_performing_videos=top_videos
    )
    
    return analytics

# ==================== RECOMMENDATION ROUTES ====================

@api_router.get("/recommendations", response_model=List[VideoResponse])
async def get_recommendations(current_user: User = Depends(get_current_user)):
    """Get personalized video recommendations"""
    
    # Get user's viewing history (simulated)
    user_history = []  # In real app, track user views
    
    # Generate AI recommendations
    recommended_video_ids = await generate_recommendations(current_user.id, user_history)
    
    # Get recommended videos
    if recommended_video_ids:
        videos = await db.videos.find({"id": {"$in": recommended_video_ids}}).to_list(20)
        return [VideoResponse(**video) for video in videos]
    
    # Fallback to trending videos
    trending_videos = await db.videos.find({"published": True}).sort("views_count", -1).limit(10).to_list(10)
    return [VideoResponse(**video) for video in trending_videos]

# ==================== MARKETPLACE ROUTES ====================

@api_router.get("/marketplace/ad-spaces", response_model=List[Dict[str, Any]])
async def get_available_ad_spaces():
    """Get available advertising spaces"""
    # Simulate ad space marketplace
    ad_spaces = [
        {
            "id": str(uuid.uuid4()),
            "video_id": "sample_video_1",
            "creator": "TechReviewer",
            "category": "Technology",
            "estimated_views": 50000,
            "cpm_rate": 3.5,
            "target_audience": ["Tech Enthusiasts", "Gamers"],
            "available_slots": ["pre_roll", "mid_roll", "post_roll"]
        },
        {
            "id": str(uuid.uuid4()),
            "video_id": "sample_video_2", 
            "creator": "CookingMaster",
            "category": "Lifestyle",
            "estimated_views": 75000,
            "cpm_rate": 2.8,
            "target_audience": ["Food Lovers", "Home Cooks"],
            "available_slots": ["pre_roll", "sponsored_segment"]
        }
    ]
    
    return ad_spaces

# ==================== LEGACY ROUTES (ChatMe compatibility) ====================

@api_router.get("/")
async def root():
    return {"message": "Bienvenue sur TuneMe (TM) - Plateforme Vidéo Publicitaire Avancée!"}

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

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()