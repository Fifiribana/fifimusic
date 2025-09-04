from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="US EXPLO API", description="Universal Sound Exploration API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models for US EXPLO

# User Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    username: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    preferences: Optional[List[str]] = []
    favorite_regions: Optional[List[str]] = []

class UserCreate(BaseModel):
    email: str
    username: str
    password: str

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
    artwork_url: str
    price: float
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    downloads: int = 0
    likes: int = 0

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
            if key in ['created_at', 'timestamp'] and isinstance(value, str):
                try:
                    item[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except ValueError:
                    pass
    return item

# Routes

# Original routes
@api_router.get("/")
async def root():
    return {"message": "US EXPLO API - Universal Sound Exploration"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    await db.status_checks.insert_one(prepare_for_mongo(status_obj.dict()))
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**parse_from_mongo(status_check)) for status_check in status_checks]

# Music Track Routes
@api_router.get("/tracks", response_model=List[Track])
async def get_tracks(
    region: Optional[str] = Query(None, description="Filter by region"),
    style: Optional[str] = Query(None, description="Filter by style"),
    instrument: Optional[str] = Query(None, description="Filter by instrument"),
    mood: Optional[str] = Query(None, description="Filter by mood"),
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
    logger.info("Starting US EXPLO API...")
    
    # Check if we already have sample data
    track_count = await db.tracks.count_documents({})
    if track_count == 0:
        logger.info("Initializing sample data...")
        
        # Sample tracks
        sample_tracks = [
            TrackCreate(
                title="Desert Winds",
                artist="Khalid Al-Rashid",
                region="Moyen-Orient",
                style="Traditional",
                instrument="Oud",
                duration=245,
                bpm=120,
                mood="Méditatif",
                audio_url="https://example.com/desert-winds.mp3",
                artwork_url="https://images.unsplash.com/photo-1528190303099-2408e63c79e3?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njd8MHwxfHNlYXJjaHwyfHx3b3JsZCUyMG11c2ljfGVufDB8fHx8MTc1NzAxMTU0MXww&ixlib=rb-4.1.0&q=85",
                price=2.99,
                description="A haunting melody from the Arabian desert"
            ),
            TrackCreate(
                title="Lagos Nights",
                artist="Femi Adebayo",
                region="Afrique",
                style="Afrobeat",
                instrument="Talking Drum",
                duration=320,
                bpm=145,
                mood="Énergique",
                audio_url="https://example.com/lagos-nights.mp3",
                artwork_url="https://images.unsplash.com/photo-1565719178004-420e3480e2b5?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NjZ8MHwxfHNlYXJjaHw0fHxnbG9iYWwlMjBpbnN0cnVtZW50c3xlbnwwfHx8fDE3NTcwMTE1NDZ8MA&ixlib=rb-4.1.0&q=85",
                price=3.49,
                description="Pulsating rhythms from the heart of Lagos"
            ),
            TrackCreate(
                title="Himalayan Echo",
                artist="Tenzin Norbu",
                region="Asie",
                style="Tibetan Folk",
                instrument="Singing Bowl",
                duration=180,
                bpm=60,
                mood="Méditatif",
                audio_url="https://example.com/himalayan-echo.mp3",
                artwork_url="https://images.unsplash.com/photo-1551973732-463437696ab3?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njd8MHwxfHNlYXJjaHwxfHx3b3JsZCUyMG11c2ljfGVufDB8fHx8MTc1NzAxMTU0MXww&ixlib=rb-4.1.0&q=85",
                price=2.79,
                description="Sacred sounds from the roof of the world"
            ),
            TrackCreate(
                title="Samba Sunrise",
                artist="Maria Santos",
                region="Amérique du Sud",
                style="Samba",
                instrument="Cuica",
                duration=285,
                bpm=160,
                mood="Festif",
                audio_url="https://example.com/samba-sunrise.mp3",
                artwork_url="https://images.unsplash.com/photo-1700419420072-8583b28f2036?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NjZ8MHwxfHNlYXJjaHwzfHxnbG9iYWwlMjBpbnN0cnVtZW50c3xlbnwwfHx8fDE3NTcwMTE1NDZ8MA&ixlib=rb-4.1.0&q=85",
                price=3.99,
                description="Carnival energy from the streets of Rio"
            ),
            TrackCreate(
                title="Celtic Morning",
                artist="Seamus O'Connor",
                region="Europe",
                style="Celtic Folk",
                instrument="Bodhrán",
                duration=210,
                bpm=90,
                mood="Inspirant",
                audio_url="https://example.com/celtic-morning.mp3",
                artwork_url="https://images.unsplash.com/photo-1573247353133-0290e4606fbf?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1NzZ8MHwxfHNlYXJjaHwyfHxtdXNpYyUyMGV4cGxvcmF0aW9ufGVufDB8fHx8MTc1NzAxMTU2MHww&ixlib=rb-4.1.0&q=85",
                price=2.49,
                description="Misty landscapes through ancient melodies"
            ),
            TrackCreate(
                title="Dreamtime Stories",
                artist="Billy Walkabout",
                region="Océanie",
                style="Aboriginal",
                instrument="Didgeridoo",
                duration=355,
                bpm=75,
                mood="Spirituel",
                audio_url="https://example.com/dreamtime-stories.mp3",
                artwork_url="https://images.unsplash.com/photo-1682358061383-ee32b66f9c8e?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1NzZ8MHwxfHNlYXJjaHw0fHxtdXNpYyUyMGV4cGxvcmF0aW9ufGVufDB8fHx8MTc1NzAxMTU2MHww&ixlib=rb-4.1.0&q=85",
                price=4.29,
                description="Ancient stories told through sacred sounds"
            )
        ]
        
        # Insert sample tracks
        for track_data in sample_tracks:
            track = Track(**track_data.dict())
            await db.tracks.insert_one(prepare_for_mongo(track.dict()))
        
        # Sample collections
        # Get some track IDs for collections
        tracks = await db.tracks.find().to_list(6)
        track_ids = [track["id"] for track in tracks]
        
        sample_collections = [
            CollectionCreate(
                title="Découvertes du Mois",
                description="Les dernières trouvailles musicales du monde entier",
                tracks=track_ids[:4],
                image_url="https://images.unsplash.com/photo-1700419420072-8583b28f2036?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NjZ8MHwxfHNlYXJjaHwzfHxnbG9iYWwlMjBpbnN0cnVtZW50c3xlbnwwfHx8fDE3NTcwMTE1NDZ8MA&ixlib=rb-4.1.0&q=85",
                featured=True
            ),
            CollectionCreate(
                title="Rythmes Africains",
                description="L'essence vibrant de l'Afrique musicale",
                tracks=track_ids[1:3],
                image_url="https://images.unsplash.com/photo-1565719178004-420e3480e2b5?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NjZ8MHwxfHNlYXJjaHw0fHxnbG9iYWwlMjBpbnN0cnVtZW50c3xlbnwwfHx8fDE3NTcwMTE1NDZ8MA&ixlib=rb-4.1.0&q=85",
                featured=True
            ),
            CollectionCreate(
                title="Mélodies Orientales",
                description="Les sons mystiques de l'Orient",
                tracks=track_ids[0:2],
                image_url="https://images.unsplash.com/photo-1551973732-463437696ab3?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njd8MHwxfHNlYXJjaHwxfHx3b3JsZCUyMG11c2ljfGVufDB8fHx8MTc1NzAxMTU0MXww&ixlib=rb-4.1.0&q=85",
                featured=True
            )
        ]
        
        # Insert sample collections
        for collection_data in sample_collections:
            collection = Collection(**collection_data.dict())
            await db.collections.insert_one(prepare_for_mongo(collection.dict()))
        
        logger.info("Sample data initialized successfully!")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    logger.info("Database connection closed")