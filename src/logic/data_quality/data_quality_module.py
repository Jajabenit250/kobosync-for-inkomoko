# data_quality_module.py
from .data_quality_service import DataQualityService
from .data_quality_controller import DataQualityController

class DataQualityModule:
    def __init__(self):
        self.providers = [DataQualityService]
        self.controllers = [DataQualityController]
        