from app.services import ProductService as productService
from app.types.productType import (
    ProductCreateRequest,
    ProductSearchQuery,
    ProductUpdateRequest,
)


async def listProducts(query: ProductSearchQuery):
    # 상품 목록 조회

    data = await productService.listProducts(query)
    return {
        "success": True,
        "message": "상품 목록 조회에 성공했습니다.",
        "data": data,
    }


async def getProduct(product_id: int):
    # 상품 상세 조회

    data = await productService.getProduct(product_id)
    return {
        "success": True,
        "message": "상품 조회에 성공했습니다.",
        "data": data,
    }


async def createProduct(body: ProductCreateRequest):
    # 상품 신규 등록

    data = await productService.createProduct(body)
    return {
        "success": True,
        "message": "상품이 성공적으로 등록되었습니다.",
        "data": data,
    }


async def updateProduct(product_id: int, body: ProductUpdateRequest):
    # 상품 정보 수정

    data = await productService.updateProduct(product_id, body)
    return {
        "success": True,
        "message": "상품 정보가 성공적으로 수정되었습니다.",
        "data": data,
    }


async def deleteProduct(product_id: int):
    # 상품 삭제 (소프트 딜리트)

    await productService.deleteProduct(product_id)
    return {
        "success": True,
        "message": "상품이 삭제되었습니다.",
    }
