from nest.core import Controller, Get, Post, Depends
from .kobo_service import KoboService
from fastapi import HTTPException, Request
import logging
from src.database.models.kobo_data_model import KoboDataModel

@Controller("kobo")
class KoboController:
    service: KoboService = Depends(KoboService)

    @Get("/extract")
    async def extract_data(self):
        try:
            await self.service.extract_and_save_data()
            return {"message": "Data extraction completed successfully"}
        except Exception as e:
            logging.error(f"Error in extract_data endpoint: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error during data extraction")

    @Get("/webhook")
    async def trigger_daily_extraction(self):
        try:
            await self.service.auto_update_current_data()
            return {"message": "Daily extraction triggered successfully"}
        except Exception as e:
            logging.error(f"Error triggering daily extraction: {str(e)}")
            raise HTTPException(status_code=500, detail="Error triggering daily extraction")
        