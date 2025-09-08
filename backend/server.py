from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="ChatMe API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models for ChatMe
class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_name: str
    receiver_name: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    is_read: bool = False

class MessageCreate(BaseModel):
    sender_name: str
    receiver_name: str
    content: str

class MessageResponse(BaseModel):
    id: str
    sender_name: str
    receiver_name: str
    content: str
    timestamp: datetime
    is_read: bool

# Legacy StatusCheck models (keep for compatibility)
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

# ChatMe API Routes
@api_router.get("/")
async def root():
    return {"message": "Bienvenue sur ChatMe API!"}

@api_router.post("/messages", response_model=MessageResponse)
async def send_message(message_data: MessageCreate):
    """Envoyer un nouveau message"""
    message = Message(**message_data.dict())
    message_dict = message.dict()
    await db.messages.insert_one(message_dict)
    return MessageResponse(**message_dict)

@api_router.get("/messages/conversation/{user1}/{user2}", response_model=List[MessageResponse])
async def get_conversation(user1: str, user2: str):
    """Récupérer l'historique des messages entre deux utilisateurs"""
    messages = await db.messages.find({
        "$or": [
            {"sender_name": user1, "receiver_name": user2},
            {"sender_name": user2, "receiver_name": user1}
        ]
    }).sort("timestamp", 1).to_list(1000)
    
    return [MessageResponse(**msg) for msg in messages]

@api_router.get("/users", response_model=List[str])
async def get_active_users():
    """Récupérer la liste des utilisateurs actifs (qui ont envoyé ou reçu des messages)"""
    # Obtenir tous les noms d'expéditeurs et de destinataires uniques
    senders = await db.messages.distinct("sender_name")
    receivers = await db.messages.distinct("receiver_name")
    
    # Combiner et supprimer les doublons
    all_users = list(set(senders + receivers))
    return sorted(all_users)

@api_router.put("/messages/{message_id}/read")
async def mark_message_as_read(message_id: str):
    """Marquer un message comme lu"""
    result = await db.messages.update_one(
        {"id": message_id}, 
        {"$set": {"is_read": True}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Message non trouvé")
    
    return {"message": "Message marqué comme lu"}

@api_router.get("/messages/unread/{username}", response_model=List[MessageResponse])
async def get_unread_messages(username: str):
    """Récupérer les messages non lus pour un utilisateur"""
    messages = await db.messages.find({
        "receiver_name": username,
        "is_read": False
    }).sort("timestamp", -1).to_list(100)
    
    return [MessageResponse(**msg) for msg in messages]

# Legacy routes (keep for compatibility)
@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

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
