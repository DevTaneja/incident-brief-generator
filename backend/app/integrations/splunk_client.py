"""
Splunk Search Client - Production with configurable wait
"""

import httpx
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
import logging
import asyncio
import json
import os

logger = logging.getLogger(__name__)


class SplunkSearchClient:
    
    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.base_url = f"https://{host}:{port}"
        self.verify_ssl = False
        self.session_key = None
        # Make wait time configurable via environment variable
        self.wait_seconds = float(os.getenv("SPLUNK_SEARCH_WAIT", "2"))
    
    async def _get_session_key(self) -> str:
        async with httpx.AsyncClient(verify=self.verify_ssl) as client:
            response = await client.post(
                f"{self.base_url}/services/auth/login",
                data={"username": self.username, "password": self.password},
                timeout=10.0
            )
            if response.status_code != 200:
                raise Exception(f"Auth failed: {response.status_code}")
            root = ET.fromstring(response.text)
            return root.find("sessionKey").text
    
    async def search_by_request_id(
        self, 
        request_id: str, 
        time_range: str,
        index: str = "main"
    ) -> List[Dict[str, Any]]:
        
        if not self.session_key:
            self.session_key = await self._get_session_key()
        
        query = f'search index="{index}" requestId="{request_id}"'
        earliest_time = f"-{time_range}"
        
        async with httpx.AsyncClient(verify=self.verify_ssl) as client:
            headers = {"Authorization": f"Splunk {self.session_key}"}
            
            response = await client.post(
                f"{self.base_url}/services/search/jobs",
                data={"search": query, "earliest_time": earliest_time, "latest_time": "now"},
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code != 201:
                logger.error(f"Job creation failed: {response.status_code}")
                return []
            
            root = ET.fromstring(response.text)
            job_id = root.find("sid").text
            logger.info(f"Created job: {job_id}, waiting {self.wait_seconds}s")
            
            # Configurable wait time (2 seconds default, increase for larger searches)
            await asyncio.sleep(self.wait_seconds)
            
            results_response = await client.get(
                f"{self.base_url}/services/search/jobs/{job_id}/results",
                params={"output_mode": "json"},
                headers=headers,
                timeout=30.0
            )
            
            if results_response.status_code != 200:
                logger.error(f"Failed to get results: {results_response.status_code}")
                return []
            
            data = results_response.json()
            results = data.get("results", [])
            
            parsed_results = []
            for result in results:
                raw = result.get("_raw")
                if raw:
                    try:
                        parsed = json.loads(raw)
                        parsed_results.append(parsed)
                    except json.JSONDecodeError:
                        parsed_results.append({"_raw": raw})
            
            logger.info(f"Found {len(parsed_results)} logs")
            return parsed_results