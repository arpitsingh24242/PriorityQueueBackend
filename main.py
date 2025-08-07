from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict, List
from fastapi.middleware.cors import CORSMiddleware
import heapq

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://messagequeue.netlify.app/"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    id: str
    priority: int
    timestamp: int

message_map: Dict[str, Message] = {}
message_heap: List[tuple] = []  
last_timestamp: Optional[int] = None 

@app.post("/add")
def add_message(msg: Message):
    global last_timestamp

    if msg.id in message_map:
        return {"error": "Message ID already exists"}

    if not (1 <= msg.priority <= 100):
        return {"error": "Priority must be between 1 and 100"}

    if last_timestamp is not None and msg.timestamp <= last_timestamp:
        return {"error": "Timestamp must be strictly increasing"}

    message_map[msg.id] = msg
    heapq.heappush(message_heap, (-msg.priority, msg.timestamp, msg.id))
    last_timestamp = msg.timestamp
    return {"message": f"Message {msg.id} added"}


@app.get("/pop")
def pop_message():
    while message_heap:
        _, _, msg_id = heapq.heappop(message_heap)
        if msg_id in message_map:
            message_map.pop(msg_id)
            return {"id": msg_id}
    return {"id": None}

@app.get("/find/{msg_id}")
def find_message(msg_id: str):
    msg = message_map.get(msg_id)
    if msg:
        return {"priority": msg.priority, "timestamp": msg.timestamp}
    return None

@app.get("/list")
def list_messages():
    sorted_msgs = sorted(
        message_map.values(),
        key=lambda m: (-m.priority, m.timestamp)
    )
    return [m.id for m in sorted_msgs]
