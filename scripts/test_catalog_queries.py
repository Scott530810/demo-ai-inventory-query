#!/usr/bin/env python3
"""
根據型錄內容設計的 RAG 測試問題
在 Docker 容器中執行，測試 RAG 系統效果
"""

import sys
import requests
import time
from pathlib import Path

# API 端點
API_URL = "http://localhost:8000/query"

# 測試問題組（根據型錄實際內容設計）
TEST_QUERIES = [
    {
        "category": "承重查詢（數值比較）",
        "tests": [
            {
                "question": "載重250kg以上的擔架床有哪些選擇？",
                "expected": ["Model 28: 295kg 符合", "Model 24: 180kg 不符合", "Model 25: 181kg 不符合"],
                "critical": True
            },
            {
                "question": "24型擔架床的最大載重是多少kg？",
                "expected": ["180 KG", "180kg"],
                "critical": True
            },
            {
                "question": "Model 25的承重限制是多少？",
                "expected": ["181 kg", "400 lb"],
                "critical": True
            },
            {
                "question": "Ferno-Flex Roll-in Chair Cot可以承載多重？",
                "expected": ["295 kg", "650 lb"],
                "critical": True
            },
        ]
    },
    {
        "category": "規格查詢（尺寸、重量）",
        "tests": [
            {
                "question": "24型擔架床展開時的長度和寬度是多少？",
                "expected": ["190 CM", "51 CM", "長度", "寬度"],
                "critical": False
            },
            {
                "question": "Model 25折收後的高度是多少？",
                "expected": ["240 mm", "9.5 in", "折收", "高度"],
                "critical": False
            },
            {
                "question": "Model 28的重量是多少？",
                "expected": ["30 kg", "67 lb", "重量"],
                "critical": False
            },
        ]
    },
    {
        "category": "特色功能查詢",
        "tests": [
            {
                "question": "24型擔架床的靠背可以調整幾段角度？",
                "expected": ["7段", "7 段", "靠背角度"],
                "critical": False
            },
            {
                "question": "24型擔架床的高度可以做幾段調整？",
                "expected": ["6段", "6 段", "高度"],
                "critical": False
            },
            {
                "question": "24型擔架床使用什麼材質製造？",
                "expected": ["鋁合金", "輕量化"],
                "critical": False
            },
        ]
    },
    {
        "category": "型號比較",
        "tests": [
            {
                "question": "請比較Model 24和Model 25的主要規格差異",
                "expected": ["24", "25", "承重", "尺寸"],
                "critical": False
            },
            {
                "question": "椅式擔架床和一般型擔架床有什麼不同？",
                "expected": ["椅式", "一般型", "Model 28", "Model 25"],
                "critical": False
            },
        ]
    },
    {
        "category": "綜合查詢",
        "tests": [
            {
                "question": "所有擔架床的承重規格比較",
                "expected": ["180", "181", "295", "Model 24", "Model 25", "Model 28"],
                "critical": True
            },
            {
                "question": "哪個型號最適合搬運重量級病患？",
                "expected": ["Model 28", "295", "Ferno-Flex"],
                "critical": True
            },
        ]
    }
]


def query_api(question: str, use_llm: bool = True, timeout: int = 120):
    """呼叫 API 查詢"""
    try:
        response = requests.post(
            API_URL,
            json={
                "question": question,
                "use_llm_answer": use_llm,
                "rag_mode": "rag_only"
            },
            timeout=timeout
        )
        response.raise_for_status()
        data = response.json()
        return data
    except requests.Timeout:
        return {"error": "請求超時", "timeout": True}
    except requests.exceptions.JSONDecodeError as e:
        return {"error": f"JSON 解析失敗: {e}", "raw_text": response.text[:200]}
    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP 錯誤: {e.response.status_code}", "raw_text": response.text[:200]}
    except Exception as e:
        return {"error": f"請求失敗: {str(e)}"}


def check_answer(answer: str, expected_keywords: list) -> tuple:
    """檢查答案是否包含預期關鍵字"""
    if not answer:
        return False, []

    found = []
    for keyword in expected_keywords:
        if keyword.lower() in answer.lower():
            found.append(keyword)

    return len(found) > 0, found


def main():
    print("="*80)
    print("型錄內容 RAG 測試")
    print("="*80)
    print(f"API: {API_URL}")
    print(f"模式: RAG Only (僅型錄)\n")

    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    timeout_tests = 0
    critical_passed = 0
    critical_failed = 0

    results_summary = []

    for category_group in TEST_QUERIES:
        category = category_group["category"]
        print(f"\n{'='*80}")
        print(f"{category}")
        print(f"{'='*80}\n")

        for test in category_group["tests"]:
            total_tests += 1
            question = test["question"]
            expected = test["expected"]
            is_critical = test.get("critical", False)

            print(f"[{total_tests}] {question}")
            print(f"    預期關鍵字: {', '.join(expected)}")

            # 執行查詢
            result = query_api(question, use_llm=True, timeout=120)

            if result.get("timeout"):
                print(f"    ⏱️  測試超時 (120秒)")
                timeout_tests += 1
                if is_critical:
                    critical_failed += 1
                results_summary.append({
                    "question": question,
                    "status": "TIMEOUT",
                    "critical": is_critical
                })
                print()
                continue

            if "error" in result:
                print(f"    ❌ 錯誤: {result['error']}")
                failed_tests += 1
                if is_critical:
                    critical_failed += 1
                results_summary.append({
                    "question": question,
                    "status": "ERROR",
                    "critical": is_critical,
                    "error": result['error']
                })
                print()
                continue

            # 檢查答案
            answer = result.get("answer", "")
            rag_count = len(result.get("rag_context", []))

            has_match, found_keywords = check_answer(answer, expected)

            if has_match:
                status = "✅ PASS"
                passed_tests += 1
                if is_critical:
                    critical_passed += 1
            else:
                status = "❌ FAIL"
                failed_tests += 1
                if is_critical:
                    critical_failed += 1

            marker = "🔴" if is_critical else "  "
            print(f"    {marker} {status}")
            print(f"    檢索片段: {rag_count}")
            print(f"    找到關鍵字: {found_keywords if found_keywords else '無'}")

            if not has_match:
                print(f"    回答預覽: {answer[:150]}...")

            results_summary.append({
                "question": question,
                "status": "PASS" if has_match else "FAIL",
                "critical": is_critical,
                "found": found_keywords,
                "rag_count": rag_count
            })

            print()
            time.sleep(1)  # 避免請求過快

    # 統計結果
    print(f"\n{'='*80}")
    print("測試統計")
    print(f"{'='*80}")
    print(f"總測試數: {total_tests}")
    print(f"  ✅ 通過: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
    print(f"  ❌ 失敗: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
    print(f"  ⏱️  超時: {timeout_tests} ({timeout_tests/total_tests*100:.1f}%)")
    print(f"\n關鍵測試 (標記 🔴):")
    critical_total = critical_passed + critical_failed
    if critical_total > 0:
        print(f"  通過: {critical_passed}/{critical_total} ({critical_passed/critical_total*100:.1f}%)")
        print(f"  失敗: {critical_failed}/{critical_total}")

    # 失敗案例
    failed_cases = [r for r in results_summary if r["status"] in ["FAIL", "ERROR"]]
    if failed_cases:
        print(f"\n失敗案例分析:")
        for i, case in enumerate(failed_cases, 1):
            marker = "🔴" if case["critical"] else "  "
            print(f"{marker} [{i}] {case['question']}")
            print(f"     狀態: {case['status']}")
            if case["status"] == "ERROR":
                print(f"     錯誤: {case.get('error', 'Unknown')}")

    # 評估結果
    print(f"\n{'='*80}")
    print("評估結果")
    print(f"{'='*80}")

    pass_rate = passed_tests / total_tests * 100
    if pass_rate >= 90:
        grade = "優秀 🌟"
    elif pass_rate >= 75:
        grade = "良好 ✅"
    elif pass_rate >= 60:
        grade = "及格 ⚠️"
    else:
        grade = "需改進 ❌"

    print(f"通過率: {pass_rate:.1f}% - {grade}")

    if critical_total > 0:
        critical_pass_rate = critical_passed / critical_total * 100
        print(f"關鍵測試通過率: {critical_pass_rate:.1f}%")
        if critical_pass_rate < 100:
            print(f"⚠️  關鍵測試未全部通過，需要優先修復！")

    print(f"\n{'='*80}")

    return 0 if critical_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
