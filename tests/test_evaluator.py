"""Unit tests for Evaluator module"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.evaluator import Evaluator


class TestEvaluator:
    """Test cases for Evaluator metrics"""

    def setup_method(self):
        """Setup test fixtures"""
        self.evaluator = Evaluator()

    def test_execution_accuracy_identical(self):
        """Test EX when queries are identical"""
        sql1 = "SELECT name FROM employees WHERE salary > 50000"
        sql2 = "SELECT name FROM employees WHERE salary > 50000"
        
        result = self.evaluator.execution_accuracy(sql1, sql2)
        
        assert result == 1.0

    def test_execution_accuracy_different(self):
        """Test EX when queries are different"""
        sql1 = "SELECT name FROM employees WHERE salary > 50000"
        sql2 = "SELECT name FROM employees WHERE salary > 60000"
        
        result = self.evaluator.execution_accuracy(sql1, sql2)
        
        assert isinstance(result, (int, float))
        assert 0 <= result <= 1

    def test_exact_set_match(self):
        """Test ESM metric"""
        sql1 = "SELECT name FROM employees"
        sql2 = "SELECT name FROM employees"
        
        result = self.evaluator.exact_set_match(sql1, sql2)
        
        assert result == 1.0

    def test_component_matching(self):
        """Test component matching"""
        sql1 = "SELECT name FROM employees WHERE salary > 50000"
        sql2 = "SELECT name FROM employees WHERE salary > 50000"
        
        result = self.evaluator.component_matching(sql1, sql2)
        
        assert isinstance(result, dict)
        assert "select" in result
        assert "where" in result

    def test_parse_sql_components(self):
        """Test SQL component parsing"""
        sql = "SELECT name FROM employees WHERE salary > 50000 GROUP BY department ORDER BY name"
        
        components = self.evaluator.parse_sql_components(sql)
        
        assert "select" in components
        assert "from" in components
        assert "where" in components
        assert "group_by" in components
        assert "order_by" in components

    def test_evaluate_all(self):
        """Test full evaluation"""
        predictions = [
            "SELECT name FROM employees WHERE salary > 50000",
            "SELECT * FROM departments"
        ]
        references = [
            "SELECT name FROM employees WHERE salary > 50000",
            "SELECT id FROM departments"
        ]
        
        results = self.evaluator.evaluate_all(predictions, references)
        
        assert "ex" in results
        assert "esm" in results
        assert "cm" in results


class TestEvaluatorEdgeCases:
    """Test edge cases for Evaluator"""

    def setup_method(self):
        """Setup test fixtures"""
        self.evaluator = Evaluator()

    def test_empty_sql(self):
        """Test handling of empty SQL"""
        result = self.evaluator.execution_accuracy("", "")
        assert result == 1.0 or result == 0.0

    def test_invalid_sql(self):
        """Test handling of invalid SQL"""
        sql1 = "SELECT FROM employees"
        sql2 = "SELECT name FROM employees"
        
        result = self.evaluator.execution_accuracy(sql1, sql2)
        assert isinstance(result, (int, float))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
