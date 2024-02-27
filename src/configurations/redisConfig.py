from dotenv import load_dotenv
load_dotenv()
from typing import Optional
import os
import platform
import redis


class RedisConfig():
    ssl_ca_certs: Optional[str]  # Type hint for the attribute

    def __init__(self):
        host = os.environ.get("REDIS_HOST")
        port = os.environ.get("REDIS_PORT")
        # password = os.environ.get("REDIS_PASSWORD")
        operating_system = platform.system()
        if operating_system == 'Linux':
            self.ssl_ca_certs = "/etc/ssl/certs/ca-certificates.crt"
        elif operating_system == 'Darwin':  # macOS
            self.ssl_ca_certs = "/etc/ssl/cert.pem"  # Update to macOS path
        else:
            raise ValueError(f"Unsupported operating system: {operating_system}")
        # self.redis = redis.Redis(host=host, port=port, password=password, ssl=False, ssl_ca_certs=self.ssl_ca_certs)
        self.redis = redis.Redis(host=host, port=port, ssl=False, ssl_ca_certs=self.ssl_ca_certs)

    def set_value(self, key, value):
        self.redis.set(key, value) 

    def get_value(self, key):
        return self.redis.get(key)  