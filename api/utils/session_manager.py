import redis
import uuid
from datetime import datetime
from api.utils.encryption_utils import EncryptionManager

class SessionManager:
    def __init__(self):
        self.redis_client = redis.Redis(host="localhost", port=6379, db=0)
        self.session_timeout = 3600  # 1 hour
        self.max_sessions_per_user = 5
        self.encryption_manager = EncryptionManager()
        self.session_prefix = "session:"

    def create_session(self, user_id: str, device_info: str) -> str:
        """Create a new session"""
        session_id = str(uuid.uuid4())

        # Check and remove oldest session if limit reached
        self.enforce_session_limit(user_id)

        session_data = {
            "user_id": user_id,
            "device_info": device_info,
            "device_fingerprint": DeviceFingerprint().generate_fingerprint(),
            "created_at": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat(),
        }
        encrypted_data = self.encryption_manager.encrypt(str(session_data))
        self.redis_client.setex(f"{self.session_prefix}{session_id}", self.session_timeout, encrypted_data)
        return session_id

    def enforce_session_limit(self, user_id: str) -> None:
        """Enforce maximum sessions per user"""
        sessions = self.redis_client.keys(f"{user_id}:session:*")
        if len(sessions) >= self.max_sessions_per_user:
            oldest_session = min(sessions, key=lambda s: self.redis_client.ttl(s))
            self.redis_client.delete(oldest_session)
