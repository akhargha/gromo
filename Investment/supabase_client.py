# supabase_client.py
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env

SUPABASE_URL = os.getenv("REACT_APP_SUPABASE_URL")
SUPABASE_KEY = os.getenv("REACT_APP_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL or SUPABASE_KEY is not set in environment variables.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
