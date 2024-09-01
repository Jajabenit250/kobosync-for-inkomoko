import aiohttp
import asyncio
from typing import Dict, List, Any
import logging

class KoboDataService:
    BASE_URL = "https://kf.kobotoolbox.org/api/v2/assets/aW9w8jHjn4Cj8SSQ5VcojK/data.json"
    HEADERS = {
        "Authorization": "Token f24b97a52f76779e97b0c10f80406af5e9590eaf",
        "Cookie": "django_language=en"
    }

    async def fetch_kobo_data(self, page_size: int = 100) -> List[Dict[str, Any]]:
        all_results = []
        async with aiohttp.ClientSession() as session:
            url = f"{self.BASE_URL}?limit={page_size}"
            while url:
                try:
                    async with session.get(url, headers=self.HEADERS) as response:
                        response.raise_for_status()
                        data = await response.json()
                        all_results.extend(data.get('results', []))
                        url = data.get('next')
                except aiohttp.ClientError as e:
                    logging.error(f"Error fetching data from KoboToolbox: {str(e)}")
                    raise
        return all_results
    