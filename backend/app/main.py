from contextlib import asynccontextmanager

from app.lib.prisma import db as prisma
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


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


@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "FastAPI와 성공적으로 연결되었습니다!5222"}


# backend/app/main.py 에 추가


@app.get("/api/products")
def get_products():
    return [
        {
            "id": 1,
            "name": "시그니처 오버핏 코튼 셔츠",
            "price": 59000,
            "category": "NEW",
            "image": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=500&auto=format&fit=crop",
            "isSale": True,
            "discount": 15,
        },
        {
            "id": 2,
            "name": "클래식 와이드 데님 팬츠",
            "price": 78000,
            "category": "SHOP",
            "image": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=500&auto=format&fit=crop",
            "isSale": False,
            "discount": 0,
        },
        {
            "id": 3,
            "name": "미니멀 레더 백팩",
            "price": 145000,
            "category": "COLLECTION",
            "image": "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=500&auto=format&fit=crop",
            "isSale": False,
            "discount": 0,
        },
        {
            "id": 4,
            "name": "어반 스웨이드 스니커즈",
            "price": 112000,
            "category": "NEW",
            "image": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=500&auto=format&fit=crop",
            "isSale": True,
            "discount": 20,
        },
    ]
