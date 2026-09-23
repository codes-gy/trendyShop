from contextlib import asynccontextmanager

from app.errors.customError import init_exception_handlers
from app.lib.prisma import db as prisma
from app.routers.authRouter import router as authRouter
from app.routers.cartRouter import router as cartRouter
from app.routers.orderRouter import router as orderRouter
from app.routers.productRouter import router as productRouter
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

init_exception_handlers(app)

origins = ["http://localhost:4000", "http://127.0.0.1:4000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(authRouter, prefix="/auth")
app.include_router(productRouter, prefix="/products")
app.include_router(cartRouter, prefix="/cart")
app.include_router(orderRouter, prefix="/orders")


@app.get("/test")
def health_check():
    return {"status": "ok", "message": "FastAPI와 성공적으로 연결되었습니다!5222"}
