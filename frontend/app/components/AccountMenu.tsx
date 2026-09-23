"use client";

import Link from "next/link";
import { useAuth } from "../lib/auth-context";

export default function AccountMenu() {
  const { user, isLoading, logout } = useAuth();

  if (isLoading) {
    // 로그인 상태 확인 중에는 레이아웃이 흔들리지 않도록 자리만 차지합니다.
    return <div className="h-4 w-24" aria-hidden="true" />;
  }

  if (!user) {
    return (
      <>
        <Link href="/login" className="text-zinc-400 transition hover:text-black">
          MY PAGE
        </Link>
        <Link href="/login" className="text-zinc-900 hover:underline">
          SIGN IN
        </Link>
      </>
    );
  }

  return (
    <>
      {/* TODO: 전용 마이페이지가 아직 없어서 임시로 주문/결제 페이지에 연결 */}
      <Link href="/order" className="text-zinc-400 transition hover:text-black">
        MY PAGE
      </Link>
      <span className="text-zinc-900">{user.name}님</span>
      <button
        onClick={() => logout()}
        className="text-zinc-400 transition hover:text-black"
      >
        LOGOUT
      </button>
    </>
  );
}
