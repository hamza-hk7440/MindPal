import json
import asyncio
import redis
from uuid import UUID
from core.celery_app import celery_app
from ingestion.infrastructure.tasks import process_chunks_task
from ingestion.infrastructure.database.repositories.resource_repository import ResourceRepository
from chat.infrastructure.database.session import _get_or_create_supabase_client

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

async def fetch_and_process_resources(subject_id_str: str):
    client = await _get_or_create_supabase_client()
    repo = ResourceRepository(client=client)
    subject_id = UUID(subject_id_str)
    
    resources, _ = await repo.get_all_resources(subject_id=subject_id, limit=100)
    
    for resource in resources:
        process_chunks_task.delay(str(resource.id), str(subject_id))

def start_ingestion_listener():
    pubsub = r.pubsub()
    pubsub.subscribe("ingestion_events")
    print("Listening for ingestion events...")
    
    for message in pubsub.listen():
        if message['type'] == 'message':
            data = json.loads(message['data'])
            subject_id = data['subject_id']
            print(f"Received ingestion event for subject_id: {subject_id}")
            
            asyncio.run(fetch_and_process_resources(subject_id))