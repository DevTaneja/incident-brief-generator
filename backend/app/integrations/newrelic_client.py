"""
New Relic Client - Fetch metrics using NRQL
"""

import httpx
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class NewRelicClient:
    """
    Client for New Relic GraphQL API.
    """
    
    def __init__(self, api_key: str, account_id: str):
        self.api_key = api_key
        self.account_id = account_id
        self.graphql_url = "https://api.newrelic.com/graphql"
    
    async def query_nrql(self, nrql: str) -> List[Dict[str, Any]]:
        """
        Execute a NRQL query using GraphQL.
        """
        graphql_query = {
            "query": f"""
            {{
              actor {{
                account(id: {self.account_id}) {{
                  nrql(query: "{nrql}") {{
                    results
                  }}
                }}
              }}
            }}
            """
        }
        
        headers = {
            "Api-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.graphql_url,
                headers=headers,
                json=graphql_query,
                timeout=30.0
            )
            
            if response.status_code != 200:
                logger.error(f"New Relic query failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return []
            
            data = response.json()
            
            if "errors" in data:
                logger.error(f"GraphQL errors: {data['errors']}")
                return []
            
            try:
                results = data["data"]["actor"]["account"]["nrql"]["results"]
                return results
            except (KeyError, TypeError) as e:
                logger.error(f"Unexpected response format: {e}")
                return []
    
    def _convert_time_range(self, time_range: str) -> str:
        """
        Convert time_range (e.g., "10m", "1h", "1d") to New Relic format.
        "10m" -> "10 minutes"
        "1h" -> "1 hour"
        "1d" -> "1 day"
        """
        time_value = int(time_range[:-1])
        time_unit = time_range[-1]
        
        unit_map = {
            'm': 'minutes',
            'h': 'hours',
            'd': 'days'
        }
        
        # Handle singular vs plural
        if time_value == 1:
            unit_map['h'] = 'hour'
            unit_map['d'] = 'day'
        
        return f"{time_value} {unit_map[time_unit]}"
    
    async def get_transactions_for_request(
        self, 
        request_id: str, 
        time_range: str
    ) -> Dict[str, Any]:
        """
        Get transaction metrics for a specific requestId.
        """
        nrql_time = self._convert_time_range(time_range)
        
        nrql = f"SELECT average(duration), max(duration), count(*) FROM Transaction WHERE requestId = '{request_id}' SINCE {nrql_time} ago"
        
        logger.info(f"Querying New Relic for request_id={request_id}")
        
        results = await self.query_nrql(nrql)
        
        if not results or not results[0]:
            return {
                "request_id": request_id,
                "found": False,
                "message": "No transactions found"
            }
        
        result = results[0]
        
        return {
            "request_id": request_id,
            "found": True,
            "average_duration_ms": result.get("average.duration"),
            "max_duration_ms": result.get("max.duration"),
            "total_calls": result.get("count"),
            "time_range": time_range
        }
    
    async def get_error_count(
        self, 
        request_id: str, 
        time_range: str
    ) -> int:
        """
        Get error count for transactions with this requestId.
        """
        nrql_time = self._convert_time_range(time_range)
        
        nrql = f"SELECT count(*) FROM Transaction WHERE requestId = '{request_id}' AND error IS TRUE SINCE {nrql_time} ago"
        
        results = await self.query_nrql(nrql)
        
        if not results or not results[0]:
            return 0
        
        return results[0].get("count", 0)