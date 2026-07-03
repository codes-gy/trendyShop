import type { Metadata } from "next";
import "./globals.css"; // 💡 기존 글로벌 CSS 가져오기

export const metadata: Metadata = {
  title: "STUDIO.🛍️ | PREMIUM ESSENTIAL STORE",
  description: "직조의 밀도가 자아내는 침묵의 우아함, 스튜디오 크리에이티브.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body className="min-h-screen bg-zinc-50 font-sans text-zinc-900 antialiased selection:bg-zinc-900 selection:text-white">
        {/* 0. 글로벌 알림 탑 바 */}
        <div className="border-b border-zinc-800 bg-zinc-950 px-4 py-2.5 text-center text-xs font-bold tracking-widest text-zinc-200 uppercase">
          🔥 NEXT GENERATION PREMIUM STORE · SIGN UP FOR 10% OFF EXCLUSIVE COUPOUN
        </div>

        {/* 1. 글로벌 헤더 (Glassmorphism) */}
        <header className="sticky top-0 z-50 flex items-center justify-between border-b border-zinc-200/50 bg-white/70 px-8 py-5 backdrop-blur-lg">
          <div className="cursor-pointer text-2xl font-black tracking-tighter text-zinc-900">
            STUDIO<span className="font-light text-zinc-400">.</span>🛍️
          </div>
          <nav className="hidden space-x-10 text-xs font-bold tracking-widest text-zinc-500 md:flex">
            <a
              href="#"
              className="relative text-zinc-950 transition after:absolute after:bottom-[-4px] after:left-0 after:h-[2px] after:w-full after:bg-black hover:text-black"
            >
              NEW
            </a>
            <a href="#" className="transition hover:text-black">
              SHOP
            </a>
            <a href="#" className="transition hover:text-black">
              COLLECTION
            </a>
            <a href="#" className="transition hover:text-black">
              EDITORIAL
            </a>
            <a
              href="#"
              className="font-extrabold text-rose-600 transition hover:text-rose-700"
            >
              SALE 30%
            </a>
          </nav>
          <div className="flex items-center space-x-5 text-xs font-bold tracking-wide">
            <button className="text-zinc-400 transition hover:text-black">
              MY PAGE
            </button>
            <button className="text-zinc-900 hover:underline">SIGN IN</button>
            <button className="relative rounded-full bg-zinc-950 px-4 py-2 text-white shadow-md transition hover:bg-zinc-800">
              CART <span className="ml-1 font-black text-rose-400">3</span>
            </button>
          </div>
        </header>

        {/* 🎯 알맹이화면(page.tsx)이 쏙 들어가는 구멍 */}
        {children}

        {/* 🏢 11. 글로벌 엔터프라이즈 푸터 */}
        <footer className="border-t border-zinc-200 bg-white px-8 py-16 text-xs leading-relaxed font-light text-zinc-400">
          <div className="mx-auto grid max-w-7xl grid-cols-1 gap-12 md:grid-cols-4">
            <div className="space-y-4">
              <h5 className="text-xl font-black tracking-tighter text-zinc-950">
                STUDIO<span className="font-light text-zinc-300">.</span>🛍️
              </h5>
              <p className="text-zinc-500">
                주식회사 스튜디오숍 디지털 에센셜 그룹
                <br />
                대표이사 : 김트렌디 · 사업자등록번호 : 123-45-67890
                <br />
                통신판매업신고 : 제 2026-서울성동-0000호
                <br />
                서울특별시 성동구 아차산로 123 테크빌딩 8층
              </p>
            </div>
            <div>
              <h6 className="mb-4 text-[11px] font-bold tracking-widest text-zinc-900 uppercase">
                Customer Support
              </h6>
              <ul className="space-y-2.5">
                <li>
                  <a href="#" className="transition hover:text-zinc-950">
                    1:1 친절 문의 전광판
                  </a>
                </li>
                <li>
                  <a href="#" className="transition hover:text-zinc-950">
                    배송 상태 및 로케이션 Tracking
                  </a>
                </li>
                <li>
                  <a href="#" className="transition hover:text-zinc-950">
                    멤버십 등급별 프리미엄 베네핏
                  </a>
                </li>
                <li>
                  <a href="#" className="transition hover:text-zinc-950">
                    대량 단체 단독 주문 컨설팅
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h6 className="mb-4 text-[11px] font-bold tracking-widest text-zinc-900 uppercase">
                Corporate Info
              </h6>
              <ul className="space-y-2.5">
                <li>
                  <a href="#" className="transition hover:text-zinc-950">
                    브랜드 헤리티지 & 아카이브 스토리
                  </a>
                </li>
                <li>
                  <a href="#" className="transition hover:text-zinc-950">
                    지속 가능한 친환경 패션 에코 보고서
                  </a>
                </li>
                <li>
                  <a href="#" className="transition hover:text-zinc-950">
                    글로벌 파트너십 및 바이어 도매 제휴 문의
                  </a>
                </li>
                <li>
                  <a href="#" className="transition hover:text-zinc-950">
                    인재 채용 (Career)
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h6 className="mb-4 text-[11px] font-bold tracking-widest text-zinc-900 uppercase">
                HEAD OFFICE CS
              </h6>
              <p className="mt-1 text-2xl font-black tracking-tight text-zinc-950">
                1644-0000
              </p>
              <p className="mt-2 text-zinc-500">
                오전 10시 - 오후 5시 (점심시간 12:00 - 13:00)
                <br />
                주말 및 전국 법정 공휴일 안전 휴무
                <br />
                공식 이메일: support@studio-shop.co.kr
              </p>
            </div>
          </div>
          <div className="mx-auto mt-16 flex max-w-7xl flex-col justify-between gap-4 border-t border-zinc-100 pt-8 text-[11px] sm:flex-row">
            <p>© 2026 STUDIO SHOP CREATIVE DIGITAL ENTERPRISE. All rights reserved.</p>
            <div className="flex space-x-6 text-zinc-500">
              <a href="#" className="transition hover:text-zinc-950">
                이용약관
              </a>
              <a
                href="#"
                className="font-bold text-zinc-800 transition hover:text-zinc-950"
              >
                개인정보처리방침
              </a>
              <a href="#" className="transition hover:text-zinc-950">
                소비자피해보상보험
              </a>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
