from nest.core import App
from fastapi.middleware.cors import CORSMiddleware
from src.database.db import init_db
from src.logic.data_quality.data_quality_module import DataQualityModule
from src.logic.kobo.kobo_module import KoboModule
from src.logic.survey.survey_module import SurveyModule

app = App(
    description="KoboSync Data Extraction tool for Inkomoko",
    modules=[DataQualityModule, KoboModule, SurveyModule],
)

# Allow CORS for all domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    init_db()
