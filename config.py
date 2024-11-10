import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

DB_CONFIG = {
    "user": os.getenv("USER_DB"),
    "password": os.getenv("PASSWORD_DB"),
    "host": os.getenv("URL_DB"),
    "port": os.getenv("PORT_DB"),
    "db": os.getenv("DATABASE_NAME_DB"),
}

MODEL = SentenceTransformer("jinaai/jina-embeddings-v3", trust_remote_code=True)
