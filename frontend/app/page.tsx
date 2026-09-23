"use client";

import { useState } from "react";
import Image from "next/image";
import Link from "next/link";

// 가짜 상품 데이터
const MEGASHOP_PRODUCTS = [
  {
    id: 1,
    name: "시그니처 오버핏 코튼 셔츠",
    price: 59000,
    category: "NEW",
    image:
      "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=500&auto=format&fit=crop",
    isSale: true,
    discount: 15,
    tag: "BEST",
    desc: "이집트산 프리미엄 코튼 100%로 짜여진 유려한 피팅감",
  },
  {
    id: 2,
    name: "클래식 와이드 데님 팬츠",
    price: 78000,
    category: "DENIM",
    image:
      "https://images.unsplash.com/photo-1542272604-787c3835535d?w=500&auto=format&fit=crop",
    isSale: false,
    discount: 0,
    tag: "ESSENTIAL",
    desc: "14온스 링방적 하이엔드 셀비지 데님 라인",
  },
  {
    id: 3,
    name: "미니멀 레더 바디 백팩",
    price: 145000,
    category: "BAG",
    image:
      "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=500&auto=format&fit=crop",
    isSale: false,
    discount: 0,
    tag: "MD PICK",
    desc: "이탈리아 풀그레인 레더를 가공한 시크한 실루엣",
  },
  {
    id: 4,
    name: "어반 스웨이드 스니커즈",
    price: 112000,
    category: "SHOES",
    image:
      "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=500&auto=format&fit=crop",
    isSale: true,
    discount: 20,
    tag: "LOW STOCK",
    desc: "천연 화강암 스웨이드 텍스처와 인체공학 아웃솔",
  },
  {
    id: 5,
    name: "파인 울 라운드 니트 웨어",
    price: 89000,
    category: "KNIT",
    image:
      "https://images.unsplash.com/photo-1614975058789-41316d0e2e9c?w=500&auto=format&fit=crop",
    isSale: true,
    discount: 10,
    tag: "NEW",
    desc: "메리노 울 본연의 보온성과 구름 같은 원사 마감",
  },
  {
    id: 6,
    name: "워시드 카펜터 나일론 팬츠",
    price: 69000,
    category: "BOTTOM",
    image:
      "https://images.unsplash.com/photo-1517423738875-5ce310acd3da?w=500&auto=format&fit=crop",
    isSale: false,
    discount: 0,
    tag: "TREND",
    desc: "밀리터리 테크웨어에서 영감을 얻은 고밀도 나일론",
  },
  {
    id: 7,
    name: "모던 실루엣 투버튼 재킷",
    price: 189000,
    category: "OUTER",
    image:
      "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=500&auto=format&fit=crop",
    isSale: false,
    discount: 0,
    tag: "PRE-ORDER",
    desc: "어깨선부터 툭 떨어지는 입체적 3D 테일러드 공정",
  },
  {
    id: 8,
    name: "스테디 크루넥 스웨트셔츠",
    price: 45000,
    category: "TOP",
    image:
      "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=500&auto=format&fit=crop",
    isSale: true,
    discount: 30,
    tag: "SEASON OFF",
    desc: "중량감 있는 헤비웨이트 프렌치 테리 코튼 원단",
  },
  {
    id: 9,
    name: "실크 블렌드 시어 블라우스",
    price: 95000,
    category: "NEW",
    image:
      "https://images.unsplash.com/photo-1603252109303-2751441dd157?w=500&auto=format&fit=crop",
    isSale: false,
    discount: 0,
    tag: "ELEGANT",
    desc: "은은한 내추럴 광택감이 감도는 시스루 포멀 텍스처",
  },
  {
    id: 10,
    name: "어반 테이퍼드 치노 슬랙스",
    price: 62000,
    category: "BOTTOM",
    image:
      "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=500&auto=format&fit=crop",
    isSale: true,
    discount: 15,
    tag: "STEADY",
    desc: "링클프리 코팅 가공으로 하루 종일 칼핏 유지",
  },
  {
    id: 11,
    name: "비건 레더 미니멀 보스턴백",
    price: 168000,
    category: "BAG",
    image:
      "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500&auto=format&fit=crop",
    isSale: false,
    discount: 0,
    tag: "HIGH-END",
    desc: "스크래치에 강한 프리미엄 친환경 마이크로파이버 가죽",
  },
  {
    id: 12,
    name: "모노크롬 가디건 크롭 베스트",
    price: 53000,
    category: "KNIT",
    image:
      "https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=500&auto=format&fit=crop",
    isSale: true,
    discount: 25,
    tag: "LAST PIECE",
    desc: "유니크한 비대칭 클로징 단추 포인트 레이어드 아이템",
  },
];

// 소셜 룩북용 고해상도 무드 피드 이미지 리스트
const INSTA_FEEDS = [
  "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=400&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1483985988355-763728e1935b?w=400&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1485968579580-b6d095142e6e?w=400&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=400&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1539109136881-3be0616acf4b?w=400&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1509631179647-0177331693ae?w=400&auto=format&fit=crop",
];

export default function HomePage() {
  const [activeTab, setActiveTab] = useState("ALL PRODUCTS");
  const [journalIndex, setJournalIndex] = useState(0);

  const CATEGORY_FILTERS: Record<string, string[]> = {
    "ALL PRODUCTS": [],
    NEW: ["NEW"],
    DENIM: ["DENIM"],
    KNIT: ["KNIT"],
    "BAG & SHOES": ["BAG", "SHOES"],
  };

  const filteredProducts =
    activeTab === "ALL PRODUCTS"
      ? MEGASHOP_PRODUCTS
      : MEGASHOP_PRODUCTS.filter((product) =>
          CATEGORY_FILTERS[activeTab]?.includes(product.category),
        );

  const journals = [
    {
      title: "The Art of Layering",
      phrase: "가벼운 린넨과 실크 텍스처를 믹스하여 표현하는 맑은 여름철 레이어링 룰.",
      img: "https://images.unsplash.com/photo-1509631179647-0177331693ae?w=800&auto=format&fit=crop",
    },
    {
      title: "Pure Silence Denim",
      phrase:
        "워싱 공정을 최소화하여 환경 손상을 줄이고 생지 고유의 깊은 컬러감을 복원한 프로젝트.",
      img: "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=800&auto=format&fit=crop",
    },
    {
      title: "Objects of Desire",
      phrase:
        "단순히 액세서리라 칭하기엔 아까운, 은은한 실버 본연의 조형미를 지닌 주얼리 오브제들.",
      img: "https://images.unsplash.com/photo-1617038260897-41a1f14a8ca0?w=800&auto=format&fit=crop",
    },
  ];

  return (
    <div className="min-h-screen bg-zinc-50 font-sans text-zinc-900 antialiased selection:bg-zinc-900 selection:text-white">
      {/* 대형 시네마틱 히어로 섹션 */}
      <section className="mx-auto max-w-7xl px-4 pt-6 md:px-8 md:pt-8">
        <div className="relative flex min-h-[480px] flex-col justify-end overflow-hidden rounded-3xl bg-zinc-950 px-5 py-10 text-white shadow-lg md:min-h-[650px] md:rounded-[32px] md:px-16 md:py-24">
          <div className="absolute inset-0 z-10 bg-gradient-to-t from-zinc-950 via-zinc-950/50 to-zinc-950/10" />
          <Image
            src="https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=1800&auto=format&fit=crop"
            alt="Mega Main Banner"
            fill
            priority
            className="scale-105 object-cover object-center opacity-65 transition duration-[2000ms] hover:scale-100"
          />

          <div className="relative z-20 max-w-3xl space-y-4 md:space-y-5">
            <div className="inline-flex items-center space-x-2 rounded-full border border-white/20 bg-black/40 px-3 py-1 text-[10px] font-black tracking-widest text-white uppercase backdrop-blur-md">
              <span className="h-1.5 w-1.5 animate-ping rounded-full bg-emerald-400" />
              <span>2026 SUMMER CAMPAIGN LIVE</span>
            </div>
            <h2 className="text-4xl leading-[1.05] font-black tracking-tight md:text-7xl md:leading-none md:tracking-tighter">
              POETRY IN
              <br />
              SILHOUETTE
            </h2>
            <p className="max-w-xl text-sm leading-relaxed font-light text-zinc-300 md:text-lg">
              직조의 밀도가 자아내는 침묵의 우아함. 가벼운 여름 바람을 통과시키는 시어링
              레이어와 미니멀리즘 아키텍처에서 조형적 힌트를 얻은 컬렉션.
            </p>
            <div className="flex flex-col gap-3 pt-4 sm:flex-row sm:flex-wrap">
              <Link
                href="/product"
                className="rounded-full bg-white px-8 py-4 text-center text-xs font-black tracking-widest text-zinc-950 shadow-2xl transition duration-300 hover:bg-zinc-200"
              >
                EXPLORE NEW IN
              </Link>
              {/* TODO: 캠페인 필름 영상 콘텐츠가 아직 없어서 다음 단계에서 연결 예정 */}
              <button className="rounded-full border border-white/30 bg-white/5 px-8 py-4 text-center text-xs font-black tracking-widest text-white backdrop-blur-md transition duration-300 hover:bg-white/10">
                WATCH CAMPAIGN FILM
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* 3단 비대칭 비주얼 그리드 */}
      <section className="mx-auto max-w-7xl space-y-6 px-6 pt-24 md:px-8">
        <div className="text-center md:text-left">
          <h3 className="text-xs font-black tracking-widest text-zinc-400 uppercase">
            Season Vibe
          </h3>
          <h2 className="mt-1 text-2xl font-black tracking-tight text-zinc-950">
            SUMMER EDITORIAL VISUAL WALL
          </h2>
        </div>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div className="group relative h-[450px] cursor-pointer overflow-hidden rounded-3xl shadow-sm md:col-span-2">
            <div className="absolute inset-0 z-10 bg-gradient-to-t from-black/70 via-transparent to-transparent" />
            <Image
              src="https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=1000&auto=format&fit=crop"
              alt="Ed 1"
              fill
              className="object-cover transition duration-700 group-hover:scale-103"
            />
            <div className="absolute bottom-6 left-6 z-20 space-y-1 text-white">
              <span className="text-[10px] font-bold tracking-widest text-zinc-300">
                LOOKBOOK VOL.42
              </span>
              <h4 className="text-xl font-bold">자유를 대변하는 릴렉스드 피팅 모션</h4>
            </div>
          </div>
          <div className="grid grid-rows-2 gap-4">
            <div className="group relative h-[218px] cursor-pointer overflow-hidden rounded-3xl shadow-sm">
              <div className="absolute inset-0 z-10 bg-black/30 transition group-hover:bg-black/40" />
              <Image
                src="https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=500&auto=format&fit=crop"
                alt="Ed 2"
                fill
                className="object-cover transition duration-700 group-hover:scale-105"
              />
              <div className="absolute inset-0 z-20 flex items-center justify-center text-center text-xs font-bold tracking-widest text-white uppercase">
                Summer Suiting
              </div>
            </div>
            <div className="group relative h-[218px] cursor-pointer overflow-hidden rounded-3xl shadow-sm">
              <div className="absolute inset-0 z-10 bg-black/30 transition group-hover:bg-black/40" />
              <Image
                src="https://images.unsplash.com/photo-1485968579580-b6d095142e6e?w=500&auto=format&fit=crop"
                alt="Ed 3"
                fill
                className="object-cover transition duration-700 group-hover:scale-105"
              />
              <div className="absolute inset-0 z-20 flex items-center justify-center text-center text-xs font-bold tracking-widest text-white uppercase">
                Sand Dune Palette
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 순위형 대형 스탠드 바 */}
      <section className="mx-auto max-w-7xl space-y-8 px-6 pt-24 md:px-8">
        <div className="border-b border-zinc-200 pb-4 text-center">
          <h3 className="text-2xl font-black tracking-tighter text-zinc-950">
            REALTIME THE BEST 3
          </h3>
          <p className="mt-1 text-xs text-zinc-500">
            현재 TRNDY에서 단 한 시간 동안 가장 폭발적으로 판매된 시그니처 톱 티어
            삼인방
          </p>
        </div>
        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          {MEGASHOP_PRODUCTS.slice(0, 3).map((prod, i) => (
            <Link
              key={prod.id}
              href={`/product/${prod.id}`}
              className="flex items-center space-x-4 rounded-3xl border border-zinc-100 bg-white p-5 shadow-sm transition hover:shadow-md"
            >
              <span className="w-8 text-center text-4xl font-black tracking-tighter text-zinc-200 italic">
                0{i + 1}
              </span>
              <div className="relative h-24 w-24 flex-shrink-0 overflow-hidden rounded-xl bg-zinc-100">
                <Image
                  src={prod.image}
                  alt={prod.name}
                  fill
                  className="object-cover object-center"
                />
              </div>
              <div className="min-w-0 flex-1 space-y-1">
                <span className="text-[10px] font-black tracking-wider text-rose-500 uppercase">
                  {prod.tag}
                </span>
                <h4 className="truncate text-xs font-bold text-zinc-800">
                  {prod.name}
                </h4>
                <p className="line-clamp-1 text-xs font-light text-zinc-400">
                  {prod.desc}
                </p>
                <div className="pt-1 text-xs font-black text-zinc-950">
                  {prod.price.toLocaleString()}원
                </div>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* 대형 타임세일 컴포넌트 */}
      <section className="mx-auto max-w-7xl px-6 pt-24 md:px-8">
        <div className="flex flex-col items-center justify-between gap-6 rounded-[36px] bg-gradient-to-r from-rose-900 to-zinc-900 p-8 text-white shadow-xl md:flex-row md:p-12">
          <div className="space-y-2 text-center md:text-left">
            <span className="inline-block rounded bg-rose-600 px-2 py-0.5 text-[9px] font-bold tracking-widest uppercase">
              LIMITED TIME ONLY
            </span>
            <h3 className="text-2xl font-black tracking-tight md:text-4xl">
              FLASH SALE: 아웃렛 미드 시즌 오프
            </h3>
            <p className="text-xs font-light text-zinc-300 md:text-sm">
              본 팝업 배너에 기재된 품목은 재고 소진 시 전량 조기 마감 및 정가 환원
              처리됩니다.
            </p>
          </div>
          <div className="flex flex-wrap items-center justify-center gap-4">
            <div className="flex space-x-2 text-center">
              <div className="w-14 rounded-xl bg-white/10 p-3 backdrop-blur-sm">
                <span className="block text-lg font-black">02</span>
                <span className="text-[9px] font-bold text-zinc-400 uppercase">HR</span>
              </div>
              <div className="w-14 rounded-xl bg-white/10 p-3 backdrop-blur-sm">
                <span className="block text-lg font-black">41</span>
                <span className="text-[9px] font-bold text-zinc-400 uppercase">
                  MIN
                </span>
              </div>
              <div className="w-14 rounded-xl bg-white/10 p-3 backdrop-blur-sm">
                <span className="block text-lg font-black">58</span>
                <span className="text-[9px] font-bold text-zinc-400 uppercase">
                  SEC
                </span>
              </div>
            </div>
            <Link
              href="/product"
              className="rounded-full bg-white px-6 py-4 text-xs font-black tracking-widest text-zinc-900 shadow-md transition hover:bg-zinc-100"
            >
              SHOP NOW →
            </Link>
          </div>
        </div>
      </section>

      {/* 메인 코어 상품  */}
      <main className="mx-auto max-w-7xl space-y-8 px-6 py-24 md:px-8">
        <div className="flex flex-col space-y-3 border-b border-zinc-200 pb-6 md:flex-row md:items-end md:justify-between">
          <div>
            <h3 className="text-3xl font-black tracking-tighter text-zinc-950">
              COLLECTION ITEMS
            </h3>
            <p className="mt-1 text-xs text-zinc-500">
              오직 TRNDY 리미티드 패키지 라인으로 구성된 고해상도 아카이브 아이템
              전체보기
            </p>
          </div>

          <div className="flex space-x-2 overflow-x-auto pt-4 md:pt-0">
            {["ALL PRODUCTS", "NEW", "DENIM", "KNIT", "BAG & SHOES"].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`rounded-full px-4 py-1.5 text-xs font-bold tracking-wider whitespace-nowrap transition ${
                  activeTab === tab
                    ? "bg-zinc-950 text-white shadow-md"
                    : "bg-zinc-200/50 text-zinc-500 hover:bg-zinc-200"
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>

        {/* 12개 대용량 마스터 격자 그리드 */}
        <div className="grid grid-cols-1 gap-x-6 gap-y-16 sm:grid-cols-2 lg:grid-cols-4">
          {filteredProducts.map((product) => (
            <Link
              key={product.id}
              href={`/product/${product.id}`}
              className="group relative block cursor-pointer"
            >
              <div className="relative aspect-[3/4] w-full overflow-hidden rounded-3xl bg-zinc-100 shadow-sm transition-all duration-500 group-hover:shadow-md">
                <Image
                  src={product.image}
                  alt={product.name}
                  fill
                  className="object-cover object-center transition duration-1000 group-hover:scale-103"
                />
                <span className="absolute top-4 left-4 rounded-md bg-zinc-950/80 px-2 py-0.5 text-[9px] font-bold tracking-widest text-white uppercase shadow-sm backdrop-blur-sm">
                  {product.tag}
                </span>
                {product.isSale && (
                  <span className="absolute top-4 right-4 animate-pulse rounded-md bg-rose-600 px-2 py-0.5 text-[9px] font-bold text-white shadow-sm">
                    {product.discount}% SALE
                  </span>
                )}
              </div>

              <div className="mt-4 space-y-1 px-1">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-black tracking-widest text-zinc-400 uppercase">
                    {product.category}
                  </span>
                </div>
                <h4 className="line-clamp-1 text-sm font-bold text-zinc-800 transition group-hover:text-black">
                  {product.name}
                </h4>
                <p className="line-clamp-1 text-xs leading-normal font-light text-zinc-400">
                  {product.desc}
                </p>
                <div className="flex items-center space-x-2 pt-1">
                  <span className="text-sm font-black text-zinc-950">
                    {product.isSale
                      ? (product.price * (1 - product.discount / 100)).toLocaleString()
                      : product.price.toLocaleString()}
                    원
                  </span>
                  {product.isSale && (
                    <span className="text-xs font-normal text-zinc-400 line-through">
                      {product.price.toLocaleString()}원
                    </span>
                  )}
                </div>
              </div>
            </Link>
          ))}
        </div>
        {filteredProducts.length === 0 && (
          <p className="py-16 text-center text-sm text-zinc-400">
            해당 카테고리에 상품이 없습니다.
          </p>
        )}
      </main>

      {/* 인터랙티브 기획 매거진 슬롯 */}
      <section className="mx-auto max-w-7xl px-6 pb-24 md:px-8">
        <div className="grid grid-cols-1 items-center gap-12 rounded-[40px] bg-zinc-100 p-8 md:grid-cols-2 md:p-16">
          <div className="space-y-6">
            <div className="space-y-1">
              <span className="text-[10px] font-black tracking-widest text-zinc-400 uppercase">
                Interactive Magazine
              </span>
              <h3 className="text-3xl font-black tracking-tighter text-zinc-950">
                TRNDY COUTURE JOURNAL
              </h3>
            </div>

            <div className="space-y-3">
              {journals.map((item, idx) => (
                <div
                  key={idx}
                  onMouseEnter={() => setJournalIndex(idx)}
                  className={`cursor-pointer rounded-2xl border p-4 transition duration-300 ${
                    journalIndex === idx
                      ? "border-zinc-200 bg-white shadow-sm"
                      : "border-transparent opacity-60 hover:opacity-100"
                  }`}
                >
                  <h4 className="text-sm font-black text-zinc-950">{item.title}</h4>
                  {journalIndex === idx && (
                    <p className="mt-2 text-xs leading-relaxed font-light text-zinc-500">
                      {item.phrase}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
          <div className="relative h-[400px] overflow-hidden rounded-3xl bg-zinc-300 shadow-inner">
            <Image
              src={journals[journalIndex].img}
              alt="Journal View"
              fill
              className="scale-100 object-cover transition-all duration-700 ease-in-out"
            />
          </div>
        </div>
      </section>

      {/* 볼드 볼륨 브랜드 대형 철학 매니페스토 */}
      <section className="relative overflow-hidden bg-zinc-950 px-6 py-28 text-center text-white md:px-8">
        <div className="bg-radial-gradient absolute inset-0 from-zinc-900 to-zinc-950 opacity-40" />
        <div className="relative z-10 mx-auto max-w-3xl space-y-6">
          <h4 className="text-[10px] font-black tracking-widest text-zinc-500 uppercase">
            OUR ESSENCE MANIFESTO
          </h4>
          <h3 className="text-4xl leading-[1.05] font-black tracking-tight md:text-7xl md:leading-none md:tracking-tighter">
            WE TEXTURE THE SILENCE
          </h3>
          <p className="mx-auto max-w-xl text-xs leading-relaxed font-light text-zinc-400 md:text-base">
            TRNDY는 보이지 않는 디테일에 집착합니다. 옷의 내부 스티치 공정, 목덜미에
            닿는 라벨의 부드러움, 주머니가 기울어지는 미세한 각도까지. 우리는 일상이
            닿는 침묵의 순간들을 완벽하게 텍스처링합니다.
          </p>
          <div className="pt-2">
            {/* TODO: 브랜드 스토리/장인정신 소개 페이지가 아직 없어서 다음 단계에서 연결 예정 */}
            <button className="rounded-full bg-white px-6 py-3 text-xs font-black tracking-widest text-zinc-950 uppercase transition hover:bg-zinc-200">
              Read Our Craftsmanship
            </button>
          </div>
        </div>
      </section>

      {/* 소셜 스타일 스냅 보드 피드 */}
      <section className="mx-auto max-w-7xl space-y-6 px-6 py-24 md:px-8">
        <div className="space-y-1 text-center">
          <h3 className="text-2xl font-black tracking-tight text-zinc-950">
            #TRNDY_STYLE_BOOK
          </h3>
          <p className="text-xs font-light text-zinc-400">
            패션 그 이상의 커뮤니티, 전 세계 컬렉터들의 연출 리얼 피드백
          </p>
        </div>
        <div className="grid grid-cols-3 gap-3 sm:grid-cols-6">
          {INSTA_FEEDS.map((img, idx) => (
            <div
              key={idx}
              className="group relative aspect-square cursor-pointer overflow-hidden rounded-2xl bg-zinc-200 shadow-sm"
            >
              <Image
                src={img}
                alt="Feed"
                fill
                className="object-cover transition duration-500 group-hover:scale-105 group-hover:brightness-95"
              />
            </div>
          ))}
        </div>
      </section>

      {/* 푸터 진입 전 신뢰 확보 아코디언 */}
      <section className="mx-auto max-w-7xl px-6 pb-24 md:px-8">
        <div className="grid grid-cols-1 gap-6 border-t border-b border-zinc-200 py-8 text-xs text-zinc-600 md:grid-cols-3">
          <div className="space-y-1 rounded-2xl border border-zinc-100 bg-white p-4">
            <span className="block font-bold text-zinc-900">
              ⚡ 실시간 빠른 배송조회 안내
            </span>
            <p className="font-light text-zinc-400">
              오후 2시 이전 결제 완료 건에 한하여 당일 즉시 컨테이너에서 CJ대한통운 출고
              처리가 접수됩니다.
            </p>
          </div>
          <div className="space-y-1 rounded-2xl border border-zinc-100 bg-white p-4">
            <span className="block font-bold text-zinc-900">
              🔄 7일 이내 자유로운 교환/반품 보장
            </span>
            <p className="font-light text-zinc-400">
              마이페이지를 통해 원클릭 교환 접수가 가능하며 시착 흔적이 없는 상품에 한해
              무료 회수 택배가 배정됩니다.
            </p>
          </div>
          <div className="space-y-1 rounded-2xl border border-zinc-100 bg-white p-4">
            <span className="block font-bold text-zinc-900">
              🔒 안전한 에스크로 금융 결제
            </span>
            <p className="font-light text-zinc-400">
              고객님의 안전 거래를 위해 현금 결제 시 저희 쇼핑몰에서 가입한 KB국민은행의
              구매안전 서비스가 적용됩니다.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
