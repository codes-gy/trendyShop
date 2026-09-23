"use client";

import { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { PRODUCT_IMAGES } from "../lib/product-images";

// 가상의 상품 데이터 8개 배열 (map 문법으로 뿌려줄 예정)
const PRODUCTS = [
  {
    id: "1",
    image: PRODUCT_IMAGES.shirt,
    title: "린넨 오버사이즈 셔츠",
    price: 45000,
    tag: "NEW",
    color: "베이지",
    category: "상의",
  },
  {
    id: "2",
    image: PRODUCT_IMAGES.casualPants,
    title: "와이드 버뮤다 팬츠",
    price: 52000,
    tag: "BEST",
    color: "블랙",
    category: "하의",
  },
  {
    id: "3",
    image: PRODUCT_IMAGES.bag,
    title: "미니멀 크로스 레더백",
    price: 128000,
    tag: "",
    color: "브라운",
    category: "잡화",
  },
  {
    id: "4",
    image: PRODUCT_IMAGES.sneakers,
    title: "실버 버클 가죽 샌들",
    price: 69000,
    tag: "SALE",
    color: "실버",
    category: "잡화",
  },
  {
    id: "5",
    image: PRODUCT_IMAGES.denim,
    title: "소프트 세미와이드 데님",
    price: 49000,
    tag: "BEST",
    color: "연청",
    category: "하의",
  },
  {
    id: "6",
    image: PRODUCT_IMAGES.slacks,
    title: "카고 포켓 롱 스커트",
    price: 42000,
    tag: "",
    color: "카키",
    category: "하의",
  },
  {
    id: "7",
    image: PRODUCT_IMAGES.blouse,
    title: "스퀘어넥 슬리브리스 티",
    price: 24000,
    tag: "",
    color: "화이트",
    category: "상의",
  },
  {
    id: "8",
    image: PRODUCT_IMAGES.knit,
    title: "스트라이프 하프 니트",
    price: 38000,
    tag: "SALE",
    color: "네이비",
    category: "상의",
  },
];

const CATEGORY_FILTERS = ["전체", "상의", "하의", "아우터", "잡화"];
const SORT_OPTIONS = ["추천순", "신상품순", "낮은 가격순", "높은 가격순"] as const;

export default function ProductListPage() {
  const [activeCategory, setActiveCategory] = useState("전체");
  const [sortBy, setSortBy] = useState<(typeof SORT_OPTIONS)[number]>("추천순");

  const filteredProducts =
    activeCategory === "전체"
      ? PRODUCTS
      : PRODUCTS.filter((product) => product.category === activeCategory);

  const sortedProducts = [...filteredProducts].sort((a, b) => {
    if (sortBy === "신상품순") return Number(b.id) - Number(a.id);
    if (sortBy === "낮은 가격순") return a.price - b.price;
    if (sortBy === "높은 가격순") return b.price - a.price;
    return 0; // 추천순: 원본 순서 유지
  });

  return (
    // [1번 외벽 박스] 전체 배경 및 레이아웃 설정
    <div className="min-h-screen bg-zinc-50 font-sans text-zinc-900 antialiased">
      {/* [3번 메인 컨텐츠 영역] */}
      <main className="mx-auto max-w-6xl px-6 py-10">
        {/* 상단 타이틀 구역 */}
        <div className="mb-8 border-b border-zinc-200 pb-6">
          <h1 className="text-3xl font-black tracking-tight">모든 상품 보기</h1>
          <p className="mt-1.5 text-xs text-zinc-400">
            TRNDY가 제안하는 시즌 에센셜 컬렉션 ({sortedProducts.length})
          </p>
        </div>

        {/* 🧭 컨트롤러 바: 필터 버튼 및 정렬 순서 선택 구역 */}
        <div className="mb-6 flex items-center justify-between text-sm">
          {/* 왼쪽: 빠른 카테고리 필터 칩 (가로 정렬 flex) */}
          <div className="scrollbar-hide flex space-x-2 overflow-x-auto">
            {CATEGORY_FILTERS.map((category) => (
              <button
                key={category}
                onClick={() => setActiveCategory(category)}
                className={`cursor-pointer rounded-full px-4 py-2 text-xs font-semibold whitespace-nowrap transition ${
                  activeCategory === category
                    ? "bg-zinc-950 text-white"
                    : "border border-zinc-200 bg-white text-zinc-600 hover:border-zinc-400"
                }`}
              >
                {category}
              </button>
            ))}
          </div>

          {/* 오른쪽: 정렬 기준 드롭다운 선택상자 */}
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as (typeof SORT_OPTIONS)[number])}
            className="cursor-pointer rounded-xl border border-zinc-200 bg-white px-3 py-2 text-xs font-medium text-zinc-600 focus:border-zinc-400 focus:outline-none"
          >
            {SORT_OPTIONS.map((option) => (
              <option key={option}>{option}</option>
            ))}
          </select>
        </div>

        {/* 🛍️ 상품 배치 격자판 (Grid) 구역 */}
        {/* 모바일 2열(grid-cols-2), 태블릿 3열(sm:), 데스크탑 4열(md:) 반응형 완벽 대응 */}
        <div className="grid grid-cols-2 gap-x-4 gap-y-10 sm:grid-cols-3 md:grid-cols-4">
          {/* 자바스크립트 map 함수로 상품 리스트 자동 나열 */}
          {sortedProducts.map((product) => (
            <Link
              key={product.id}
              href={`/product/${product.id}`}
              className="group relative block cursor-pointer"
            >
              {/* 상품 이미지 박스 */}
              <div className="relative mb-3.5 flex aspect-[3/4] items-center justify-center overflow-hidden rounded-2xl bg-zinc-200">
                <Image
                  src={product.image}
                  alt={product.title}
                  fill
                  className="object-cover transition duration-500 group-hover:scale-105"
                />

                {/* 좌상단 상태 배지 (NEW, BEST, SALE) */}
                {product.tag && (
                  <span
                    className={`absolute top-3 left-3 z-10 rounded-md px-2 py-1 text-[9px] font-black tracking-wider text-white ${
                      product.tag === "SALE" ? "bg-red-500" : "bg-zinc-950"
                    }`}
                  >
                    {product.tag}
                  </span>
                )}
              </div>

              {/* 상품 텍스트 정보 정보 */}
              <div className="space-y-1">
                <p className="text-[11px] font-medium text-zinc-400">{product.color}</p>
                <h3 className="truncate text-sm font-medium text-zinc-700 transition group-hover:text-zinc-950">
                  {product.title}
                </h3>
                <p className="text-sm font-bold text-zinc-950">
                  {product.price.toLocaleString()}원
                </p>
              </div>
            </Link>
          ))}
        </div>

        {sortedProducts.length === 0 && (
          <p className="py-16 text-center text-sm text-zinc-400">
            해당 카테고리에 상품이 없습니다.
          </p>
        )}

        {/* 🔄 하단 페이지네이션 / 더보기 버튼 */}
        {/* TODO: 실제 상품이 8개뿐이라 페이지네이션 데이터가 없음. 상품 수가 늘어나면 연결 예정 */}
        <div className="mt-20 flex justify-center">
          <button className="cursor-pointer rounded-xl border border-zinc-200 bg-white px-8 py-3.5 text-xs font-semibold text-zinc-700 shadow-sm transition duration-200 hover:border-zinc-950 hover:text-zinc-950">
            더보기 (1 / 3) 🔽
          </button>
        </div>
      </main>
    </div>
  );
}
