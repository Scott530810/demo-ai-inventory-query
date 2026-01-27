#!/usr/bin/env python3
"""
簡化版 RAG 測試 - 只測試檢索效果，不使用 LLM
"""

import sys
import requests

API_URL = "http://localhost:8000/query"

# 測試問題（根據型錄實際內容）
TESTS = [
    # 承重查詢（關鍵）
    ("24型擔架床的最大載重", ["180"], True),
    ("Model 25的承重", ["181", "400"], True),
    ("Model 28的載重", ["295", "650"], True),
    ("載重250kg以上的擔架床", ["295"], True),

    # 規格查詢
    ("24型擔架床的長度", ["190"], False),
    ("24型擔架床的寬度", ["51"], False),
    ("Model 25的高度", ["610", "530", "640"], False),

    # 特色查詢
    ("24型擔架床靠背角度", ["7"], False),
    ("24型擔架床高度調整", ["6"], False),
    ("24型擔架床材質", ["鋁合金"], False),

    # 綜合
    ("所有擔架床承重比較", ["180", "181", "295"], True),
]

def test_query(question, expected_keywords, is_critical):
    """測試單個查詢"""
    try:
        response = requests.post(
            API_URL,
            json={
                "question": question,
                "use_llm_answer": False,  # 不使用 LLM，避免超時
                "rag_mode": "rag_only"
            },
            timeout=30
        )

        if response.status_code != 200:
            return False, f"HTTP {response.status_code}", []

        data = response.json()

        if not data.get("success"):
            return False, f"查詢失敗: {data.get('error')}", []

        rag_context = data.get("rag_context", [])
        if not rag_context:
            return False, "無 RAG 檢索結果", []

        # 檢查檢索到的內容是否包含關鍵字
        all_content = " ".join([ctx["content"] for ctx in rag_context])
        found = [kw for kw in expected_keywords if kw in all_content]

        success = len(found) > 0
        return success, f"{len(rag_context)} 個片段", found

    except Exception as e:
        return False, str(e), []


def main():
    print("="*80)
    print("RAG 檢索測試（簡化版）")
    print("="*80)
    print(f"測試模式: RAG Only (不使用 LLM)\n")

    total = 0
    passed = 0
    critical_passed = 0
    critical_total = 0

    for question, expected, is_critical in TESTS:
        total += 1
        if is_critical:
            critical_total += 1

        success, info, found = test_query(question, expected, is_critical)

        marker = "🔴" if is_critical else "  "
        status = "✅" if success else "❌"

        print(f"{marker} [{total}] {question}")
        print(f"    預期: {expected}")
        print(f"    {status} {info}")

        if success:
            passed += 1
            if is_critical:
                critical_passed += 1
            print(f"    找到: {found}")
        else:
            print(f"    失敗原因: {info}")

        print()

    # 統計
    print("="*80)
    print(f"測試統計:")
    print(f"  總數: {total}")
    print(f"  通過: {passed} ({passed/total*100:.1f}%)")
    print(f"  失敗: {total-passed}")
    print(f"\n關鍵測試 (🔴):")
    print(f"  通過: {critical_passed}/{critical_total} ({critical_passed/critical_total*100:.1f}%)")

    # 評估
    print(f"\n評估:")
    pass_rate = passed / total * 100
    if pass_rate >= 90:
        print(f"  {pass_rate:.1f}% - 優秀 🌟")
    elif pass_rate >= 75:
        print(f"  {pass_rate:.1f}% - 良好 ✅")
    elif pass_rate >= 60:
        print(f"  {pass_rate:.1f}% - 及格 ⚠️")
    else:
        print(f"  {pass_rate:.1f}% - 需改進 ❌")

    print("="*80)

    return 0 if critical_passed == critical_total else 1


if __name__ == "__main__":
    sys.exit(main())
