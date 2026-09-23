from typing import Annotated

from app.controllers import ProductController as product_controller
from app.lib.passport.index import admin_authenticate
from app.types.productType import (
    ProductCreateRequest,
    ProductSearchQuery,
    ProductUpdateRequest,
)
from fastapi import APIRouter, Depends, status

router = APIRouter(tags=["Product"])


@router.get("")
async def listProducts(query: Annotated[ProductSearchQuery, Depends()]):
    return await product_controller.listProducts(query)


@router.get("/{product_id}")
async def getProduct(product_id: int):
    return await product_controller.getProduct(product_id)


@router.post("", status_code=status.HTTP_201_CREATED)
async def createProduct(
    body: ProductCreateRequest,
    _admin: Annotated[dict, Depends(admin_authenticate)],
):
    return await product_controller.createProduct(body)


@router.patch("/{product_id}")
async def updateProduct(
    product_id: int,
    body: ProductUpdateRequest,
    _admin: Annotated[dict, Depends(admin_authenticate)],
):
    return await product_controller.updateProduct(product_id, body)


@router.delete("/{product_id}")
async def deleteProduct(
    product_id: int,
    _admin: Annotated[dict, Depends(admin_authenticate)],
):
    return await product_controller.deleteProduct(product_id)
