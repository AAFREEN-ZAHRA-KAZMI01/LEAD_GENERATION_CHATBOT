from openai import OpenAI
from config import Config

client = OpenAI(api_key=Config.OPENAI_API_KEY)

def get_embedding(text):
    response = client.embeddings.create(
        input=text,
        model=Config.EMBEDDING_MODEL
    )
    return response.data[0].embedding