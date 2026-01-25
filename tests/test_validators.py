"""
Unit tests for validators module
測試 SQL 清理和驗證功能
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ambulance_inventory.utils.validators import clean_sql, validate_sql, is_dangerous_sql


class TestCleanSql:
    """測試 clean_sql 函數"""

    def test_clean_markdown_code_block(self):
        """測試移除 Markdown 程式碼區塊"""
        sql = "```sql\nSELECT * FROM inventory\n```"
        result = clean_sql(sql)
        assert result == "SELECT * FROM inventory"

    def test_clean_angle_brackets(self):
        """測試移除角括號包裹（某些模型輸出格式）"""
        sql = "<SELECT * FROM inventory WHERE stock > 0>"
        result = clean_sql(sql)
        assert result == "SELECT * FROM inventory WHERE stock > 0"

    def test_clean_sql_tags(self):
        """測試移除 <sql> 標籤"""
        sql = "<sql>SELECT * FROM inventory</sql>"
        result = clean_sql(sql)
        assert result == "SELECT * FROM inventory"

    def test_clean_query_tags(self):
        """測試移除 <query> 標籤"""
        sql = "<query>SELECT * FROM inventory</query>"
        result = clean_sql(sql)
        assert result == "SELECT * FROM inventory"

    def test_clean_quotes(self):
        """測試移除引號包裹"""
        sql = '"SELECT * FROM inventory"'
        result = clean_sql(sql)
        assert result == "SELECT * FROM inventory"

    def test_clean_single_quotes(self):
        """測試移除單引號包裹"""
        sql = "'SELECT * FROM inventory'"
        result = clean_sql(sql)
        assert result == "SELECT * FROM inventory"

    def test_clean_complex_model_output(self):
        """測試複雜的模型輸出格式"""
        sql = """```sql
<SELECT product_id, product_name, category, brand, model, specifications,
stock_quantity, unit_price, supplier, last_updated
FROM inventory
WHERE stock_quantity > 0
ORDER BY stock_quantity DESC
LIMIT 50>
```"""
        result = clean_sql(sql)
        assert result.startswith("SELECT")
        assert "FROM inventory" in result
        assert not result.startswith("<")
        assert not result.endswith(">")

    def test_preserve_valid_sql(self):
        """測試保留有效的 SQL"""
        sql = "SELECT * FROM inventory WHERE stock_quantity > 0"
        result = clean_sql(sql)
        assert result == sql

    def test_multiline_sql(self):
        """測試多行 SQL"""
        sql = """SELECT product_id, product_name
FROM inventory
WHERE stock_quantity > 0
ORDER BY product_id"""
        result = clean_sql(sql)
        assert "SELECT" in result
        assert "FROM inventory" in result
        assert "WHERE" in result
        assert "ORDER BY" in result


class TestValidateSql:
    """測試 validate_sql 函數"""

    def test_valid_select(self):
        """測試有效的 SELECT 查詢"""
        sql = "SELECT * FROM inventory"
        is_valid, error = validate_sql(sql)
        assert is_valid is True
        assert error == ""

    def test_empty_sql(self):
        """測試空 SQL"""
        is_valid, error = validate_sql("")
        assert is_valid is False
        assert "為空" in error

    def test_non_select_query(self):
        """測試非 SELECT 查詢"""
        sql = "UPDATE inventory SET stock_quantity = 0"
        is_valid, error = validate_sql(sql)
        assert is_valid is False
        assert "SELECT" in error

    def test_missing_from(self):
        """測試缺少 FROM 子句"""
        sql = "SELECT 1 + 1"
        is_valid, error = validate_sql(sql)
        assert is_valid is False
        assert "FROM" in error

    def test_unbalanced_parentheses(self):
        """測試括號不匹配"""
        sql = "SELECT * FROM inventory WHERE (stock_quantity > 0"
        is_valid, error = validate_sql(sql)
        assert is_valid is False
        assert "括號" in error

    def test_select_with_subquery(self):
        """測試帶子查詢的 SELECT"""
        sql = "SELECT * FROM inventory WHERE category IN (SELECT category FROM categories)"
        is_valid, error = validate_sql(sql)
        assert is_valid is True


class TestIsDangerousSql:
    """測試 is_dangerous_sql 函數"""

    def test_drop_table(self):
        """測試 DROP TABLE"""
        sql = "DROP TABLE inventory"
        is_dangerous, reason = is_dangerous_sql(sql)
        assert is_dangerous is True
        assert "DROP" in reason

    def test_delete_from(self):
        """測試 DELETE"""
        sql = "DELETE FROM inventory WHERE id = 1"
        is_dangerous, reason = is_dangerous_sql(sql)
        assert is_dangerous is True
        assert "DELETE" in reason

    def test_update(self):
        """測試 UPDATE"""
        sql = "UPDATE inventory SET stock_quantity = 0"
        is_dangerous, reason = is_dangerous_sql(sql)
        assert is_dangerous is True
        assert "UPDATE" in reason

    def test_insert(self):
        """測試 INSERT"""
        sql = "INSERT INTO inventory VALUES (1, 'test')"
        is_dangerous, reason = is_dangerous_sql(sql)
        assert is_dangerous is True
        assert "INSERT" in reason

    def test_truncate(self):
        """測試 TRUNCATE"""
        sql = "TRUNCATE TABLE inventory"
        is_dangerous, reason = is_dangerous_sql(sql)
        assert is_dangerous is True
        assert "TRUNCATE" in reason

    def test_multiple_statements(self):
        """測試多個 SQL 語句（SQL 注入）"""
        # 測試不含危險關鍵字的多語句
        sql = "SELECT * FROM inventory; SELECT * FROM products;"
        is_dangerous, reason = is_dangerous_sql(sql)
        assert is_dangerous is True
        assert "多個" in reason

    def test_multiple_statements_with_dangerous_keyword(self):
        """測試含危險關鍵字的多語句"""
        sql = "SELECT * FROM inventory; DROP TABLE inventory;"
        is_dangerous, reason = is_dangerous_sql(sql)
        assert is_dangerous is True
        # 可能是 DROP 或多個語句，兩者都是危險的
        assert "DROP" in reason or "多個" in reason

    def test_sql_comment(self):
        """測試 SQL 註解"""
        sql = "SELECT * FROM inventory -- WHERE id = 1"
        is_dangerous, reason = is_dangerous_sql(sql)
        assert is_dangerous is True
        assert "註解" in reason

    def test_safe_select(self):
        """測試安全的 SELECT"""
        sql = "SELECT * FROM inventory WHERE stock_quantity > 0"
        is_dangerous, reason = is_dangerous_sql(sql)
        assert is_dangerous is False
        assert reason == ""

    def test_keyword_in_string_is_safe(self):
        """測試關鍵字在欄位名稱中是安全的"""
        # 'updated' contains 'update' but should be safe
        sql = "SELECT last_updated FROM inventory"
        is_dangerous, reason = is_dangerous_sql(sql)
        # This should be safe because UPDATE is checked as a word boundary
        assert is_dangerous is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
