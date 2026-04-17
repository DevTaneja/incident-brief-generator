"""
Jira Client - Search issues by text
"""

import httpx
import logging
from typing import List, Dict, Any
from base64 import b64encode

logger = logging.getLogger(__name__)


class JiraClient:
    """
    Client for Jira Cloud REST API.
    Searches issues by text in summary, description, and comments.
    """
    
    def __init__(self, url: str, email: str, api_token: str, project_key: str):
        self.url = url.rstrip('/')
        self.email = email
        self.api_token = api_token
        self.project_key = project_key
        self.search_url = f"{self.url}/rest/api/3/search/jql"
        
        # Basic auth with email + API token
        auth_string = f"{email}:{api_token}"
        encoded_auth = b64encode(auth_string.encode()).decode()
        self.headers = {
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/json"
        }
    
    async def search_by_keywords(self, keywords: List[str], max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search Jira issues by keywords in text.
        """
        if not keywords:
            return []
        
        # Build JQL query
        text_conditions = [f'text ~ "{keyword}"' for keyword in keywords]
        jql = f'project = {self.project_key} AND {" AND ".join(text_conditions)}'
        
        logger.info(f"Searching Jira with JQL: {jql}")
        
        # For the new API, jql is a query parameter
        params = {
            "jql": jql,
            "maxResults": max_results,
            "fields": "summary,status,priority,description,created,updated"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.search_url,
                headers=self.headers,
                params=params,
                timeout=30.0
            )
            
            if response.status_code != 200:
                logger.error(f"Jira search failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return []
            
            data = response.json()
            issues = data.get("issues", [])
            
            # Format the results
            results = []
            for issue in issues:
                fields = issue.get("fields", {})
                results.append({
                    "key": issue.get("key"),
                    "summary": fields.get("summary"),
                    "status": fields.get("status", {}).get("name"),
                    "priority": fields.get("priority", {}).get("name"),
                    "description": fields.get("description"),
                    "created": fields.get("created"),
                    "updated": fields.get("updated"),
                    "url": f"{self.url}/browse/{issue.get('key')}"
                })
            
            logger.info(f"Found {len(results)} issues for keywords: {keywords}")
            return results
    
    async def search_by_error_message(self, error_message: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search Jira by full error message (splits into keywords).
        
        Args:
            error_message: The error message from Splunk logs
            max_results: Maximum number of issues to return
        
        Returns:
            List of matching issues
        """
        # Simple keyword extraction from error message
        # Remove common words and split
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        words = error_message.lower().split()
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        
        # Take top 5 keywords
        keywords = keywords[:5]
        
        if not keywords:
            return []
        
        return await self.search_by_keywords(keywords, max_results)