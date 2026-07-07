export default function UltimateCartPage() {
  // 1. 실제 백엔드와 연동될 법한 정교한 장바구니 상품 데이터 세트
  const cartItems = [
    {
      id: "1",
      title: "워시드 미니멀 데님 자켓",
      option: "Color: 블랙 / Size: L",
      price: 159000,
      discountPrice: 127200, // 20% 할인 반영 가격
      quantity: 1,
      imgText: "JACKET",
      status: "stock-alert", // 품절 임박 표시용 상태값
      deliveryType: "내일보장",
    },
    {
      id: "2",
      title: "린넨 오버사이즈 셔츠",
      option: "Color: 베이지 / Size: M",
      price: 45000,
      discountPrice: 45000,
      quantity: 2,
      imgText: "SHIRTS",
      status: "normal",
      deliveryType: "일반배송",
    },
    {
      id: "3",
      title: "와이드 버뮤다 팬츠",
      option: "Color: 블랙 / Size: M",
      price: 52000,
      discountPrice: 41600, // 20% 할인 반영 가격
      quantity: 1,
      imgText: "PANTS",
      status: "normal",
      deliveryType: "내일보장",
    },
  ];

  // 2. 장바구니 금액 정밀 셈법 자동화 수식
  const totalOriginalPrice = cartItems.reduce(
    (acc, item) => acc + item.price * item.quantity,
    0,
  );
  const totalDiscountPrice = cartItems.reduce(
    (acc, item) => acc + (item.price - item.discountPrice) * item.quantity,
    0,
  );
  const totalProductPrice = totalOriginalPrice - totalDiscountPrice;
  const shippingFee = totalProductPrice >= 100000 ? 0 : 3000; // 10만원 이상 결제 시 무료배송
  const totalOrderPrice = totalProductPrice + shippingFee;
  const expectedPoints = Math.floor(totalOrderPrice * 0.01); // 1% 적립

  return (
    // [1번 외벽 박스] 전체 배경색 및 폰트 디테일
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
          <a href="#" className="transition hover:text-black">
            SHOP
          </a>
          <a href="#" className="transition hover:text-black">
            COLLECTION
          </a>
        </nav>
        <div className="flex items-center space-x-1 text-sm font-bold text-zinc-950">
          <span>마이페이지</span>
          <span className="rounded-full bg-zinc-100 px-1.5 py-0.5 text-[10px]">
            VIP
          </span>
        </div>
      </header>

      {/* [3번 메인 대형 컨텐츠 영역] */}
      <main className="mx-auto max-w-6xl px-6 py-10">
        {/* 3-1. 주문 스텝 인디케이터 상단 배치 */}
        <div className="mb-8 flex flex-col items-start justify-between gap-2 border-b border-zinc-200 pb-6 md:flex-row md:items-center">
          <div>
            <h1 className="flex items-baseline space-x-2 text-3xl font-black tracking-tight">
              <span>장바구니</span>
              <span className="text-sm font-bold text-blue-600">
                ({cartItems.length})
              </span>
            </h1>
          </div>
          {/* 결제 단계 UX 표시 */}
          <div className="flex items-center space-x-3 text-xs font-bold tracking-wide">
            <span className="border-b-2 border-zinc-950 pb-0.5 text-zinc-950">
              01 장바구니
            </span>
            <span className="text-zinc-300">➔</span>
            <span className="text-zinc-400">02 주문/결제</span>
            <span className="text-zinc-300">➔</span>
            <span className="text-zinc-400">03 주문 완료</span>
          </div>
        </div>

        {/* 3-2. 2분할 메인 레이아웃 시작 (비대칭 비율: 2칸 vs 1칸) */}
        <div className="grid grid-cols-1 items-start gap-8 lg:grid-cols-3">
          {/* 📦 왼쪽 섹션 (2칸 분량 차지): 상품 목록 + 사은품 + 쿠폰 폼 */}
          <div className="space-y-6 lg:col-span-2">
            {/* 1) 상단 체크박스 및 컨트롤러 바 */}
            <div className="flex items-center justify-between rounded-2xl border border-zinc-200/60 bg-white p-4 text-xs font-semibold text-zinc-500 shadow-sm">
              <div className="flex items-center space-x-2.5">
                <input
                  type="checkbox"
                  defaultChecked
                  className="h-4 w-4 cursor-pointer rounded border-zinc-300 text-zinc-950 focus:ring-zinc-950"
                />
                <span className="text-zinc-800">전체 선택 (3/3)</span>
              </div>
              <div className="flex space-x-4">
                <button className="cursor-pointer transition hover:text-zinc-900">
                  품절/유효기간 만료 삭제
                </button>
                <span className="text-zinc-200">|</span>
                <button className="cursor-pointer transition hover:text-red-500">
                  선택 삭제
                </button>
              </div>
            </div>

            {/* 2) 장바구니에 담긴 진짜 이커머스 아이템 리스트 피드 */}
            <div className="space-y-4">
              {cartItems.map((item) => (
                <div
                  key={item.id}
                  className="group relative flex flex-col space-y-4 rounded-3xl border border-zinc-200/60 bg-white p-5 shadow-sm md:flex-row md:space-y-0 md:space-x-4"
                >
                  {/* 체크박스와 이미지 구역 */}
                  <div className="flex flex-shrink-0 items-center space-x-3">
                    <input
                      type="checkbox"
                      defaultChecked
                      className="h-4 w-4 cursor-pointer rounded border-zinc-300 text-zinc-950 focus:ring-zinc-950"
                    />
                    <div className="relative flex aspect-[3/4] w-20 flex-shrink-0 items-center justify-center overflow-hidden rounded-2xl bg-zinc-100 text-[10px] font-bold tracking-wider text-zinc-400 md:w-24">
                      {item.imgText}
                      {/* 무료배송/내일보장 마크 오버레이 */}
                      <span
                        className={`absolute inset-x-0 bottom-0 py-0.5 text-center text-[9px] font-bold text-white ${
                          item.deliveryType === "내일보장"
                            ? "bg-blue-600/90"
                            : "bg-zinc-500/90"
                        }`}
                      >
                        {item.deliveryType}
                      </span>
                    </div>
                  </div>

                  {/* 정보 설명 및 수량 제어 구역 */}
                  <div className="flex min-w-0 flex-1 flex-col justify-between py-1">
                    <div className="space-y-1.5">
                      <div className="flex items-start justify-between">
                        <h3 className="truncate pr-8 text-sm font-bold text-zinc-900 md:text-base">
                          {item.title}
                        </h3>
                        <button className="absolute top-5 right-5 cursor-pointer text-sm text-zinc-400 transition hover:text-zinc-950">
                          ✕
                        </button>
                      </div>
                      <p className="inline-block rounded-md bg-zinc-50 px-2.5 py-1 text-[11px] font-medium text-zinc-400">
                        {item.option}
                      </p>

                      {/* ⚠️ 품절 임박 조건부 마크업 */}
                      {item.status === "stock-alert" && (
                        <p className="animate-pulse text-[10px] font-bold tracking-tight text-red-500">
                          🚨 품절 임박! 현재 잔여 수량이 2개 미만입니다.
                        </p>
                      )}
                    </div>

                    {/* 하단 단가 계산 및 인터랙션 라인 */}
                    <div className="mt-6 flex items-end justify-between border-t border-zinc-100/70 pt-4">
                      {/* 수량 체인저 */}
                      <div className="flex items-center overflow-hidden rounded-xl border border-zinc-200 bg-zinc-50 text-xs">
                        <button className="px-3 py-1.5 font-bold transition hover:bg-zinc-200">
                          −
                        </button>
                        <span className="w-10 border-x border-zinc-200 bg-white px-3 py-1.5 text-center font-bold text-zinc-800">
                          {item.quantity}
                        </span>
                        <button className="px-3 py-1.5 font-bold transition hover:bg-zinc-200">
                          +
                        </button>
                      </div>

                      {/* 원가 vs 할인금액 입체적 가격 매칭 */}
                      <div className="text-right">
                        {item.price !== item.discountPrice && (
                          <p className="text-xs font-medium text-zinc-400 line-through">
                            {(item.price * item.quantity).toLocaleString()}원
                          </p>
                        )}
                        <p className="text-base font-black text-zinc-950">
                          {(item.discountPrice * item.quantity).toLocaleString()}원
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* 3) 🆕 대형 쇼핑몰의 꽃: 사은품 증정 안내 스페셜 가이드 보드 */}
            {totalProductPrice >= 150000 && (
              <div className="flex items-center space-x-4 rounded-3xl border border-amber-200/70 bg-amber-50/60 p-5">
                <span className="text-2xl">🎁</span>
                <div className="min-w-0 flex-1 text-xs">
                  <h4 className="text-sm font-bold text-amber-950">
                    구매 금액별 스페셜 사은품 대상자 선정
                  </h4>
                  <p className="mt-0.5 text-amber-800/80">
                    총 결제 금액이 15만원을 초과하여 [STUDIO 미니 브이넥 스카프]
                    사은품이 주문서 작성 시 자동으로 무료 포함됩니다.
                  </p>
                </div>
              </div>
            )}

            {/* 4) 🆕 프로모션 다운로드 및 쿠폰/적립금 미리 적용창 대시보드 */}
            <div className="space-y-4 rounded-3xl border border-zinc-200/60 bg-white p-6 shadow-sm">
              <h3 className="text-sm font-black tracking-tight text-zinc-800">
                쿠폰 및 혜택 적용 미리보기
              </h3>
              <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
                <div className="flex items-center justify-between rounded-2xl border border-zinc-200 bg-zinc-50/50 p-4">
                  <div>
                    <p className="text-[10px] font-bold text-zinc-400 uppercase">
                      사용 가능한 쿠폰
                    </p>
                    <p className="mt-0.5 text-xs font-bold text-zinc-800">
                      보유 중인 쿠폰 2장
                    </p>
                  </div>
                  <button className="rounded-xl border border-zinc-300 bg-white px-3 py-1.5 text-[11px] font-bold text-zinc-700 transition hover:border-zinc-950">
                    쿠폰 선택
                  </button>
                </div>
                <div className="flex items-center justify-between rounded-2xl border border-zinc-200 bg-zinc-50/50 p-4">
                  <div>
                    <p className="text-[10px] font-bold text-zinc-400 uppercase">
                      보유 마일리지
                    </p>
                    <p className="mt-0.5 text-xs font-bold text-zinc-800">
                      3,450원 사용 가능
                    </p>
                  </div>
                  <button className="rounded-xl border border-zinc-300 bg-white px-3 py-1.5 text-[11px] font-bold text-zinc-700 transition hover:border-zinc-950">
                    전액 사용
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* 💳 오른쪽 섹션 (1칸 분량 차지): 스티키형 금액 합산 요약 스탠드 */}
          <div className="top-[90px] space-y-5 rounded-3xl border border-zinc-200/60 bg-white p-6 shadow-md lg:sticky">
            <h2 className="border-b border-zinc-100 pb-3 text-base font-black tracking-tight">
              최종 결제 정보
            </h2>

            {/* 상세 가격 인보이스 매칭 */}
            <div className="space-y-3.5 text-xs font-medium text-zinc-500">
              <div className="flex justify-between">
                <span>총 상품 주문 원가</span>
                <span className="font-bold text-zinc-800">
                  {totalOriginalPrice.toLocaleString()}원
                </span>
              </div>
              <div className="flex justify-between">
                <span>시즌 프로모션 할인 혜택</span>
                <span className="font-bold text-red-500">
                  -{totalDiscountPrice.toLocaleString()}원
                </span>
              </div>
              <div className="flex justify-between">
                <span>기본 배송비</span>
                <span className="font-bold text-zinc-800">
                  {shippingFee === 0 ? "0원" : `+${shippingFee.toLocaleString()}원`}
                </span>
              </div>

              {/* 배송비 조건 충족 시 축하 배너 스위칭 */}
              {shippingFee === 0 ? (
                <p className="rounded-xl bg-blue-50 p-2 text-center text-[10px] font-bold text-blue-600">
                  🎉 [조건 충족] 무료 배송 혜택이 적용되었습니다.
                </p>
              ) : (
                <p className="rounded-xl bg-zinc-50 p-2 text-center text-[10px] text-zinc-400">
                  💡 {(100000 - totalProductPrice).toLocaleString()}원 추가 주문 시
                  **무료배송** 전환 가능!
                </p>
              )}
            </div>

            {/* 주문 합계 금액 */}
            <div className="flex items-end justify-between border-t border-zinc-100 pt-4">
              <span className="text-sm font-bold text-zinc-900">
                최종 결제 예정 금액
              </span>
              <span className="text-2xl font-black text-zinc-950">
                {totalOrderPrice.toLocaleString()}원
              </span>
            </div>

            {/* 가상의 적립 혜택 피드백 */}
            <div className="flex justify-between rounded-xl bg-zinc-50 p-3 text-[10px] font-medium text-zinc-500">
              <span>구매 확정 시 마일리지 적립</span>
              <span className="font-bold text-zinc-950">
                +{expectedPoints.toLocaleString()}원 (1%)
              </span>
            </div>

            {/* 메인 트리거 버튼 구역 */}
            <div className="space-y-2 pt-2">
              <button className="w-full cursor-pointer rounded-2xl bg-zinc-950 py-4 text-center text-sm font-bold text-white shadow-md transition duration-200 hover:bg-zinc-800">
                {totalOrderPrice.toLocaleString()}원 주문서 작성하기 🚀
              </button>
              <button className="w-full cursor-pointer rounded-xl border border-zinc-200 bg-white py-2.5 text-center text-xs font-semibold text-zinc-500 transition hover:bg-zinc-50">
                ← 더 둘러보러 가기
              </button>
            </div>
          </div>
        </div>

        {/* 4층: 🆕 하단 크로스셀링(Cross-selling) 구역 (장바구니 전용 연관 아이템 추천 그리드) */}
        <section className="mt-24 border-t border-zinc-200 pt-16">
          <div className="mb-8 flex items-end justify-between">
            <div>
              <h3 className="text-xl font-black tracking-tight">
                장바구니에 담은 상품과 어울리는 추천 코디 🕶️
              </h3>
              <p className="mt-1 text-xs text-zinc-400">
                다른 고객들이 장바구니에 함께 넣어 결제한 베스트 아이템
              </p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            {[
              {
                name: "비건 레더 캡슐 미니 스퀘어백",
                price: "89,000원",
                tag: "MD추천",
              },
              { name: "레이어드 최적화 소프트 나시 팩", price: "18,000원", tag: "" },
              { name: "안티링클 텍스처드 미들 삭스", price: "8,500원", tag: "BEST" },
              { name: "미니멀 하프 프레임 선글라스", price: "34,000원", tag: "SALE" },
            ].map((rec, idx) => (
              <div
                key={idx}
                className="group cursor-pointer rounded-2xl border border-zinc-200/50 bg-white p-4 shadow-sm transition hover:shadow-md"
              >
                <div className="relative mb-3.5 flex aspect-[3/4] items-center justify-center overflow-hidden rounded-xl bg-zinc-200 text-[10px] font-bold text-zinc-400">
                  <span className="transition duration-300 group-hover:scale-105">
                    REC ITEM 0{idx + 1}
                  </span>
                  {rec.tag && (
                    <span className="absolute top-2 left-2 rounded-md bg-zinc-950 px-1.5 py-0.5 text-[8px] font-black text-white">
                      {rec.tag}
                    </span>
                  )}
                </div>
                <h4 className="truncate text-xs font-bold text-zinc-700 transition group-hover:text-black">
                  {rec.name}
                </h4>
                <div className="mt-1 flex items-center justify-between">
                  <p className="text-xs font-black text-zinc-950">{rec.price}</p>
                  <button className="rounded-lg border border-zinc-200 px-2 py-1 text-xs font-medium transition hover:bg-zinc-950 hover:text-white">
                    담기 +
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* 5층: 쇼핑몰 고객 안심 보증 / CS 및 쇼핑 유의사항 피드 안내장 */}
        <section className="mt-20 space-y-4 rounded-3xl border border-zinc-200/30 bg-zinc-100 p-6 text-[11px] leading-relaxed text-zinc-400 md:p-8">
          <h4 className="text-xs font-bold text-zinc-700">
            ⚠️ 장바구니 이용 안내 유의사항
          </h4>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <ul className="list-disc space-y-1 pl-4">
              <li>
                장바구니에 담긴 상품은 최대 30일간 보관되며, 이후에는 자동으로 삭제
                처리됩니다.
              </li>
              <li>
                판매 종료되거나 임시 품절 처리된 상품은 주문서 작성 시 자동으로 제외될
                수 있습니다.
              </li>
              <li>
                장바구니에 상품을 담았더라도 결제 완료 전까지는 재고 확보가 보장되지
                않으므로 빠른 주문을 권장합니다.
              </li>
            </ul>
            <ul className="list-disc space-y-1 pl-4">
              <li>
                쿠폰 적용 및 마일리지 사용은 다음 단계인 [주문서 작성/결제 페이지]에서
                최종 선택 가능합니다.
              </li>
              <li>
                해외 배송 상품의 경우 결제 합산 금액에 따라 통관 시 별도의 관부가세가
                청구될 수 있습니다.
              </li>
              <li>
                사은품 프로모션은 선착순 한정 수량으로 운영되며, 재고 소진 시 예고 없이
                변경될 수 있습니다.
              </li>
            </ul>
          </div>
        </section>
      </main>

      {/* [6번 내부 구역: 하단 푸터] */}
      <footer className="mt-32 border-t border-zinc-800 bg-zinc-900 py-8 text-center text-[11px] text-zinc-500">
        © 2026 STUDIO. All rights reserved. Built with Tailwind CSS v4.
      </footer>
    </div>
  );
}
