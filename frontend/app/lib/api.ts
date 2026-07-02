// frontend/app/lib/api.ts 또는 apiClient.ts
import axios from "axios";

const apiClient = axios.create({
  // 💡 Next.js 4000번에서 호출하므로 백엔드 포트인 8000번을 정확히 바라봐야 합니다.
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  headers: {
    // ⚠️ [중요] 반드시 s가 붙은 복수형 'headers'여야 합니다! 'header'가 아닙니다.
    "Content-Type": "application/json",
  },
});

export default apiClient;
