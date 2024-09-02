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

    @Post("/webhook")
    async def webhook(self, request: Request):
        try:
            print(request)
            
            data = await request.json()
            
            await self.service.process_webhook_data(data)
            return {"message": "Webhook data processed successfully"}
        except Exception as e:
            logging.error(f"Error in webhook endpoint: {str(e)}")
            raise HTTPException(status_code=400, detail="Error processing webhook data")

    @Get("/trigger-daily-extraction")
    async def trigger_daily_extraction(self):
        try:
            await self.service.daily_extraction()
            return {"message": "Daily extraction triggered successfully"}
        except Exception as e:
            logging.error(f"Error triggering daily extraction: {str(e)}")
            raise HTTPException(status_code=500, detail="Error triggering daily extraction")
        