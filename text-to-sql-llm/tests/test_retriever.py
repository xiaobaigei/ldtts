"""Unit tests for ExampleRetriever module"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.retriever import ExampleRetriever
from src.complexity_estimator import ComplexityEstimator


class TestExampleRetriever:
    """Test cases for ExampleRetriever"""

    def setup_method(self):
        """Setup test fixtures"""
        self.retriever = ExampleRetriever()
        self.examples = [
            {
                "question": "What is the salary of John Smith?",
                "sql": "SELECT salary FROM employees WHERE name = 'John Smith'",
                "schema": "employees (id, name, salary)",
                "complexity": "easy"
            },
            {
                "question": "List all departments with budget over 100000",
                "sql": "SELECT name FROM departments WHERE budget > 100000",
                "schema": "departments (id, name, budget)",
                "complexity": "easy"
            },
            {
                "question": "Show employees in the sales department",
                "sql": "SELECT name FROM employees WHERE department = 'Sales'",
                "schema": "employees (name, department)",
                "complexity": "easy"
            },
            {
                "question": "Find the average salary by department",
                "sql": "SELECT department, AVG(salary) FROM employees GROUP BY department",
                "schema": "employees (department, salary)",
                "complexity": "medium"
            },
            {
                "question": "Which department has the highest total budget?",
                "sql": "SELECT name FROM departments ORDER BY budget DESC LIMIT 1",
                "schema": "departments (name, budget)",
                "complexity": "medium"
            },
            {
                "question": "Show departments with average salary greater than overall average",
                "sql": "SELECT d.name FROM departments d JOIN employees e ON d.id = e.dept_id GROUP BY d.name HAVING AVG(e.salary) > (SELECT AVG(salary) FROM employees)",
                "schema": "departments, employees",
                "complexity": "hard"
            }
        ]
        self.retriever.build_index(self.examples)

    def test_build_index(self):
        """Test index building"""
        assert len(self.retriever.examples) == 6

    def test_retrieve_basic(self):
        """Test basic retrieval"""
        question = "What is the salary of Jane Doe?"
        schema_str = "employees (name, salary)"
        
        results = self.retriever.retrieve(question, schema_str, top_k=2)
        
        assert len(results) <= 2
        assert all("question" in r for r in results)

    def test_retrieve_adaptive(self):
        """Test adaptive retrieval with complexity assessment"""
        question = "What is the salary of Jane Doe?"
        schema_str = "employees (name, salary)"
        linked_schema = {"employees": ["name", "salary"]}
        
        results = self.retriever.retrieve_adaptive(question, schema_str, linked_schema)
        
        assert isinstance(results, list)
        assert len(results) >= 1

    def test_jaccard_similarity(self):
        """Test Jaccard similarity calculation"""
        s1 = "What is the salary of John Smith"
        s2 = "What is the salary of Jane Doe"
        
        sim = self.retriever._jaccard_similarity(s1, s2)
        
        assert 0 <= sim <= 1

    def test_complexity_matching(self):
        """Test complexity-based filtering"""
        question = "Find the average salary by department"
        schema_str = "employees (department, salary)"
        
        results = self.retriever.retrieve(question, schema_str, top_k=5, target_complexity="medium")
        
        assert isinstance(results, list)


class TestComplexityEstimator:
    """Test cases for ComplexityEstimator"""

    def setup_method(self):
        """Setup test fixtures"""
        self.estimator = ComplexityEstimator()

    def test_assess_easy(self):
        """Test easy complexity detection"""
        question = "What is the salary of John?"
        schema = {"employees": ["name", "salary"]}
        
        complexity = self.estimator.assess_complexity(question, schema)
        
        assert complexity in ["easy", "medium", "hard", "extra"]

    def test_assess_hard(self):
        """Test hard complexity detection"""
        question = "Find departments where average salary is greater than overall average and have at least 5 employees"
        schema = {"employees": ["salary", "dept_id"], "departments": ["name"]}
        
        complexity = self.estimator.assess_complexity(question, schema)
        
        assert complexity in ["hard", "extra"]

    def test_get_example_count(self):
        """Test example count mapping"""
        assert self.estimator.get_example_count("easy") == 1
        assert self.estimator.get_example_count("medium") == 3
        assert self.estimator.get_example_count("hard") == 5
        assert self.estimator.get_example_count("extra") == 7

    def test_assess_and_get_k(self):
        """Test combined assessment"""
        question = "Which department has the most employees?"
        schema = {"employees": ["department"], "departments": ["name"]}
        
        complexity, k = self.estimator.assess_and_get_k(question, schema)
        
        assert isinstance(complexity, str)
        assert isinstance(k, int)
        assert k >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
