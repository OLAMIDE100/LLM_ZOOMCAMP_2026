import sys

from dotenv import load_dotenv
from openai import OpenAI

from metrics import RAGWithMetrics
from embedder import Embedder
import psycopg



def create_assistant():
    load_dotenv()
    conn = psycopg.connect(
    "postgresql://user:pswd@monitoring:5432/faq"
    )



    return RAGWithMetrics(
        llm_client=OpenAI(),
        embedder=Embedder(),
        conn=conn,
        course='llm-zoomcamp'
    )
