interface ProductDetailProps {
  params: Promise<{ id: string }>;
}

export default async function ProductDetailPage({ params }: ProductDetailProps) {
  const { id } = await params;

  return (
    // [1번 외벽 박스] 배경색 및 기본 서체 셋팅
    <div className="min-h-screen bg-zinc-50 font-sans text-zinc-900 antialiased">
      {/* [2번 내부 구역: 상단 헤더] */}
      <header className="sticky top-0 z-50 flex items-center justify-between border-b border-zinc-200/80 bg-white/80 px-6 py-4 backdrop-blur-md">
        <div className="cursor-pointer text-xl font-black tracking-widest text-zinc-900">
          STUDIO.🛍️
        </div>
        <nav className="hidden space-x-8 text-sm font-medium text-zinc-600 md:flex">
          <a href="#" className="transition hover:text-black">
            NEW
          </a>
          <a href="#" className="font-semibold text-black">
            SHOP
          </a>
          <a href="#" className="transition hover:text-black">
            COLLECTION
          </a>
          <a
            href="#"
            className="font-semibold text-red-500 transition hover:text-red-600"
          >
            SALE %
          </a>
        </nav>
        <div className="flex items-center space-x-4 text-sm font-medium">
          <button className="rounded-full bg-zinc-950 px-4 py-2 text-xs text-white transition hover:bg-zinc-800">
            장바구니 (3)
          </button>
        </div>
      </header>

      {/* [3번 내부 구역: 메인 상세페이지 컨텐츠 시작] */}
      <main className="mx-auto max-w-6xl px-6 py-12">
        {/* 브레드크럼 */}
        <div className="mb-8 flex space-x-2 text-xs font-medium text-zinc-400">
          <a href="#" className="hover:text-zinc-600">
            HOME
          </a>
          <span>/</span>
          <a href="#" className="hover:text-zinc-600">
            SHOP
          </a>
          <span>/</span>
          <span className="text-zinc-600">아이템 #{id}</span>
        </div>

        {/* 1층 상단 스펙: 2분할 레이아웃 시작 (이미지 vs 주문창) */}
        <div className="grid grid-cols-1 gap-12 md:grid-cols-2 lg:gap-16">
          {/* 왼쪽: 상품 이미지 스택 */}
          <div className="space-y-4">
            <div className="relative flex aspect-[3/4] flex-col items-center justify-center rounded-3xl bg-zinc-200 text-lg font-bold text-zinc-400 shadow-sm">
              <span>MAIN IMAGE #{id}</span>
              <span className="mt-1 text-xs font-normal text-zinc-500">
                클릭 시 확대 보기
              </span>
            </div>
            <div className="grid grid-cols-4 gap-3">
              <div className="flex aspect-square cursor-pointer items-center justify-center rounded-xl border-2 border-zinc-950 bg-zinc-300 text-[10px] font-bold text-zinc-500">
                IMAGE 01
              </div>
              <div className="flex aspect-square cursor-pointer items-center justify-center rounded-xl bg-zinc-200 text-[10px] text-zinc-400">
                IMAGE 02
              </div>
              <div className="flex aspect-square cursor-pointer items-center justify-center rounded-xl bg-zinc-200 text-[10px] text-zinc-400">
                IMAGE 03
              </div>
              <div className="flex aspect-square cursor-pointer items-center justify-center rounded-xl bg-zinc-200 text-[10px] text-zinc-400">
                IMAGE 04
              </div>
            </div>
          </div>

          {/* 오른쪽: 정보 스펙창 */}
          <div className="flex flex-col justify-between space-y-6">
            <div className="space-y-3">
              <span className="rounded-md bg-zinc-950 px-2.5 py-1 text-[10px] font-black tracking-wider text-white uppercase">
                BEST ITEM
              </span>
              <h1 className="text-3xl leading-tight font-black tracking-tight text-zinc-900">
                미니멀 캡슐 원단 시그니처 자켓 #{id}
              </h1>
              <div className="flex items-baseline space-x-3 pt-1">
                <span className="text-2xl font-black text-zinc-950">159,000원</span>
                <span className="text-sm text-zinc-400 line-through">199,000원</span>
                <span className="text-sm font-bold text-red-500">20% OFF</span>
              </div>
              <p className="border-t border-zinc-200/60 pt-3 text-sm leading-relaxed text-zinc-500">
                자연스러운 오버핏 실루엣과 바이오 워싱 가공을 거쳐 수축을 최소화한
                STUDIO의 주력 넘버링 프리미엄 자켓 라인업입니다.
              </p>
            </div>

            {/* 옵션 구역 */}
            <div className="space-y-4 border-t border-zinc-200/60 pt-4">
              <div className="space-y-2">
                <span className="text-xs font-bold text-zinc-400">COLOR</span>
                <div className="flex space-x-3">
                  <button className="h-7 w-7 rounded-full bg-zinc-800 ring-2 ring-zinc-950 ring-offset-2"></button>
                  <button className="h-7 w-7 rounded-full bg-stone-400 ring-0 ring-zinc-300 ring-offset-2 hover:ring-1"></button>
                  <button className="h-7 w-7 rounded-full bg-zinc-200 ring-0 ring-zinc-300 ring-offset-2 hover:ring-1"></button>
                </div>
              </div>

              <div className="space-y-2">
                <span className="text-xs font-bold text-zinc-400">SIZE</span>
                <div className="flex space-x-2">
                  {["S", "M", "L", "XL"].map((size) => (
                    <button
                      key={size}
                      className={`flex h-11 w-11 items-center justify-center rounded-xl border text-xs font-bold transition ${
                        size === "L"
                          ? "border-zinc-950 bg-zinc-950 text-white"
                          : "border-zinc-200 bg-white text-zinc-600 hover:border-zinc-400"
                      }`}
                    >
                      {size}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* 최종 가격 및 2버튼 */}
            <div className="space-y-4 border-t border-zinc-200/60 pt-4">
              <div className="flex items-end justify-between">
                <span className="text-xs font-semibold text-zinc-400">
                  총 상품 금액
                </span>
                <span className="text-xl font-black text-zinc-950">159,000원</span>
              </div>
              <div className="flex space-x-3">
                <button className="flex-1 rounded-xl bg-zinc-950 py-4 text-sm font-bold text-white transition hover:bg-zinc-800">
                  바로 구매하기
                </button>
                <button className="rounded-xl border border-zinc-200 bg-white px-5 py-4 text-sm font-bold text-zinc-950 transition hover:bg-zinc-100">
                  🖤
                </button>
              </div>

              {/* 미니 텍스트 정보 리스트 */}
              <div className="space-y-1 rounded-xl bg-zinc-100/80 p-3.5 text-[11px] text-zinc-500">
                <p>• 배송 기간 : 서울/경기 기준 내일 보장 (무료배송)</p>
                <p>• 혜택 안내 : 멤버십 가입 시 첫 구매 10% 추가 적립</p>
              </div>
            </div>
          </div>
        </div>

        {/* 2층: 긴 아코디언 상세 정보 보드 (하단 스크롤 레이아웃 대폭 확장) */}
        <section className="mt-28 border-t border-zinc-200">
          {/* 상단 스티키형 탭 메뉴 */}
          <div className="sticky top-[61px] z-40 flex justify-center space-x-12 border-b border-zinc-200 bg-zinc-50/90 text-sm font-bold text-zinc-400 backdrop-blur-sm">
            <button className="border-b-2 border-zinc-950 py-4 text-zinc-950">
              PRODUCT INFO
            </button>
            <button className="py-4 hover:text-zinc-600">CUSTOMER REVIEW (42)</button>
            <button className="py-4 hover:text-zinc-600">DELIVERY & RETURN</button>
          </div>

          {/* 무한 롱-스펙 정보 컷 */}
          <div className="mx-auto max-w-2xl space-y-16 py-16">
            {/* 컷 1: 패브릭 노트 */}
            <div className="space-y-4 text-center">
              <span className="text-xs font-bold tracking-widest text-zinc-400 uppercase">
                01 / BRAND IDENTITY
              </span>
              <h3 className="text-xl font-extrabold tracking-tight">
                지속 가능한 프리미엄 소재
              </h3>
              <p className="text-justify text-sm leading-relaxed text-zinc-500 md:text-center">
                가공 처리되지 않은 천연 린넨과 고밀도 수입 코튼을 혼방하여 오랜 시간
                착용해도 변함없는 아웃핏을 자랑합니다. 가벼운 수분기는 빠르게 건조되어
                쾌적한 여름 일상을 지원합니다.
              </p>
            </div>
            <div className="flex h-[600px] items-center justify-center rounded-3xl bg-zinc-200 text-sm font-bold text-zinc-400">
              스튜디오 피팅 모델 고화질 화보 01
            </div>

            {/* 컷 2: 마감 공정 디테일 */}
            <div className="space-y-4 pt-8 text-center">
              <span className="text-xs font-bold tracking-widest text-zinc-400 uppercase">
                02 / CRAFTSMANSHIP
              </span>
              <h3 className="text-xl font-extrabold tracking-tight">
                해체주의적 절개와 더블 세세 봉제
              </h3>
              <p className="text-justify text-sm leading-relaxed text-zinc-500 md:text-center">
                어깨선부터 소매단까지 떨어지는 비대칭 스티치는 STUDIO의 독자적인 패턴
                공법입니다. 보이지 않는 내부 안감 안쪽까지 해리 테이프로 꼼꼼히 감싸
                시각적 완성도와 내구성을 모두 잡았습니다.
              </p>
            </div>
            <div className="flex h-[600px] items-center justify-center rounded-3xl bg-zinc-200 text-sm font-bold text-zinc-400">
              원단 줌인 및 마감 디테일 정밀 클로즈업 02
            </div>
          </div>
        </section>

        {/* 3층: 대형 포토 및 댓글 리뷰 구역 (새로 추가) */}
        <section className="mt-20 border-t border-zinc-200 pt-16">
          <div className="mb-10 flex flex-col items-start justify-between gap-4 md:flex-row md:items-center">
            <div>
              <h2 className="flex items-center space-x-2 text-2xl font-black tracking-tight">
                <span>구매 고객들의 실시간 평가</span>
                <span className="text-lg text-blue-600">★ 4.8</span>
              </h2>
              <p className="mt-1 text-xs text-zinc-400">
                포토 리뷰 작성 시 즉시 사용 가능한 2,000원 적립금 제공
              </p>
            </div>
            <button className="rounded-xl border border-zinc-300 bg-white px-4 py-2.5 text-xs font-semibold text-zinc-700 transition hover:border-zinc-950">
              리뷰 작성하기 📝
            </button>
          </div>

          {/* 실시간 포토 갤러리 미니 그리드 */}
          <div className="mb-10 grid grid-cols-4 gap-3 sm:grid-cols-6">
            {[1, 2, 3, 4, 5, 6].map((idx) => (
              <div
                key={idx}
                className="flex aspect-square cursor-pointer items-center justify-center rounded-2xl bg-zinc-200 text-[10px] font-bold text-zinc-400 shadow-sm transition hover:opacity-80"
              >
                PHOTO 0{idx}
              </div>
            ))}
          </div>

          {/* 한줄평 댓글 리뷰 리스트 피드 */}
          <div className="space-y-4">
            {[
              {
                user: "kim**",
                spec: "Color: 블랙 / Size: L",
                review:
                  "키 181에 L 사이즈 딱 원하던 세미오버핏 나옵니다. 원단 짱짱하고 두께감도 지금 입기에 최적이에요.",
                score: "★★★★★",
              },
              {
                user: "lee**",
                spec: "Color: 베이지 / Size: M",
                review:
                  "색상이 화면보다 실물이 훨씬 감성 넘치네요. 단추 디테일이 고급스러워서 아주 만족합니다.",
                score: "★★★★★",
              },
              {
                user: "park**",
                spec: "Color: 블랙 / Size: S",
                review:
                  "소매가 약간 길게 나오긴 했는데 롤업해서 입으니까 미니멀하고 예뻐요. 배송도 하루 만에 와서 깜짝 놀랐습니다.",
                score: "★★★★☆",
              },
            ].map((rev, i) => (
              <div
                key={i}
                className="space-y-2 rounded-2xl border border-zinc-200/60 bg-white p-6 shadow-sm"
              >
                <div className="flex justify-between text-xs font-bold">
                  <div className="flex items-center space-x-2">
                    <span className="text-zinc-800">{rev.user}</span>
                    <span className="text-zinc-300">|</span>
                    <span className="font-normal text-zinc-400">{rev.spec}</span>
                  </div>
                  <span className="font-mono tracking-tight text-amber-500">
                    {rev.score}
                  </span>
                </div>
                <p className="text-xs leading-relaxed text-zinc-600 md:text-sm">
                  {rev.review}
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* 4층: 연관 추천 상품 아이템 매칭 그리드 (새로 추가) */}
        <section className="mt-28 border-t border-zinc-200 pt-16">
          <h3 className="mb-1 text-xl font-black tracking-tight">
            함께 코디하면 좋은 추천 상품 🧥
          </h3>
          <p className="mb-8 text-xs text-zinc-400">
            STUDIO 크루들이 제안하는 시그니처 믹스앤매치 셋업 라인
          </p>

          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            {[
              { name: "린넨 세미와이드 버뮤다 쇼츠", price: "48,000원" },
              { name: "스퀘어 비건 머슬핏 슬리브리스", price: "22,000원" },
              { name: "소가죽 오링 미니 바디 스케어백", price: "98,000원" },
              { name: "실버 스퀘어 체인 링크 팔찌", price: "29,000원" },
            ].map((item, idx) => (
              <div key={idx} className="group cursor-pointer">
                <div className="mb-3 flex aspect-[3/4] items-center justify-center overflow-hidden rounded-2xl bg-zinc-200 text-[10px] font-bold text-zinc-400">
                  <span className="transition duration-300 group-hover:scale-105">
                    MATCH ITEM 0{idx + 1}
                  </span>
                </div>
                <h4 className="truncate text-xs font-bold text-zinc-700 transition group-hover:text-black">
                  {item.name}
                </h4>
                <p className="mt-0.5 text-xs font-black text-zinc-950">{item.price}</p>
              </div>
            ))}
          </div>
        </section>

        {/* 5층: 배송/환불 교환 CS 텍스트 안내장 고도화 */}
        <section className="mt-28 grid grid-cols-1 gap-8 rounded-3xl border border-zinc-200/70 bg-white p-6 text-[11px] leading-relaxed text-zinc-500 md:grid-cols-2 md:p-8">
          <div className="space-y-2">
            <h4 className="text-xs font-black tracking-wider text-zinc-800 uppercase">
              📦 배송 가이드
            </h4>
            <p>
              • STUDIO의 모든 의류 상품은 100% 무료 전용 박스 배송 시스템을 채택하고
              있습니다.
            </p>
            <p>
              • 오후 3시 이전 주문 결제 완료 건은 당일 출고되어 기본적으로 다음 날
              도착을 보장합니다.
            </p>
            <p>
              • 도서산간 지역의 경우 물류 흐름 상황에 따라 1~2일 가량 지연이 발생할 수
              있습니다.
            </p>
          </div>
          <div className="space-y-2">
            <h4 className="text-xs font-black tracking-wider text-zinc-800 uppercase">
              🔄 반품 및 교환 정책
            </h4>
            <p>
              • 상품 수령 후 7일 이내 시 착용 흔적이 없는 새 상품 상태에 한하여 자유롭게
              교환 및 반품이 가능합니다.
            </p>
            <p>
              • 단, 의류 택(Tag)을 훼손하거나 오염, 세탁, 수선 처리가 된 경우에는
              교환처리가 거부될 수 있습니다.
            </p>
            <p>
              • 단순 변심에 의한 컬러/사이즈 왕복 교환 배송비는 6,000원이 부과됩니다.
            </p>
          </div>
        </section>
      </main>

      {/* [6번 내부 구역: 하단 푸터] */}
      <footer className="mt-32 border-t border-zinc-800 bg-zinc-900 py-10 text-center text-[11px] text-zinc-500">
        © 2026 STUDIO. All rights reserved. Built with Tailwind CSS v4.
      </footer>
    </div>
  );
}
