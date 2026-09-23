export default function UltimateCheckoutPage() {
  // 1. 실제 백엔드 주문서 API에서 내려올 법한 상세 데이터 세트
  const orderItems = [
    {
      id: "1",
      title: "워시드 미니멀 데님 자켓",
      option: "Color: 블랙 / Size: L",
      price: 159000,
      discountPrice: 127200,
      quantity: 1,
      imgText: "JACKET",
    },
    {
      id: "3",
      title: "와이드 버뮤다 팬츠",
      option: "Color: 블랙 / Size: M",
      price: 52000,
      discountPrice: 41600,
      quantity: 1,
      imgText: "PANTS",
    },
  ];

  // 2. 결제 정밀 금액 연산 변수
  const totalOriginalPrice = orderItems.reduce(
    (acc, item) => acc + item.price * item.quantity,
    0,
  );
  const totalProductDiscount = orderItems.reduce(
    (acc, item) => acc + (item.price - item.discountPrice) * item.quantity,
    0,
  );
  const couponDiscount = 10000; // 가상의 적용 쿠폰 할인액
  const pointUsed = 3500; // 가상의 사용 적립금
  const shippingFee = 0; // 10만원 이상 무료배송

  const totalOrderPrice =
    totalOriginalPrice -
    totalProductDiscount -
    couponDiscount -
    pointUsed +
    shippingFee;
  const expectedPoints = Math.floor(totalOrderPrice * 0.01);

  return (
    // [1번 외벽 박스] 전체 배경색 및 폰트 레이아웃 설정
    <div className="min-h-screen bg-zinc-50 font-sans text-zinc-900 antialiased">
      {/* [3번 메인 대형 컨텐츠 영역] */}
      <main className="mx-auto max-w-6xl px-6 py-10">
        {/* 상단 타이틀 및 결제 단계 인디케이터 */}
        <div className="mb-8 flex flex-col items-start justify-between gap-2 border-b border-zinc-200 pb-6 md:flex-row md:items-center">
          <div>
            <h1 className="text-3xl font-black tracking-tight">주문 / 결제</h1>
            <p className="mt-1 flex items-center gap-1.5 text-xs text-zinc-400">
              <span className="inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-500"></span>
              주문 정보를 입력하신 후 결제를 완료해 주세요. (SSL 암호화 안전 결제)
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-x-2 gap-y-1 text-[11px] font-bold tracking-wide sm:gap-x-3 sm:text-xs">
            <span className="text-zinc-400">01 장바구니</span>
            <span className="text-zinc-300">➔</span>
            <span className="border-b-2 border-zinc-950 pb-0.5 text-zinc-950">
              02 주문/결제
            </span>
            <span className="text-zinc-300">➔</span>
            <span className="text-zinc-400">03 주문 완료</span>
          </div>
        </div>

        {/* 2분할 레이아웃 시작 (비대칭 비율: 2칸 vs 1칸) */}
        <div className="grid grid-cols-1 items-start gap-8 lg:grid-cols-3">
          {/* 📝 왼쪽 섹션 (2칸 분량 차지): 정보 입력 폼 대형 피드 */}
          <div className="space-y-6 lg:col-span-2">
            {/* 1) 주문자 회원 정보 확인 */}
            <div className="space-y-4 rounded-3xl border border-zinc-200/60 bg-white p-6 shadow-sm">
              <h3 className="border-b border-zinc-100 pb-2 text-base font-black tracking-tight">
                주문자 정보
              </h3>
              <div className="grid grid-cols-1 gap-4 text-xs font-medium md:grid-cols-3">
                <div className="space-y-1">
                  <label className="text-zinc-400">이름</label>
                  <p className="rounded-xl border border-zinc-100/50 bg-zinc-50 p-3 text-sm font-bold text-zinc-800">
                    홍길동
                  </p>
                </div>
                <div className="space-y-1">
                  <label className="text-zinc-400">이메일</label>
                  <p className="rounded-xl border border-zinc-100/50 bg-zinc-50 p-3 text-sm font-bold text-zinc-800">
                    studio@example.com
                  </p>
                </div>
                <div className="space-y-1">
                  <label className="text-zinc-400">휴대폰 번호</label>
                  <p className="rounded-xl border border-zinc-100/50 bg-zinc-50 p-3 text-sm font-bold text-zinc-800">
                    010-1234-5678
                  </p>
                </div>
              </div>
            </div>

            {/* 2) 고도화된 배송지 정보 입력창 (내부 탭 내장) */}
            <div className="space-y-5 rounded-3xl border border-zinc-200/60 bg-white p-6 shadow-sm">
              <div className="flex flex-col items-start justify-between gap-3 border-b border-zinc-100 pb-3 sm:flex-row sm:items-center">
                <h3 className="text-base font-black tracking-tight">배송지 정보</h3>
                {/* 배송지 선택 세그먼트 탭 버튼 그룹 */}
                <div className="flex rounded-xl border border-zinc-200 bg-zinc-50 p-0.5 text-[11px] font-bold">
                  <button className="rounded-lg bg-white px-3 py-1.5 text-zinc-950 shadow-xs">
                    기본 배송지
                  </button>
                  <button className="rounded-lg px-3 py-1.5 text-zinc-400 hover:text-zinc-600">
                    최근 배송지
                  </button>
                  <button className="rounded-lg px-3 py-1.5 text-zinc-400 hover:text-zinc-600">
                    신규 입력
                  </button>
                </div>
              </div>

              {/* 실제 인풋 필드 세트 */}
              <div className="space-y-4 text-xs">
                <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                  <div className="space-y-1.5">
                    <label className="font-bold text-zinc-500">
                      수령인 <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      defaultValue="홍길동"
                      className="w-full rounded-xl border border-zinc-200 bg-white p-3 text-sm font-medium focus:border-zinc-950 focus:outline-none"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <label className="font-bold text-zinc-500">
                      연락처 <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      defaultValue="010-1234-5678"
                      className="w-full rounded-xl border border-zinc-200 bg-white p-3 text-sm font-medium focus:border-zinc-950 focus:outline-none"
                    />
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="font-bold text-zinc-500">
                    주소 <span className="text-red-500">*</span>
                  </label>
                  <div className="mb-2 flex space-x-2">
                    <input
                      type="text"
                      placeholder="04524"
                      disabled
                      className="w-32 rounded-xl border border-zinc-200 bg-zinc-50 p-3 text-sm font-medium text-zinc-400"
                    />
                    <button className="cursor-pointer rounded-xl bg-zinc-950 px-4 text-xs font-bold text-white transition hover:bg-zinc-800">
                      우편번호 찾기
                    </button>
                  </div>
                  <input
                    type="text"
                    placeholder="서울 중구 세종대로 110"
                    disabled
                    className="mb-2 w-full rounded-xl border border-zinc-200 bg-zinc-50 p-3 text-sm font-medium text-zinc-400"
                  />
                  <input
                    type="text"
                    placeholder="서울특별시청 1층 종합민원실"
                    className="w-full rounded-xl border border-zinc-200 bg-white p-3 text-sm font-medium focus:border-zinc-950 focus:outline-none"
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="font-bold text-zinc-500">배송 메모</label>
                  <select className="w-full cursor-pointer rounded-xl border border-zinc-200 bg-white p-3 text-sm font-medium text-zinc-600 focus:border-zinc-950 focus:outline-none">
                    <option>부재 시 문 앞에 놓아주세요</option>
                    <option>배송 전 미리 연락해 주세요</option>
                    <option>택배함에 넣어주세요</option>
                    <option>직접 입력</option>
                  </select>
                </div>
              </div>
            </div>

            {/* 3) 주문 상품 스크롤형 간이 목록 피드 */}
            <div className="space-y-4 rounded-3xl border border-zinc-200/60 bg-white p-6 shadow-sm">
              <h3 className="border-b border-zinc-100 pb-2 text-base font-black tracking-tight">
                주문 상품 정보 ({orderItems.length}개)
              </h3>
              <div className="divide-y divide-zinc-100">
                {orderItems.map((item) => (
                  <div
                    key={item.id}
                    className="flex space-x-4 py-4 first:pt-0 last:pb-0"
                  >
                    <div className="flex aspect-[3/4] w-12 flex-shrink-0 items-center justify-center rounded-xl bg-zinc-100 text-[9px] font-bold text-zinc-400">
                      {item.imgText}
                    </div>
                    <div className="flex min-w-0 flex-1 flex-col justify-between">
                      <div className="flex items-start justify-between gap-4">
                        <h4 className="truncate text-xs font-bold text-zinc-800 md:text-sm">
                          {item.title}
                        </h4>
                        <span className="flex-shrink-0 text-xs font-black text-zinc-950">
                          {(item.discountPrice * item.quantity).toLocaleString()}원
                        </span>
                      </div>
                      <p className="text-[10px] font-medium text-zinc-400">
                        {item.option} / {item.quantity}개
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 4) 🆕 할인 쿠폰 및 적립금 입력 전용 제어 보드 */}
            <div className="space-y-5 rounded-3xl border border-zinc-200/60 bg-white p-6 shadow-sm">
              <h3 className="border-b border-zinc-100 pb-2 text-base font-black tracking-tight">
                할인 혜택 적용
              </h3>

              <div className="space-y-4 text-xs">
                {/* 쿠폰 적용 라인 */}
                <div className="space-y-1.5">
                  <label className="font-bold text-zinc-500">쿠폰 선택</label>
                  <div className="flex space-x-2">
                    <select className="flex-1 cursor-pointer rounded-xl border border-zinc-200 bg-white p-3 text-sm font-medium text-zinc-700 focus:border-zinc-950 focus:outline-none">
                      <option>
                        [시즌 오프] 전상품 10,000원 즉시 할인 쿠폰 사용 가능
                      </option>
                      <option>[웰컴 등급] 5% 추가 할인 쿠폰</option>
                      <option>적용 가능한 쿠폰 선택 안 함</option>
                    </select>
                    <button className="cursor-pointer rounded-xl border border-zinc-200 bg-zinc-100 px-4 text-xs font-bold text-zinc-700 transition hover:bg-zinc-200">
                      변경
                    </button>
                  </div>
                </div>

                {/* 적립금 직접 입력 라인 */}
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between">
                    <label className="font-bold text-zinc-500">
                      적립금 마일리지 사용
                    </label>
                    <span className="text-[11px] font-medium text-zinc-400">
                      보유 마일리지:{" "}
                      <strong className="font-bold text-zinc-700">5,200원</strong>
                    </span>
                  </div>
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      defaultValue="3,500"
                      className="flex-1 rounded-xl border border-zinc-200 bg-white p-3 text-right text-sm font-bold text-zinc-800 focus:border-zinc-950 focus:outline-none"
                    />
                    <button className="cursor-pointer rounded-xl bg-zinc-950 px-4 text-xs font-bold text-white transition hover:bg-zinc-800">
                      전액 사용
                    </button>
                  </div>
                  <p className="text-[10px] text-zinc-400">
                    • 적립금은 최소 1,000원부터 100원 단위로 꺼내 쓰실 수 있습니다.
                  </p>
                </div>
              </div>
            </div>

            {/* 5) 고도화된 결제 수단 그리드 선택창 (선택된 수단에 따른 하위 폼 유동 배치) */}
            <div className="space-y-5 rounded-3xl border border-zinc-200/60 bg-white p-6 shadow-sm">
              <h3 className="border-b border-zinc-100 pb-2 text-base font-black tracking-tight">
                결제 수단
              </h3>

              {/* 간편 결제 및 일반 카드 결제용 반응형 칩 버튼 배치 */}
              <div className="grid grid-cols-2 gap-2 text-xs font-bold sm:grid-cols-4">
                <button className="flex cursor-pointer flex-col items-center justify-center space-y-1 rounded-xl border border-zinc-200 bg-zinc-50/50 p-3.5 text-center text-zinc-500 transition">
                  <span className="text-sm">💛</span>
                  <span>카카오페이</span>
                </button>
                <button className="flex cursor-pointer flex-col items-center justify-center space-y-1 rounded-xl border border-zinc-200 bg-zinc-50/50 p-3.5 text-center text-zinc-500 transition">
                  <span className="text-sm">💙</span>
                  <span>토스페이</span>
                </button>
                <button className="flex cursor-pointer flex-col items-center justify-center space-y-1 rounded-xl border border-zinc-200 bg-zinc-50/50 p-3.5 text-center text-zinc-500 transition">
                  <span className="text-sm text-green-600">💚</span>
                  <span>네이버페이</span>
                </button>
                <button className="flex cursor-pointer flex-col items-center justify-center space-y-1 rounded-2xl border-2 border-zinc-950 bg-white p-3.5 text-center text-zinc-950 shadow-xs transition">
                  <span className="text-sm">💳</span>
                  <span>일반 신용카드</span>
                </button>
              </div>

              {/* 🆕 [확장 인터페이스] 신용카드 선택 시 하단에 노출될 가상의 카드 할부 정보 카드 박스 */}
              <div className="space-y-3 rounded-2xl border border-zinc-200 bg-zinc-50 p-4 text-xs font-medium">
                <div className="flex flex-col gap-2.5 sm:flex-row">
                  <select className="flex-1 rounded-xl border border-zinc-200 bg-white p-2.5 text-xs font-semibold text-zinc-700 focus:outline-none">
                    <option>-- 카드를 선택해 주세요 --</option>
                    <option>현대카드 (무이자 할부 가능)</option>
                    <option>신한카드 (국민/삼성 포함 혜택)</option>
                    <option>우리카드</option>
                  </select>
                  <select className="w-full rounded-xl border border-zinc-200 bg-white p-2.5 text-xs font-semibold text-zinc-700 focus:outline-none sm:w-40">
                    <option>일시불</option>
                    <option>2개월 무이자 할부</option>
                    <option>3개월 무이자 할부</option>
                    <option>5개월 할부 (부분 무이자)</option>
                  </select>
                </div>
                <p className="rounded-lg bg-blue-50/60 px-2.5 py-2 text-[10px] leading-normal font-bold text-blue-600">
                  🔥 현대카드 결제 시 복합 M포인트 최대 10% 추가 차감 및 청구할인 5%
                  프로모션 동시 선적용 중
                </p>
              </div>
            </div>
          </div>

          {/* 💳 오른쪽 섹션 (1칸 분량 차지): 영수증 상세 인보이스 매칭 및 스티키 고정 */}
          <div className="top-[85px] space-y-5 rounded-3xl border border-zinc-200/60 bg-white p-6 shadow-md lg:sticky">
            <h2 className="border-b border-zinc-100 pb-3 text-base font-black tracking-tight">
              최종 영수증 금액
            </h2>

            {/* 상세 쪼개기 영수증 인보이스 데이터 출력 */}
            <div className="space-y-3.5 border-b border-zinc-100 pb-4 text-xs font-medium text-zinc-500">
              <div className="flex justify-between">
                <span>총 상품 판매 원가</span>
                <span className="font-bold text-zinc-800">
                  {totalOriginalPrice.toLocaleString()}원
                </span>
              </div>
              <div className="flex justify-between">
                <span>상품 자체 시즌 할인액</span>
                <span className="font-bold text-red-500">
                  -{totalProductDiscount.toLocaleString()}원
                </span>
              </div>
              <div className="flex justify-between">
                <span>쿠폰 전용 차감 금액</span>
                <span className="font-bold text-red-500">
                  -{couponDiscount.toLocaleString()}원
                </span>
              </div>
              <div className="flex justify-between">
                <span>사용 처리된 회원 적립금</span>
                <span className="font-bold text-red-500">
                  -{pointUsed.toLocaleString()}원
                </span>
              </div>
              <div className="flex justify-between">
                <span>기본 기본 배송비</span>
                <span className="font-bold text-zinc-800">무료 배송</span>
              </div>
            </div>

            {/* 대형 실결제 청구 총합계 가격판 */}
            <div className="flex items-end justify-between">
              <span className="text-xs font-bold text-zinc-900">
                최종 카드 결제 금액
              </span>
              <span className="text-2xl font-black tracking-tight text-red-500">
                {totalOrderPrice.toLocaleString()}원
              </span>
            </div>

            {/* 혜택 환류 피드백 */}
            <div className="flex justify-between rounded-xl bg-zinc-50 p-3 text-[10px] font-bold text-zinc-500">
              <span>배송 완료 후 최종 적립금</span>
              <span className="font-black text-zinc-950">
                +{expectedPoints.toLocaleString()}원 (1%)
              </span>
            </div>

            {/* ⚠️ 법적 동의 전자금융 거래 약관 필수 아코디언 */}
            <div className="space-y-3 border-t border-zinc-100 pt-4 text-[11px] text-zinc-500">
              <div className="flex items-start space-x-2">
                <input
                  type="checkbox"
                  id="ultimate-agree"
                  className="mt-0.5 h-3.5 w-3.5 cursor-pointer rounded border-zinc-300 text-zinc-950 focus:ring-zinc-950"
                />
                <label
                  htmlFor="ultimate-agree"
                  className="cursor-pointer leading-tight font-bold text-zinc-800"
                >
                  주문할 상품의 상품명, 가격, 배송정보에 유의하며 약관에 최종
                  동의합니다.
                </label>
              </div>
              <div className="origin-top-left scale-95 space-y-1 rounded-xl bg-zinc-50/70 p-2.5 pl-5.5 text-zinc-400">
                <p>• 위 결제금액은 대행서비스 이용 승인금액입니다.</p>
                <p>• 구매조건 확인 및 개인정보 제3자 제공 위탁 동의</p>
                <p>• 취소/환불 규정 및 전자 대행 이용 동의 [필수]</p>
              </div>
            </div>

            {/* 최종 대형 트리거 버튼 실행 */}
            <div className="pt-2">
              <button className="w-full cursor-pointer rounded-2xl bg-zinc-950 py-4 text-center text-sm font-black tracking-wider text-white shadow-xl transition duration-200 hover:bg-zinc-800">
                {totalOrderPrice.toLocaleString()}원 안전 결제하기 🔒
              </button>
              <p className="mt-3 text-center text-[10px] leading-relaxed text-zinc-400">
                본 주문은 TRNDY의 통합 물전산 망에 직접 동기화되어 즉시 출고 처리
                대상으로 등록됩니다.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
