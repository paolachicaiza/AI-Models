import redis
import os
from dotenv import load_dotenv
from urllib.parse import urlparse
load_dotenv()

REDIS_URL = os.environ.get("REDIS_URL")
REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")

class _RedisClient:
  def __init__(self):
    self.host = urlparse(REDIS_URL).hostname
    self.client = redis.Redis(
      host=self.host,
      port=6379,
      db=0
    )
    if self.client.ping():
      print("[Redis]: Successfully connected to Redis")
    else:
      raise Exception("[Redis]: Failed to connect to Redis")

  def __call__(self, *args, **kwds):
    return self.client

  def get_files(self, dataset: str, file_name: str):
    return self.client.hget('api-cache', dataset + "/" + file_name)


redis = _RedisClient()