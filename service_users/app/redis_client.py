import redis
import os

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "host.docker.internal"),  # <-- changer localhost
    port=6379,
    decode_responses=True
)
