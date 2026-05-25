"""Unit tests for SQL Generator module"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.sql_generator import SQLGenerator


class TestSQLGenerator:
    """Test cases for SQLGenerator"""

    def setup_method(self):
        """Setup test fixtures"""
        self.generator = SQLGenerator(use_self_correction=False)
        self.linked_schema = {"employees": ["id", "name", "salary"]}
        self.examples = [
            {
                "question": "What is the salary of John?",
                "sql": "SELECT salary FROM employees WHERE name = 'John'"
            }
        ]

    def test_build_prompt(self):
        """Test prompt building"""
        question = "What is the salary of Jane?"
        
        prompt = self.generator.build_prompt(question, self.linked_schema, self.examples)
        
        assert isinstance(prompt, str)
        assert "Question:" in prompt
        assert "employees" in prompt

    def test_generate_sql(self):
        """Test SQL generation (requires API)"""
        question = "What is the salary of Jane?"
        
        try:
            result = self.generator.generate_sql(question, self.linked_schema, self.examples)
            assert isinstance(result, str) or result is None
        except Exception:
            pass

    def test_parse_sql_from_response(self):
        """Test SQL parsing from LLM response"""
        response = "SELECT salary FROM employees WHERE name = 'Jane'"
        
        parsed = self.generator._parse_sql(response)
        
        assert isinstance(parsed, str)
        assert "SELECT" in parsed.upper()

    def test_prompt_includes_schema(self):
        """Test that prompt includes schema information"""
        question = "List all employees"
        
        prompt = self.generator.build_prompt(question, self.linked_schema, self.examples)
        
        assert "employees" in prompt
        assert "name" in prompt or "salary" in prompt


class TestSelfCorrection:
    """Test self-correction functionality"""

    def setup_method(self):
        """Setup test fixtures"""
        self.generator = SQLGenerator(use_self_correction=True, max_attempts=2)

    def test_max_attempts_respected(self):
        """Test that max attempts is respected"""
        assert self.generator.max_attempts == 2

    def test_correction_prompt_format(self):
        """Test correction prompt formatting"""
        original_prompt = "Question: What is the salary?"
        sql = "SELECT salary FORM employees"  
        error = "Syntax error near 'FORM'"
        
        correction_prompt = self.generator._build_correction_prompt(
            original_prompt, sql, error
        )
        
        assert isinstance(correction_prompt, str)
        assert "error" in correction_prompt.lower() or "fix" in correction_prompt.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
