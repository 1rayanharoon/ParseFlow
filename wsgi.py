# wsgi.py
from vercel_wsgi import VercelWSGI
from app import app

handler = VercelWSGI(app)
