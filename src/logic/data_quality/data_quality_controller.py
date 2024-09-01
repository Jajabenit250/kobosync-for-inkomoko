from typing import Dict, List, Any
from nest.core import Controller, Get, Post, Depends
from .data_quality_service import DataQualityService
import logging

@Controller('data-quality')
class DataQualityController:
    service: DataQualityService = Depends(DataQualityService)

    @Post("/check")
    async def check_data_quality(self, data: Dict[str, List[Dict[str, Any]]]):
        try:
            issues = self.service.check_all(data)
            summary = self.service.generate_summary(issues)
            
            # Save issues to the database
            await self.service.save_issues_to_db(issues)
            
            return {
                "message": "Data quality check completed and issues saved to the database",
                "summary": summary,
                "issues": issues
            }
        except Exception as e:
            logging.error(f"Error in data quality check: {str(e)}")
            raise Exception("An error occurred during the data quality check")

    @Get("/issues")
    async def get_issues(self, entity_type: str = None, issue_type: str = None, limit: int = 100, offset: int = 0):
        total, issues = await self.service.get_issues(entity_type, issue_type, limit, offset)
        return {
            "total": total,
            "issues": issues
        }

    @Get("/summary")
    async def get_summary(self):
        return await self.service.get_summary()
    