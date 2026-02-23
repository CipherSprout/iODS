from contextlib import asynccontextmanager

from fastapi import FastAPI

from iods.api.routes import router
from iods.core.config import get_settings
from iods.core.logging import configure_logging
from iods.db.session import create_db_and_tables


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    create_db_and_tables()
    yield


app = FastAPI(title="iODS API", version="1.0.0", lifespan=lifespan)
app.include_router(router)
