from logging import debug
import uvicorn
from fastapi import FastAPI
from api.routes.api import router as api_router

from core.config import DEBUG, PROJECT_NAME, API_PREFIX, VERSION
def get_application() -> FastAPI:
    application = FastAPI(title=PROJECT_NAME, debug=DEBUG, version=VERSION)
    application.include_router(api_router, prefix=API_PREFIX)
    
    return application

app = get_application()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port = 8080, reload = False, debug = False)