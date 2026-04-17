"""
LLM Client - Keyword extraction and analysis using Groq API
"""

import logging
import json
import re
from typing import List, Dict, Any
import httpx

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Client for Groq LLM API (fast, free tier).
    """
    
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
    
    async def extract_keywords(self, error_message: str) -> List[str]:
        """
        Extract search keywords from an error message using LLM.
        """
        prompt = f"""Extract 3-5 important search keywords from this error message for Jira search.

Error message: "{error_message}"

Return ONLY a JSON array of keywords, nothing else.

Example: ["database", "connection", "timeout"]

Keywords:"""
        
        response = await self._chat(prompt)
        
        # Debug: print the actual response
        print(f"DEBUG LLM Response: {response}")
        
        # Parse response to extract keywords
        try:
            # Clean the response
            response = response.strip()
            if response.startswith('['):
                keywords = json.loads(response)
                return keywords[:5]
        except Exception as e:
            print(f"DEBUG Parse error: {e}")
            pass
        
        # Fallback: simple extraction
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "failed", "due", "to"}
        words = error_message.lower().split()
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        return keywords[:5]
    
    async def analyze_incident(
        self,
        error_message: str,
        logs: List[Dict[str, Any]],
        metrics: Dict[str, Any],
        jira_issues: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate analysis and recommendations from all incident data.
        """
        
        # Format logs
        logs_text = ""
        for log in logs[:5]:
            logs_text += f"- {log.get('timestamp')}: {log.get('level')} - {log.get('message')}\n"
        
        # Format Jira issues
        jira_text = ""
        for issue in jira_issues[:3]:
            jira_text += f"- {issue['key']}: {issue['summary']} (Status: {issue['status']})\n"
        
        prompt = f"""Analyze this incident and provide a structured report.

## Error Message
{error_message}

## Logs
{logs_text}

## Performance Metrics
- Avg duration: {metrics.get('average_duration_ms', 'N/A')}ms
- Total calls: {metrics.get('total_calls', 'N/A')}
- Error count: {metrics.get('error_count', 0)}

## Related Jira Issues
{jira_text}

Return ONLY valid JSON in this format:
{{
    "summary": "brief 1-sentence summary",
    "root_cause_analysis": "what likely caused this",
    "impact": "potential impact",
    "recommendations": ["rec1", "rec2", "rec3"],
    "related_issues": ["issue keys"]
}}"""
        
        response = await self._chat(prompt)
        
        # Parse JSON response
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {
            "summary": f"Incident: {error_message[:100]}",
            "root_cause_analysis": "Review logs for more details",
            "impact": "Service degradation possible",
            "recommendations": ["Check logs", "Review recent changes", "Monitor system"],
            "related_issues": []
        }
    
    async def _chat(self, user_message: str) -> str:
        """Send chat completion request to Groq."""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a technical incident analysis expert. Return ONLY valid JSON when requested."},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.3,
            "max_tokens": 500
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    logger.error(f"Groq API failed: {response.status_code}")
                    logger.error(f"Response: {response.text}")
                    return ""
                
                data = response.json()
                return data["choices"][0]["message"]["content"]
                
            except Exception as e:
                logger.error(f"Error calling Groq: {str(e)}")
                return ""


# At the bottom of llm_client.py, add:
from app.config import settings

# Create singleton instance
llm_client = LLMClient(
    api_key=settings.groq_api_key,
    model=settings.groq_model
)