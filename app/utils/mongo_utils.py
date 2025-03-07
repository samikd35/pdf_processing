import os
from pymongo import MongoClient
from urllib.parse import quote_plus
from dotenv import load_dotenv
from openai import OpenAI
import json

# Load environment variables
load_dotenv()

# MongoDB connection setup
username = quote_plus(os.getenv("MONGO_USERNAME"))
password = quote_plus(os.getenv("MONGO_PASSWORD"))
MONGO_URI = f"mongodb+srv://{username}:{password}@cluster0.fq7zh.mongodb.net/?retryWrites=true&w=majority&tls=true&appName=Cluster0"

client = MongoClient(MONGO_URI)
db = client["Dossie_Scholars"]
collection = db["AASTU"]

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text):
    """Generate embeddings for the given text using OpenAI's embedding model."""
    try:
        response = openai_client.embeddings.create(
            input=text,
            model="text-embedding-3-small"  # Using OpenAI's embedding model
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None

def create_vector_index():
    """Create a vector index in MongoDB if it doesn't exist."""
    try:
        # Check if the index already exists
        existing_indexes = collection.index_information()
        if "vector_index" not in existing_indexes:
            # Create a 2d vector index on the embedding field
            collection.create_index(
                [("embedding", "vector")],
                name="vector_index"
            )
            print("Vector index created successfully")
        else:
            print("Vector index already exists")
    except Exception as e:
        print(f"Error creating vector index: {e}")

def store_document(chunks, metadata):
    """Store document chunks and their embeddings in MongoDB."""
    document_ids = []
    
    try:
        for i, chunk in enumerate(chunks):
            # Generate embedding for the chunk
            embedding = get_embedding(chunk)
            
            if embedding:
                # Create document with metadata and embedding
                document = {
                    "text": chunk,
                    "embedding": embedding,
                    "metadata": metadata,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
                
                # Insert document into MongoDB
                result = collection.insert_one(document)
                document_ids.append(str(result.inserted_id))
            
        return document_ids
    except Exception as e:
        print(f"Error storing document: {e}")
        raise
