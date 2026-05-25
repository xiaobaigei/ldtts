"""Unit tests for SchemaLinker module"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.schema_linker import SchemaLinker


class TestSchemaLinker:
    """Test cases for SchemaLinker"""

    def setup_method(self):
        """Setup test fixtures"""
        self.linker = SchemaLinker()
        self.full_schema = {
            "employees": ["id", "name", "department", "salary", "hire_date", "dept_id"],
            "departments": ["id", "name", "budget", "manager_id"],
            "projects": ["id", "name", "department_id", "start_date", "end_date"],
            "salaries": ["id", "employee_id", "amount", "pay_date"]
        }

    def test_link_schema_basic(self):
        """Test basic schema linking"""
        question = "What is the salary of Jane Doe?"
        result = self.linker.link_schema(question, self.full_schema)
        
        assert isinstance(result, dict)
        assert "tables" in result
        assert "columns" in result

    def test_get_simplified_schema(self):
        """Test simplified schema extraction"""
        question = "Show employees hired after 2020"
        result = self.linker.get_simplified_schema(question, self.full_schema)
        
        assert isinstance(result, dict)
        assert "employees" in result

    def test_jaccard_matching(self):
        """Test Jaccard similarity matching"""
        question_tokens = ["salary", "employee"]
        table_names = ["employees", "departments", "projects"]
        
        matches = self.linker._match_tables(question_tokens, table_names)
        assert isinstance(matches, list)
        assert len(matches) <= len(table_names)

    def test_empty_question(self):
        """Test handling of empty question"""
        result = self.linker.link_schema("", self.full_schema)
        assert result["tables"] == [] or len(result["tables"]) == 0

    def test_complex_question(self):
        """Test complex question with multiple tables"""
        question = "Show employees in the sales department with salary greater than 50000"
        result = self.linker.link_schema(question, self.full_schema)
        
        assert "employees" in result["tables"]
        assert len(result["tables"]) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
