import redis
from config import Config

class RedisConnector:
    def __init__(self):
        self.connection = redis.Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            db=Config.REDIS_DB,
            decode_responses=True
        )
    
    def store_session(self, session_id, data):
        self.connection.hset(f"session:{session_id}", mapping=data)
    
    def get_session(self, session_id):
        return self.connection.hgetall(f"session:{session_id}")
    
    def update_session_field(self, session_id, field, value):
        self.connection.hset(f"session:{session_id}", field, value)
    
    def delete_session(self, session_id):
        self.connection.delete(f"session:{session_id}")