"use client";

import { useState, type FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "../lib/auth-context";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setIsSubmitting(true);

    const result = await login(email, password);

    setIsSubmitting(false);

    if (!result.success) {
      setErrorMessage(result.message);
      return;
    }

    router.push("/");
    router.refresh();
  };

  return (
    <div className="flex min-h-[calc(100vh-140px)] items-center justify-center bg-zinc-50 px-6 py-16">
      <div className="w-full max-w-sm space-y-8">
        <div className="space-y-2 text-center">
          <Link
            href="/"
            className="inline-block text-2xl font-black tracking-tighter text-zinc-900"
          >
            TRNDY<span className="font-light text-zinc-400">.</span>
          </Link>
          <p className="text-sm text-zinc-400">로그인하고 TRNDY를 만나보세요.</p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="space-y-4 rounded-3xl border border-zinc-200/60 bg-white p-8 shadow-sm"
        >
          <div className="space-y-1.5">
            <label htmlFor="email" className="text-xs font-bold text-zinc-500">
              이메일
            </label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="w-full rounded-xl border border-zinc-200 bg-white p-3 text-sm focus:border-zinc-950 focus:outline-none"
            />
          </div>

          <div className="space-y-1.5">
            <label htmlFor="password" className="text-xs font-bold text-zinc-500">
              비밀번호
            </label>
            <input
              id="password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="8자 이상"
              className="w-full rounded-xl border border-zinc-200 bg-white p-3 text-sm focus:border-zinc-950 focus:outline-none"
            />
          </div>

          {errorMessage && (
            <p className="rounded-xl bg-red-50 p-3 text-center text-xs font-semibold text-red-500">
              {errorMessage}
            </p>
          )}

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full rounded-xl bg-zinc-950 py-3.5 text-sm font-bold text-white transition hover:bg-zinc-800 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isSubmitting ? "로그인 중..." : "로그인"}
          </button>

          <p className="text-center text-[11px] text-zinc-400">
            아직 회원이 아니신가요?{" "}
            {/* TODO: 회원가입 페이지가 아직 없어서 다음 단계에서 연결 예정 */}
            <span className="font-semibold text-zinc-600">회원가입</span>
          </p>
        </form>

        <p className="text-center text-[11px] text-zinc-400">
          로컬에서 백엔드(FastAPI)가 함께 실행 중이어야 로그인이 동작합니다.
        </p>
      </div>
    </div>
  );
}
