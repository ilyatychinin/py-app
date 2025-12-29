import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
APP_HOST = os.getenv('APP_HOST', 'localhost')
APP_PORT = int(os.getenv('APP_PORT', 5000))
APP_URL = f"http://{APP_HOST}:{APP_PORT}"
