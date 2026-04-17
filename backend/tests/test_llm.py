"""
Test Groq API directly.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.integrations.llm_client import LLMClient

async def test_groq():
    print(f"Model: {settings.groq_model}")
    print(f"API Key exists: {bool(settings.groq_api_key)}")
    
    client = LLMClient(
        api_key=settings.groq_api_key,
        model=settings.groq_model
    )
    
    # Test simple chat
    print("\n1. Testing simple chat...")
    response = await client._chat("Say 'Hello World'")
    print(f"Response: {response}")
    
    # Test keyword extraction
    print("\n2. Testing keyword extraction...")
    keywords = await client.extract_keywords("Database connection failed due to timeout in payment service")
    print(f"Keywords: {keywords}")

if __name__ == "__main__":
    asyncio.run(test_groq())