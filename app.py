from nest.core import App
from fastapi.middleware.cors import CORSMiddleware
from src.database.db import init_db
from src.logic.survey.survey_module import SurveyModule

app = App(
    description="KoboTool Data Sync For Inkomoko APIs",
    modules=[SurveyModule],
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
