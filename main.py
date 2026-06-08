from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import text

from routes.auth_routes import router as auth_router
from routes.invoice_routes import router as invoice_router

from database import engine, Base
from db_models import User


app = FastAPI(title="SquilsScanner Invoice OCR API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)


app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Auth"]
)

app.include_router(
    invoice_router,
    prefix="/invoice",
    tags=["Invoice OCR"]
)


@app.get("/")
def home():
    return {
        "message": "SquilsScanner API is running"
    }


@app.get("/db-test")
def db_test():

    try:
        with engine.connect() as connection:

            result = connection.execute(
                text("SELECT 1")
            )

            value = result.scalar()

        return {
            "status": "success",
            "database": "connected",
            "result": value
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }
