import json
import redis
from core.celery_app import celery_app
r= redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
def publish_event(channel: str, event_data: dict):
    r.publish(channel, json.dumps(event_data))
def listen_to_channel(channel: str):
    pubsub= r.pubsub()
    pubsub.subscribe(channel)
    return pubsub