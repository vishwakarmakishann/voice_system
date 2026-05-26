from slowapi import Limiter
from slowapi.util import get_remote_address

# Use the IP address as the default key for rate limiting
limiter = Limiter(key_func=get_remote_address)
