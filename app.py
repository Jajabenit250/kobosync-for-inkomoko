from src.common.utils.config import initialize_clickhouse
from nest.core import App
from fastapi.middleware.cors import CORSMiddleware
# import aioredis

app = App(
    description="KoboTool Data Sync For Inkomoko APIs",
    modules=[],
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
    initialize_clickhouse()
