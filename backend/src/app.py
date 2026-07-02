from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from backend.src.config.database import Base, engine
from backend.src.domain.exceptions import AppError

# IMPORT MODELS (QUAN TRỌNG)
import backend.src.models.auth
import backend.src.models.enterprise
import backend.src.models.category
import backend.src.models.project
import backend.src.models.proposal
import backend.src.models.review
import backend.src.models.expert

# ROUTER TỔNG
from backend.src.presentation import router


app = FastAPI(
    title="AITasker Backend",
    version="1.0.0"
)


# STATIC
app.mount("/static", StaticFiles(directory="static"), name="static")


# SESSION
app.add_middleware(
    SessionMiddleware,
    secret_key="change-me"
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ERROR HANDLER
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


# ROUTER
app.include_router(router)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Backend running"}