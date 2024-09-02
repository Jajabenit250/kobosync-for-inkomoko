from typing import Dict, List, Any
from nest.core import Controller, Get, Post, Depends
from .data_quality_service import DataQualityService
import logging
from src.database.models.data_quality_model import DataQualityCheckResponse, Summary, IssuesByType, IssuesByEntity, Issue

@Controller('data-quality')
class DataQualityController:
    service: DataQualityService = Depends(DataQualityService)

    @Post("/check")
    async def check_data_quality(self) -> DataQualityCheckResponse:
        try:
            result = await self.service.process_and_report()
            return DataQualityCheckResponse(
                message="Data quality check completed",
                summary=Summary(
                    total_issues=result["summary"]["total_issues"],
                    issues_by_type=IssuesByType(**result["summary"]["issues_by_type"]),
                    issues_by_entity=result["summary"]["issues_by_entity"]
                ),
                issues=IssuesByEntity(surveys=[Issue(**issue) for issue in result["issues"]["surveys"]])
            )
        except Exception as e:
            logging.error(f"Error in data quality check: {str(e)}")
            raise Exception("An error occurred during the data quality check")

        