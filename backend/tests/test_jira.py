"""
Test Jira search functionality.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.integrations.jira_client import JiraClient

async def test_jira():
    print("Testing Jira Search")
    print("-" * 30)
    
    # Check if Jira is configured
    if not settings.jira_url or not settings.jira_email or not settings.jira_api_token:
        print("❌ Jira not configured. Please add to .env:")
        print("   JIRA_URL=https://your-domain.atlassian.net")
        print("   JIRA_EMAIL=your-email@example.com")
        print("   JIRA_API_TOKEN=your-token")
        print("   JIRA_PROJECT_KEY=IBG")
        return
    
    client = JiraClient(
        url=settings.jira_url,
        email=settings.jira_email,
        api_token=settings.jira_api_token,
        project_key=settings.jira_project_key
    )
    
    # Test with sample keywords
    keywords = ["database", "timeout"]
    print(f"\n1. Searching for keywords: {keywords}")
    results = await client.search_by_keywords(keywords)
    
    print(f"   Found {len(results)} issues")
    for issue in results:
        print(f"   - {issue['key']}: {issue['summary']} ({issue['status']})")
    
    # Test with error message
    error = "Database connection failed due to timeout in payment service"
    print(f"\n2. Searching by error message: {error[:50]}...")
    results = await client.search_by_error_message(error)
    
    print(f"   Found {len(results)} issues")
    for issue in results:
        print(f"   - {issue['key']}: {issue['summary']}")

if __name__ == "__main__":
    asyncio.run(test_jira())