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
    <div className="bg-zinc-50 min-h-screen text-zinc-900 font-sans antialiased">
      {/* [2번 내부 구역: 상단 헤더] 동일하게 유지 */}
      <header className="border-b border-zinc-200/80 bg-white/80 backdrop-blur-md sticky top-0 z-50 px-6 py-4 flex items-center justify-between">
        <div className="text-xl font-black tracking-widest text-zinc-900 cursor-pointer">
          STUDIO.🛍️
        </div>
        <nav className="hidden md:flex space-x-8 text-sm font-medium text-zinc-600">
          <a href="#" className="text-black font-semibold">
            SHOP
          </a>
          <a href="#" className="hover:text-black transition">
            NEW
          </a>
          <a href="#" className="hover:text-black transition">
            COLLECTION
          </a>
        </nav>
        <div className="flex items-center space-x-4 text-sm font-medium">
          <button className="bg-zinc-950 text-white px-4 py-2 rounded-full text-xs">
            장바구니 (3)
          </button>
        </div>
      </header>

      {/* [3번 메인 컨텐츠 영역] */}
      <main className="max-w-6xl mx-auto px-6 py-10">
        {/* 상단 타이틀 구역 */}
        <div className="border-b border-zinc-200 pb-6 mb-8">
          <h1 className="text-3xl font-black tracking-tight">모든 상품 보기</h1>
          <p className="text-zinc-400 text-xs mt-1.5">
            STUDIO가 제안하는 시즌 에센셜 컬렉션 ({products.length})
          </p>
        </div>

        {/* 🧭 컨트롤러 바: 필터 버튼 및 정렬 순서 선택 구역 */}
        <div className="flex justify-between items-center mb-6 text-sm">
          {/* 왼쪽: 빠른 카테고리 필터 칩 (가로 정렬 flex) */}
          <div className="flex space-x-2 overflow-x-auto scrollbar-hide">
            <button className="bg-zinc-950 text-white font-semibold px-4 py-2 rounded-full text-xs cursor-pointer">
              전체
            </button>
            <button className="bg-white text-zinc-600 border border-zinc-200 hover:border-zinc-400 px-4 py-2 rounded-full text-xs transition cursor-pointer">
              상의
            </button>
            <button className="bg-white text-zinc-600 border border-zinc-200 hover:border-zinc-400 px-4 py-2 rounded-full text-xs transition cursor-pointer">
              하의
            </button>
            <button className="bg-white text-zinc-600 border border-zinc-200 hover:border-zinc-400 px-4 py-2 rounded-full text-xs transition cursor-pointer">
              아우터
            </button>
            <button className="bg-white text-zinc-600 border border-zinc-200 hover:border-zinc-400 px-4 py-2 rounded-full text-xs transition cursor-pointer">
              잡화
            </button>
          </div>

          {/* 오른쪽: 정렬 기준 드롭다운 선택상자 */}
          <select className="bg-white border border-zinc-200 rounded-xl px-3 py-2 text-xs font-medium text-zinc-600 focus:outline-none focus:border-zinc-400 cursor-pointer">
            <option>추천순</option>
            <option>신상품순</option>
            <option>낮은 가격순</option>
            <option>높은 가격순</option>
          </select>
        </div>

        {/* 🛍️ 상품 배치 격자판 (Grid) 구역 */}
        {/* 모바일 2열(grid-cols-2), 태블릿 3열(sm:), 데스크탑 4열(md:) 반응형 완벽 대응 */}
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-x-4 gap-y-10">
          {/* 자바스크립트 map 함수로 상품 리스트 자동 나열 */}
          {products.map((product) => (
            <div key={product.id} className="group cursor-pointer relative">
              {/* 상품 이미지 박스 */}
              <div className="bg-zinc-200 aspect-[3/4] rounded-2xl overflow-hidden relative mb-3.5 flex items-center justify-center text-zinc-400 font-semibold text-xs tracking-wider">
                {/* 마우스 올리면 1.05배 확대 효과 */}
                <span className="group-hover:scale-105 transition duration-500">
                  IMAGE {product.id}
                </span>

                {/* 좌상단 상태 배지 (NEW, BEST, SALE) */}
                {product.tag && (
                  <span
                    className={`absolute top-3 left-3 text-[9px] font-black px-2 py-1 rounded-md tracking-wider text-white ${
                      product.tag === "SALE" ? "bg-red-500" : "bg-zinc-950"
                    }`}
                  >
                    {product.tag}
                  </span>
                )}
              </div>

              {/* 상품 텍스트 정보 정보 */}
              <div className="space-y-1">
                <p className="text-[11px] text-zinc-400 font-medium">{product.color}</p>
                <h3 className="text-sm font-medium text-zinc-700 group-hover:text-zinc-950 transition truncate">
                  {product.title}
                </h3>
                <p className="text-sm font-bold text-zinc-950">{product.price}</p>
              </div>
            </div>
          ))}
        </div>

        {/* 🔄 하단 페이지네이션 / 더보기 버튼 */}
        <div className="flex justify-center mt-20">
          <button className="bg-white border border-zinc-200 hover:border-zinc-950 text-zinc-700 hover:text-zinc-950 font-semibold px-8 py-3.5 rounded-xl text-xs transition duration-200 shadow-sm cursor-pointer">
            더보기 (1 / 3) 🔽
          </button>
        </div>
      </main>

      {/* [4번 내부 구역: 하단 푸터] 마감 */}
      <footer className="bg-zinc-900 text-zinc-500 text-[11px] border-t border-zinc-800 mt-32 py-8 text-center">
        © 2026 STUDIO. All rights reserved. Built with Tailwind CSS v4.
      </footer>
    </div>
  );
}
