from contextlib import asynccontextmanager

from app.lib.prisma import db as prisma
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.authRouter import router as authRouter

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not prisma.is_connected():
        await prisma.connect()
    yield
    if prisma.is_connected():
        await prisma.disconnect()


app = FastAPI(
    title="Trendy Shop API",
    description="쇼핑몰 백엔드 API입니다.",
    version="1.0.0",
    lifespan=lifespan,
)

origins = ["http://localhost:4000", "http://127.0.0.1:4000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(authRouter, prefix="/auth")


@app.get("/test")
def health_check():
    return {"status": "ok", "message": "FastAPI와 성공적으로 연결되었습니다!5222"}
