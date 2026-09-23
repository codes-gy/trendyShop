"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import apiClient from "./api";

export interface AuthUser {
  id: number;
  email: string;
  name: string;
  role: "USER" | "ADMIN" | "SUPER_ADMIN";
}

interface AuthContextValue {
  user: AuthUser | null;
  isLoading: boolean;
  login: (
    email: string,
    password: string,
  ) => Promise<{ success: boolean; message: string }>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const ACCESS_TOKEN_KEY = "accessToken";
const REFRESH_TOKEN_KEY = "refreshToken";

async function fetchCurrentUser(accessToken: string): Promise<AuthUser> {
  // GET /auth/me는 다른 도메인들과 달리 {success, message, data} 포장 없이
  // UserResponse 필드를 그대로 반환합니다. (백엔드 response_model 설정에 따른 것)
  const res = await apiClient.get<AuthUser>("/auth/me", {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  return res.data;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // 최초 마운트 시 저장된 토큰이 있으면 내 정보를 조회해서 로그인 상태를 복원합니다.
  // (localStorage 접근은 클라이언트 마운트 이후에만 가능하므로, SSR과의 하이드레이션
  // 불일치를 피하려면 이 setState들은 반드시 useEffect 안에서 이뤄져야 합니다.)
  useEffect(() => {
    const accessToken = window.localStorage.getItem(ACCESS_TOKEN_KEY);
    if (!accessToken) {
      // eslint-disable-next-line react-hooks/set-state-in-effect -- 마운트 이후 localStorage 확인 결과를 반영하는 의도된 동작입니다.
      setIsLoading(false);
      return;
    }

    fetchCurrentUser(accessToken)
      .then((currentUser) => {
        setUser(currentUser);
      })
      .catch(() => {
        // 토큰이 만료/무효화된 경우 조용히 로그아웃 상태로 되돌립니다.
        window.localStorage.removeItem(ACCESS_TOKEN_KEY);
        window.localStorage.removeItem(REFRESH_TOKEN_KEY);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const res = await apiClient.post<{
        success: boolean;
        message: string;
        data: { accessToken: string; refreshToken: string };
      }>("/auth/login", { email, password });

      const { accessToken, refreshToken } = res.data.data;
      window.localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
      window.localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);

      const currentUser = await fetchCurrentUser(accessToken);
      setUser(currentUser);

      return { success: true, message: res.data.message };
    } catch (err) {
      const message = extractErrorMessage(err);
      return { success: false, message };
    }
  };

  const logout = async () => {
    const accessToken = window.localStorage.getItem(ACCESS_TOKEN_KEY);
    try {
      if (accessToken) {
        await apiClient.post(
          "/auth/logout",
          {},
          { headers: { Authorization: `Bearer ${accessToken}` } },
        );
      }
    } catch {
      // 백엔드 로그아웃 통신이 실패해도 클라이언트 쪽 토큰은 지웁니다.
    } finally {
      window.localStorage.removeItem(ACCESS_TOKEN_KEY);
      window.localStorage.removeItem(REFRESH_TOKEN_KEY);
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

function extractErrorMessage(err: unknown): string {
  if (
    typeof err === "object" &&
    err !== null &&
    "response" in err &&
    typeof (err as { response?: { data?: { message?: string } } }).response?.data
      ?.message === "string"
  ) {
    return (err as { response: { data: { message: string } } }).response.data.message;
  }
  return "로그인 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.";
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth()는 AuthProvider 내부에서만 사용할 수 있습니다.");
  }
  return ctx;
}
