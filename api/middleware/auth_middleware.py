# Initialize Redis client with error handling
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    logging.error(f"Failed to initialize Redis client: {str(e)}")
    redis_client = None

# Token verification and user assignment
try:
    claims = token_manager.verify_token(token)
    request.user = claims
except jwt.InvalidTokenError as e:
    if token_manager.can_refresh(token):
        new_token = token_manager.refresh_token(token)
        if new_token:
