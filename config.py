import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
LOLZ_API_TOKEN = os.getenv("LOLZ_API_TOKEN")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 10))
