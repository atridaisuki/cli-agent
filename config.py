from dotenv import load_dotenv
import os

load_dotenv()

LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-chat")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4096"))
