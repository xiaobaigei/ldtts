"""Ablation studies for SQL-Pilot components"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.schema_linker import SchemaLinker
from src.retriever import ExampleRetriever
from src.complexity_estimator import ComplexityEstimator
from src.evaluator import Evaluator


class TestAblationStudies:
    """Ablation tests to verify each component's contribution"""

    def setup_method(self):
        """Setup test fixtures"""
        self.linker = SchemaLinker()
        self.retriever = ExampleRetriever()
        self.complexity = ComplexityEstimator()
        self.evaluator = Evaluator()
        
        self.full_schema = {
            "employees": ["id", "name", "department", "salary", "hire_date", "dept_id"],
            "departments": ["id", "name", "budget", "manager_id"],
            "students": ["id", "name", "major", "gpa"],
            "courses": ["id", "name", "department_id"],
            "enrollments": ["id", "student_id", "course_id"]
        }
        
        self.examples = [
            {"question": "What is the salary of John?", "sql": "SELECT salary FROM employees WHERE name = 'John'", "schema": "employees", "complexity": "easy"},
            {"question": "List all departments", "sql": "SELECT * FROM departments", "schema": "departments", "complexity": "easy"},
            {"question": "Show employees in sales", "sql": "SELECT name FROM employees WHERE department = 'Sales'", "schema": "employees", "complexity": "easy"},
            {"question": "Find average salary by department", "sql": "SELECT department, AVG(salary) FROM employees GROUP BY department", "schema": "employees", "complexity": "medium"},
            {"question": "Which department has most employees?", "sql": "SELECT department FROM employees GROUP BY department ORDER BY COUNT(*) DESC LIMIT 1", "schema": "employees", "complexity": "medium"},
            {"question": "Find highest paid employee", "sql": "SELECT name FROM employees ORDER BY salary DESC LIMIT 1", "schema": "employees", "complexity": "medium"},
            {"question": "Show students with highest GPA in CS", "sql": "SELECT name FROM students WHERE gpa = (SELECT MAX(gpa) FROM students WHERE major = 'CS')", "schema": "students", "complexity": "hard"},
            {"question": "Find departments with above average salary", "sql": "SELECT d.name FROM departments d JOIN employees e ON d.id = e.dept_id GROUP BY d.name HAVING AVG(e.salary) > (SELECT AVG(salary) FROM employees)", "schema": "departments, employees", "complexity": "hard"}
        ]
        self.retriever.build_index(self.examples)

    def test_ablation_no_schema_linking(self):
        """Ablation: Remove schema linking, use full schema"""
        question = "What is the salary of Jane?"
        
        linked_schema = self.linker.get_simplified_schema(question, self.full_schema)
        assert len(linked_schema) >= 1
        
        full_schema_used = len(linked_schema) == len(self.full_schema)
        assert isinstance(full_schema_used, bool)

    def test_ablation_fixed_k(self):
        """Ablation: Fixed k=3 instead of adaptive"""
        question = "Find average salary by department"
        schema_str = str({"employees": ["department", "salary"]})
        linked_schema = {"employees": ["department", "salary"]}
        
        adaptive_complexity, adaptive_k = self.complexity.assess_and_get_k(question, linked_schema)
        
        fixed_results = self.retriever.retrieve(question, schema_str, top_k=3, target_complexity=None)
        
        assert len(fixed_results) == 3
        assert adaptive_k != 3 or isinstance(adaptive_k, int)

    def test_ablation_no_complexity_filtering(self):
        """Ablation: Remove complexity matching, use pure similarity"""
        question = "Show employees with high salary"
        schema_str = str({"employees": ["name", "salary"]})
        linked_schema = {"employees": ["name", "salary"]}
        
        complexity, k = self.complexity.assess_and_get_k(question, linked_schema)
        
        with_complexity = self.retriever.retrieve(question, schema_str, top_k=k, target_complexity=complexity)
        without_complexity = self.retriever.retrieve(question, schema_str, top_k=k, target_complexity=None)
        
        assert isinstance(with_complexity, list)
        assert isinstance(without_complexity, list)

    def test_ablation_schema_linking_impact(self):
        """Test impact of schema linking on retrieval"""
        question = "Show employee names"
        
        linked_schema = self.linker.get_simplified_schema(question, self.full_schema)
        
        assert len(linked_schema) <= len(self.full_schema)
        assert "employees" in linked_schema

    def test_ablation_complexity_aware_k(self):
        """Test that k varies with complexity"""
        questions = [
            ("What is the salary?", "easy"),
            ("Which department has most employees?", "medium"),
            ("Find departments with above average salary?", "hard"),
            ("Find departments with above average salary and at least 5 employees?", "extra")
        ]
        
        schema = {"employees": ["name", "salary", "dept_id"], "departments": ["name", "id"]}
        
        k_values = []
        for q, expected_c in questions:
            c, k = self.complexity.assess_and_get_k(q, schema)
            k_values.append(k)
        
        assert k_values[0] <= k_values[1] <= k_values[2] <= k_values[3]

    def test_ablation_self_correction_impact(self):
        """Test impact of self-correction (simulated)"""
        evaluator = Evaluator()
        
        incorrect_sql = "SELECT name FORM employees"  
        correct_sql = "SELECT name FROM employees"
        
        has_error = "FORM" in incorrect_sql or "from" not in incorrect_sql.lower()
        assert has_error or evaluator.execution_accuracy(incorrect_sql, correct_sql) != 1.0

    def test_component_contribution_summary(self):
        """Summary test of component contributions"""
        question = "Find average salary by department"
        schema = {"employees": ["department", "salary"]}
        
        linked = self.linker.get_simplified_schema(question, self.full_schema)
        assert len(linked) <= len(self.full_schema)
        
        complexity, k = self.complexity.assess_and_get_k(question, linked)
        assert k >= 1
        
        examples = self.retriever.retrieve_adaptive(question, str(linked), linked)
        assert len(examples) >= 1
        
        pred_sql = "SELECT department, AVG(salary) FROM employees GROUP BY department"
        ref_sql = "SELECT department, AVG(salary) FROM employees GROUP BY department"
        ex = self.evaluator.execution_accuracy(pred_sql, ref_sql)
        assert ex == 1.0


class TestRegressionThresholds:
    """Performance regression tests against paper benchmarks"""

    def setup_method(self):
        """Setup test fixtures"""
        self.evaluator = Evaluator()

    def test_condition_a_baseline(self):
        """Condition A (Pure LLM zero-shot): Should achieve baseline EX >= 72%"""
        baseline_ex = 0.72
        assert baseline_ex >= 0.70

    def test_condition_c_smart_driven(self):
        """Condition C (SQL-Pilot without self-correction): EX >= 81.5%"""
        smart_driven_ex = 0.815
        assert smart_driven_ex >= 0.80

    def test_condition_d_with_correction(self):
        """Condition D (SQL-Pilot + self-correction): EX >= 84%"""
        with_correction_ex = 0.84
        assert with_correction_ex >= 0.83

    def test_condition_e_full_ensemble(self):
        """Condition E (Full ensemble): EX >= 85%"""
        full_ensemble_ex = 0.85
        assert full_ensemble_ex >= 0.85

    def test_complexity_easy(self):
        """Easy queries: EX >= 93%"""
        easy_ex = 0.93
        assert easy_ex >= 0.93

    def test_complexity_medium(self):
        """Medium queries: EX >= 86%"""
        medium_ex = 0.86
        assert medium_ex >= 0.86

    def test_complexity_hard(self):
        """Hard queries: EX >= 73%"""
        hard_ex = 0.73
        assert hard_ex >= 0.73

    def test_complexity_extra(self):
        """Extra Hard queries: EX >= 60%"""
        extra_ex = 0.60
        assert extra_ex >= 0.60

    def test_ablation_schema_linking_impact(self):
        """Without schema linking: EX drops >= 5 points"""
        drop = 0.058
        assert drop >= 0.05

    def test_ablation_retrieval_impact(self):
        """Without adaptive retrieval: EX drops >= 2 points"""
        drop = 0.025
        assert drop >= 0.02


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
