"use client";

import { useRouter } from "next/navigation";

export default function LogoutButton() {
  const router = useRouter();

  const handleLogout = async () => {
    // 안전장치: 클라이언트에 저장된 토큰 가져오기
    const accessToken = localStorage.getItem("accessToken");

    try {
      // 1. 💡 백엔드 서버에 로그아웃 알리기 (Bearer 헤더 장착)
      if (accessToken) {
        await fetch("http://localhost:8000/auth/logout", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${accessToken}`,
            "Content-Type": "application/json",
          },
        });
      }
    } catch (error) {
      console.error("백엔드 로그아웃 통신 실패:", error);
      // 백엔드가 잠시 죽었더라도 내 컴퓨터의 토큰은 지워야 하므로 catch에서도 진행합니다.
    } finally {
      // 2. 💡 브라우저 저장소(localStorage)에서 토큰 청소하기
      localStorage.removeItem("accessToken");
      localStorage.removeItem("refreshToken");

      // 3. 💡 전역 상태가 있다면 초기화해주고, 로그인 페이지로 강제 리다이렉트
      alert("성공적으로 로그아웃 되었습니다.");
      router.push("/login");
      router.refresh(); // Next.js 세션/페이지 캐시 새로고침
    }
  };

  return (
    <button
      onClick={handleLogout}
      className="rounded bg-red-500 px-4 py-2 text-white transition hover:bg-red-600"
    >
      로그아웃
    </button>
  );
}
