import json
from core.celery_app import celery_app
import redis
from chat.domain.events.conversation_event import ConversationCreatedEvent
r= redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
async def bridge_conversation_to_ingestion(event: ConversationCreatedEvent):
    payload = {
        "subject_id": str(event.subject_id),
        "conversation_id": str(event.conversation_id),
    }
    r.publish("ingestion_events", json.dumps(payload))
    
