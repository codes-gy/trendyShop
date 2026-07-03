export default function ProductListPage() {
  // 가상의 상품 데이터 8개 배열 (map 문법으로 뿌려줄 예정)
  const products = [
    {
      id: "1",
      title: "린넨 오버사이즈 셔츠",
      price: "45,000원",
      tag: "NEW",
      color: "베이지",
    },
    {
      id: "2",
      title: "와이드 버뮤다 팬츠",
      price: "52,000원",
      tag: "BEST",
      color: "블랙",
    },
    {
      id: "3",
      title: "미니멀 크로스 레더백",
      price: "128,000원",
      tag: "",
      color: "브라운",
    },
    {
      id: "4",
      title: "실버 버클 가죽 샌들",
      price: "69,000원",
      tag: "SALE",
      color: "실버",
    },
    {
      id: "5",
      title: "소프트 세미와이드 데님",
      price: "49,000원",
      tag: "BEST",
      color: "연청",
    },
    {
      id: "6",
      title: "카고 포켓 롱 스커트",
      price: "42,000원",
      tag: "",
      color: "카키",
    },
    {
      id: "7",
      title: "스퀘어넥 슬리브리스 티",
      price: "24,000원",
      tag: "",
      color: "화이트",
    },
    {
      id: "8",
      title: "스트라이프 하프 니트",
      price: "38,000원",
      tag: "SALE",
      color: "네이비",
    },
  ];

  return (
    // [1번 외벽 박스] 전체 배경 및 레이아웃 설정
    <div className="min-h-screen bg-zinc-50 font-sans text-zinc-900 antialiased">
      {/* [2번 내부 구역: 상단 헤더] 동일하게 유지 */}
      <header className="sticky top-0 z-50 flex items-center justify-between border-b border-zinc-200/80 bg-white/80 px-6 py-4 backdrop-blur-md">
        <div className="cursor-pointer text-xl font-black tracking-widest text-zinc-900">
          STUDIO.🛍️
        </div>
        <nav className="hidden space-x-8 text-sm font-medium text-zinc-600 md:flex">
          <a href="#" className="font-semibold text-black">
            SHOP
          </a>
          <a href="#" className="transition hover:text-black">
            NEW
          </a>
          <a href="#" className="transition hover:text-black">
            COLLECTION
          </a>
        </nav>
        <div className="flex items-center space-x-4 text-sm font-medium">
          <button className="rounded-full bg-zinc-950 px-4 py-2 text-xs text-white">
            장바구니 (3)
          </button>
        </div>
      </header>

      {/* [3번 메인 컨텐츠 영역] */}
      <main className="mx-auto max-w-6xl px-6 py-10">
        {/* 상단 타이틀 구역 */}
        <div className="mb-8 border-b border-zinc-200 pb-6">
          <h1 className="text-3xl font-black tracking-tight">모든 상품 보기</h1>
          <p className="mt-1.5 text-xs text-zinc-400">
            STUDIO가 제안하는 시즌 에센셜 컬렉션 ({products.length})
          </p>
        </div>

        {/* 🧭 컨트롤러 바: 필터 버튼 및 정렬 순서 선택 구역 */}
        <div className="mb-6 flex items-center justify-between text-sm">
          {/* 왼쪽: 빠른 카테고리 필터 칩 (가로 정렬 flex) */}
          <div className="scrollbar-hide flex space-x-2 overflow-x-auto">
            <button className="cursor-pointer rounded-full bg-zinc-950 px-4 py-2 text-xs font-semibold text-white">
              전체
            </button>
            <button className="cursor-pointer rounded-full border border-zinc-200 bg-white px-4 py-2 text-xs text-zinc-600 transition hover:border-zinc-400">
              상의
            </button>
            <button className="cursor-pointer rounded-full border border-zinc-200 bg-white px-4 py-2 text-xs text-zinc-600 transition hover:border-zinc-400">
              하의
            </button>
            <button className="cursor-pointer rounded-full border border-zinc-200 bg-white px-4 py-2 text-xs text-zinc-600 transition hover:border-zinc-400">
              아우터
            </button>
            <button className="cursor-pointer rounded-full border border-zinc-200 bg-white px-4 py-2 text-xs text-zinc-600 transition hover:border-zinc-400">
              잡화
            </button>
          </div>

          {/* 오른쪽: 정렬 기준 드롭다운 선택상자 */}
          <select className="cursor-pointer rounded-xl border border-zinc-200 bg-white px-3 py-2 text-xs font-medium text-zinc-600 focus:border-zinc-400 focus:outline-none">
            <option>추천순</option>
            <option>신상품순</option>
            <option>낮은 가격순</option>
            <option>높은 가격순</option>
          </select>
        </div>

        {/* 🛍️ 상품 배치 격자판 (Grid) 구역 */}
        {/* 모바일 2열(grid-cols-2), 태블릿 3열(sm:), 데스크탑 4열(md:) 반응형 완벽 대응 */}
        <div className="grid grid-cols-2 gap-x-4 gap-y-10 sm:grid-cols-3 md:grid-cols-4">
          {/* 자바스크립트 map 함수로 상품 리스트 자동 나열 */}
          {products.map((product) => (
            <div key={product.id} className="group relative cursor-pointer">
              {/* 상품 이미지 박스 */}
              <div className="relative mb-3.5 flex aspect-[3/4] items-center justify-center overflow-hidden rounded-2xl bg-zinc-200 text-xs font-semibold tracking-wider text-zinc-400">
                {/* 마우스 올리면 1.05배 확대 효과 */}
                <span className="transition duration-500 group-hover:scale-105">
                  IMAGE {product.id}
                </span>

                {/* 좌상단 상태 배지 (NEW, BEST, SALE) */}
                {product.tag && (
                  <span
                    className={`absolute top-3 left-3 rounded-md px-2 py-1 text-[9px] font-black tracking-wider text-white ${
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
                <p className="text-sm font-bold text-zinc-950">{product.price}</p>
              </div>
            </div>
          ))}
        </div>

        {/* 🔄 하단 페이지네이션 / 더보기 버튼 */}
        <div className="mt-20 flex justify-center">
          <button className="cursor-pointer rounded-xl border border-zinc-200 bg-white px-8 py-3.5 text-xs font-semibold text-zinc-700 shadow-sm transition duration-200 hover:border-zinc-950 hover:text-zinc-950">
            더보기 (1 / 3) 🔽
          </button>
        </div>
      </main>

      {/* [4번 내부 구역: 하단 푸터] 마감 */}
      <footer className="mt-32 border-t border-zinc-800 bg-zinc-900 py-8 text-center text-[11px] text-zinc-500">
        © 2026 STUDIO. All rights reserved. Built with Tailwind CSS v4.
      </footer>
    </div>
  );
}
