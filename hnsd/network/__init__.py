import os

from hnsd.network.structures import IPAddress

LOCAL_ROUTER = IPAddress(os.getenv("LOCAL_IP"))
GOOGLE_DNS = IPAddress("8.8.8.8")
CLOUDFLARE = IPAddress("1.1.1.1")