"""LLM categorization quality eval (~200 cases, calls the real OpenAI API).

NOT a CI unit test — non-deterministic and costs money. Run manually for QA:
    .venv/Scripts/python.exe scripts/eval_categorization.py

Measures per-category & overall accuracy of openai_service.parse_line, plus
direction sanity for income. Writes a UTF-8 report to scripts/eval_report.md.
"""

import io
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services import openai_service  # noqa: E402

TODAY = date(2026, 6, 2)
CATS = [
    "식비", "카페/간식", "교통", "생활/마트", "쇼핑", "문화/여가",
    "건강/의료", "주거/통신", "경조사", "교육", "기타지출", "수입",
]

CASES: dict[str, list[str]] = {
    "식비": [
        "맥날 6000", "맥날 만이천원", "김밥천국 5500", "점심 백반 9000",
        "배달 치킨 23000", "삼겹살 18000", "분식 떡볶이 4000", "국밥 8천원",
        "버거킹 7500", "롯데리아 6800", "김치찌개 8000", "짜장면 7000",
        "회식 삼겹살 5만원", "도시락 5500", "배달의민족 19000", "쌀국수 11000",
        "피자 25000", "초밥 32000", "어제 점심 김밥 4500",
    ],
    "카페/간식": [
        "스벅 아메리카노 4900", "스벅 라떼 5천원", "투썸 6500", "메가커피 2000",
        "빽다방 1500", "베스킨라빈스 6000", "이디야 3500", "공차 4800",
        "컴포즈커피 1800", "던킨 5000", "카페 디저트 12000", "아이스크림 3000",
        "마카롱 4500", "커피 한잔 4000", "스벅 6천원", "투썸 케이크 7500",
    ],
    "교통": [
        "택시 12000", "어제 택시 만오천원", "버스카드 충전 50000", "지하철 1400",
        "KTX 표 47000", "주유 60000", "카카오택시 8000", "시외버스 23000",
        "톨게이트 4500", "주차비 6000", "기차표 38000", "따릉이 1000",
        "항공권 89000", "버스 1500", "고속버스 18000", "택시비 9천원",
    ],
    "생활/마트": [
        "이마트 32000", "편의점 3000", "홈플러스 45000", "쿠팡 생필품 28000",
        "세제 구입 9000", "마트 장보기 54000", "휴지 8000", "생수 한박스 12000",
        "노브랜드 21000", "GS25 4500", "CU 3200", "코스트코 87000",
        "주방세제 5500", "건전지 4000", "다이소 5000", "장보기 3만원",
    ],
    "쇼핑": [
        "올리브영 23000", "무신사 옷 59000", "자라 79000", "신발 89000",
        "화장품 34000", "유니클로 39000", "가방 120000", "나이키 운동화 110000",
        "악세사리 25000", "향수 78000", "후드티 45000", "청바지 69000",
        "에어팟 199000", "원피스 55000", "모자 19000", "아이폰 케이스 15000",
    ],
    "문화/여가": [
        "영화 15000", "CGV 14000", "넷플릭스 13500", "노래방 20000", "볼링 18000",
        "콘서트 99000", "메가박스 13000", "PC방 5000", "전시회 18000",
        "유튜브 프리미엄 14900", "스팀 게임 49000", "방탈출 22000", "당구장 15000",
        "뮤지컬 110000", "디즈니플러스 9900", "놀이공원 56000",
    ],
    "건강/의료": [
        "약국 8000", "병원 진료 5000", "치과 120000", "한의원 30000", "영양제 45000",
        "감기약 6000", "안과 25000", "피부과 80000", "비타민 32000",
        "정형외과 15000", "건강검진 150000", "산부인과 40000", "처방약 4500",
        "내과 진료 7000",
    ],
    "주거/통신": [
        "월세 500000", "전기요금 45000", "휴대폰 요금 66000", "인터넷 33000",
        "가스비 28000", "관리비 120000", "수도요금 18000", "통신비 55000",
        "도시가스 32000", "월세 60만원", "전기세 5만원", "와이파이 33000",
        "핸드폰 요금 7만원", "아파트 관리비 15만원",
    ],
    "경조사": [
        "결혼식 축의금 100000", "부조금 50000", "조의금 50000", "돌잔치 100000",
        "결혼 축하금 200000", "집들이 선물 40000", "화환 80000", "회갑 50000",
        "졸업선물 30000", "생일선물 30000", "축의금 10만원", "조의금 5만원",
    ],
    "교육": [
        "학원비 200000", "인강 99000", "토익 응시료 48000", "교재 18000",
        "과외비 300000", "온라인 강의 55000", "책 구입 18000", "자격증 시험 60000",
        "영어학원 250000", "문제집 22000", "수강료 180000", "세미나 50000",
        "학원 30만원",
    ],
    "기타지출": [
        "후원 10000", "기부 20000", "회비 30000", "벌금 40000", "수수료 1500",
        "택배비 3000", "모임 회비 25000", "기부금 100000", "송금 수수료 500",
        "연체료 8000",
    ],
    "수입": [
        "월급 3500000", "용돈 20만원", "환급 50000", "부수입 150000", "지원금 250000",
        "급여 4000000", "상여금 1000000", "알바비 800000", "이자 12000",
        "세금환급 230000", "보너스 50만원", "중고거래 판매 45000", "배당금 80000",
        "월급 350만원",
    ],
}

# extra acceptable categories for genuinely ambiguous inputs
ACCEPT_EXTRA: dict[str, set[str]] = {
    "맥날 6000": {"카페/간식"}, "맥날 만이천원": {"카페/간식"},
    "버거킹 7500": {"카페/간식"}, "롯데리아 6800": {"카페/간식"},
    "베스킨라빈스 6000": {"식비"}, "던킨 5000": {"식비"}, "아이스크림 3000": {"식비"},
    "마카롱 4500": {"식비"}, "투썸 케이크 7500": {"식비"},
    "다이소 5000": {"쇼핑"}, "쿠팡 생필품 28000": {"쇼핑"}, "건전지 4000": {"쇼핑"},
    "아이폰 케이스 15000": {"생활/마트"}, "에어팟 199000": {"생활/마트"},
    "향수 78000": {"건강/의료"}, "화장품 34000": {"건강/의료"},
    "교재 18000": {"문화/여가", "쇼핑"}, "책 구입 18000": {"문화/여가", "쇼핑"},
    "문제집 22000": {"문화/여가", "쇼핑"},
    "생일선물 30000": {"쇼핑"}, "졸업선물 30000": {"쇼핑"}, "집들이 선물 40000": {"쇼핑"},
    "화환 80000": {"생활/마트"},
    "영양제 45000": {"생활/마트"}, "비타민 32000": {"생활/마트"}, "마스크 10000": {"생활/마트"},
    "택배비 3000": {"쇼핑"},
    "중고거래 판매 45000": set(),  # strictly income
    "놀이공원 56000": set(),
}


def _accept(intended: str, text: str) -> set[str]:
    return {intended} | ACCEPT_EXTRA.get(text, set())


def _eval_one(intended: str, text: str) -> dict:
    try:
        r = openai_service.parse_line(text, CATS, TODAY)
        pred = r.get("category")
        ok = pred in _accept(intended, text)
        income_ok = intended != "수입" or r.get("direction") == "income"
        return {"intended": intended, "text": text, "pred": pred,
                "conf": r.get("confidence"), "ok": ok and income_ok,
                "dir": r.get("direction"), "err": None}
    except Exception as e:  # noqa: BLE001
        return {"intended": intended, "text": text, "pred": None, "conf": None,
                "ok": False, "dir": None, "err": str(e)[:120]}


def main() -> None:
    jobs = [(cat, t) for cat, lines in CASES.items() for t in lines]
    with ThreadPoolExecutor(max_workers=10) as pool:
        results = list(pool.map(lambda a: _eval_one(*a), jobs))

    path = os.path.join(os.path.dirname(__file__), "eval_report.md")
    out = io.open(path, "w", encoding="utf-8")
    total_ok = sum(1 for r in results if r["ok"])
    out.write(f"# 분류 정확도 eval — {total_ok}/{len(results)} "
              f"({total_ok / len(results) * 100:.1f}%)\n\n")

    by_cat: dict[str, list[dict]] = {}
    for r in results:
        by_cat.setdefault(r["intended"], []).append(r)

    out.write("## 카테고리별 정확도\n\n| 카테고리 | 정확도 |\n|---|---|\n")
    for cat in CASES:
        rs = by_cat[cat]
        ok = sum(1 for r in rs if r["ok"])
        out.write(f"| {cat} | {ok}/{len(rs)} |\n")

    fails = [r for r in results if not r["ok"]]
    out.write(f"\n## 실패 케이스 ({len(fails)})\n\n")
    for r in fails:
        if r["err"]:
            out.write(f"- ERROR `{r['text']}` (기대 {r['intended']}) → {r['err']}\n")
        else:
            out.write(f"- `{r['text']}` 기대=**{r['intended']}** 예측=**{r['pred']}** "
                      f"(conf {r['conf']}, dir {r['dir']})\n")
    out.close()

    print(f"OVERALL {total_ok}/{len(results)} = {total_ok / len(results) * 100:.1f}%")
    print(f"FAILS: {len(fails)}")
    for cat in CASES:
        rs = by_cat[cat]
        ok = sum(1 for r in rs if r["ok"])
        if ok < len(rs):
            print(f"  {cat}: {ok}/{len(rs)}")
    print("report: scripts/eval_report.md")


if __name__ == "__main__":
    main()
