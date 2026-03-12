import os
os.environ.setdefault("API_KEY", "f1-api-key")

from a2wsgi import ASGIMiddleware
from main import app

application = ASGIMiddleware(app)
