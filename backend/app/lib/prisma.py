from dotenv import load_dotenv
import sys
import os

load_dotenv()

generated_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../generated"))
if generated_path not in sys.path:
    sys.path.insert(0, generated_path)

from prisma import Prisma

# 전역에서 돌려쓸 싱글톤 인스턴스 생성
db = Prisma(
    log_queries=True
)