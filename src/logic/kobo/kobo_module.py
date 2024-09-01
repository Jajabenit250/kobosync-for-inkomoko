from .kobo_service import KoboService
from .kobo_controller import KoboController

class KoboModule:
    def __init__(self):
        self.providers = [KoboService]
        self.controllers = [KoboController]
        