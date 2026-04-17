"""
Test Splunk search - Updated to show parsed results.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.integrations.splunk_client import SplunkSearchClient

async def test_search():
    print("Testing Splunk Search")
    print("-" * 30)
    
    client = SplunkSearchClient(
        host="localhost",
        port=8089,
        username="Dev@1234",
        password="Dev@1234"
    )
    
    print("Searching for request_id='test-003' in last 24 hours...")
    
    results = await client.search_by_request_id(
        request_id="test-003",
        time_range="24h",
        index="main"
    )
    
    print(f"\nFound {len(results)} results")
    
    for result in results:
        print(f"\n--- Log Entry ---")
        print(f"Request ID: {result.get('requestId')}")
        print(f"Message: {result.get('message')}")
        print(f"Level: {result.get('level')}")
        print(f"Timestamp: {result.get('timestamp')}")

if __name__ == "__main__":
    asyncio.run(test_search())