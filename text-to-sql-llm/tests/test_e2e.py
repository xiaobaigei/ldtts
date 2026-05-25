"""End-to-end integration tests for SQL-Pilot pipeline"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.schema_linker import SchemaLinker
from src.retriever import ExampleRetriever
from src.complexity_estimator import ComplexityEstimator
from src.evaluator import Evaluator


class TestEndToEnd:
    """End-to-end test cases based on paper case studies"""

    def __init__(self):
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
            "enrollments": ["id", "student_id", "course_id"],
            "professors": ["id", "name", "dept_id"]
        }
        
        self.examples = [
            {
                "question": "What is the salary of John Smith?",
                "sql": "SELECT salary FROM employees WHERE name = 'John Smith'",
                "schema": "employees (name, salary)",
                "complexity": "easy"
            },
            {
                "question": "List all departments",
                "sql": "SELECT * FROM departments",
                "schema": "departments",
                "complexity": "easy"
            },
            {
                "question": "Show employees hired after 2020",
                "sql": "SELECT name FROM employees WHERE hire_date > '2020-12-31'",
                "schema": "employees (hire_date)",
                "complexity": "easy"
            },
            {
                "question": "Find the average salary by department",
                "sql": "SELECT department, AVG(salary) FROM employees GROUP BY department",
                "schema": "employees (department, salary)",
                "complexity": "medium"
            },
            {
                "question": "Which department has the most employees?",
                "sql": "SELECT department FROM employees GROUP BY department ORDER BY COUNT(*) DESC LIMIT 1",
                "schema": "employees (department)",
                "complexity": "medium"
            },
            {
                "question": "Show names of students with highest GPA in Computer Science",
                "sql": "SELECT name FROM students WHERE gpa = (SELECT MAX(gpa) FROM students WHERE major = 'Computer Science')",
                "schema": "students (name, major, gpa)",
                "complexity": "hard"
            },
            {
                "question": "Find departments with average salary greater than overall average",
                "sql": "SELECT d.name FROM departments d JOIN employees e ON d.id = e.dept_id GROUP BY d.name HAVING AVG(e.salary) > (SELECT AVG(salary) FROM employees)",
                "schema": "departments, employees",
                "complexity": "hard"
            }
        ]
        self.retriever.build_index(self.examples)

    def test_case_study_1_join(self):
        """Test Case 1: Easy/Medium JOIN query"""
        question = "List the names of all employees who work in the 'Research' department and have a salary greater than 50000"
        
        linked_schema = self.linker.get_simplified_schema(question, self.full_schema)
        assert "employees" in linked_schema or len(linked_schema) >= 1
        
        complexity, k = self.complexity.assess_and_get_k(question, linked_schema)
        assert complexity in ["easy", "medium", "hard", "extra"]
        assert k >= 1
        return True

    def test_case_study_2_nested_subquery(self):
        """Test Case 2: Nested subquery (Hard)"""
        question = "Show the name of the student who has the highest GPA among all students majoring in Computer Science"
        
        linked_schema = self.linker.get_simplified_schema(question, self.full_schema)
        assert "students" in linked_schema
        
        examples = self.retriever.retrieve_adaptive(question, str(linked_schema), linked_schema)
        assert len(examples) >= 1
        return True

    def test_case_study_3_having_subquery(self):
        """Test Case 3: HAVING with subquery (Extra Hard)"""
        question = "Find the departments where the average salary of employees is greater than the overall average salary across all departments, and the department has at least 5 employees"
        
        linked_schema = self.linker.get_simplified_schema(question, self.full_schema)
        complexity, k = self.complexity.assess_and_get_k(question, linked_schema)
        
        assert complexity in ["hard", "extra"]
        assert k >= 5
        return True

    def test_case_study_4_where_vs_having(self):
        """Test Case 4: WHERE vs HAVING ambiguity (Medium)"""
        question = "Show departments with their professor count"
        
        linked_schema = self.linker.get_simplified_schema(question, self.full_schema)
        complexity, k = self.complexity.assess_and_get_k(question, linked_schema)
        
        assert isinstance(linked_schema, dict)
        assert len(linked_schema) >= 1
        assert complexity in ["easy", "medium", "hard"]
        assert k >= 1
        return True

    def test_case_study_5_multi_table_aggregation(self):
        """Test Case 5: Multi-table aggregation (Medium)"""
        question = "Show students and their enrolled courses"
        
        linked_schema = self.linker.get_simplified_schema(question, self.full_schema)
        complexity, k = self.complexity.assess_and_get_k(question, linked_schema)
        
        assert isinstance(linked_schema, dict)
        assert len(linked_schema) >= 1
        assert isinstance(complexity, str)
        assert isinstance(k, int)
        return True

    def test_pipeline_integration(self):
        """Test full pipeline integration"""
        question = "What is the salary of Jane Doe?"
        
        linked_schema = self.linker.get_simplified_schema(question, self.full_schema)
        assert isinstance(linked_schema, dict)
        assert len(linked_schema) >= 1
        
        complexity, k = self.complexity.assess_and_get_k(question, linked_schema)
        assert isinstance(complexity, str)
        assert isinstance(k, int)
        
        examples = self.retriever.retrieve_adaptive(question, str(linked_schema), linked_schema)
        assert isinstance(examples, list)
        return True

    def test_complexity分层(self):
        """Test complexity stratification"""
        easy_q = "What is the salary of John?"
        medium_q = "Which department has the most employees?"
        hard_q = "Find departments with average salary greater than overall average"
        extra_q = "Find departments where average salary is greater than overall average and have at least 5 employees"
        
        schema = {"employees": ["name", "salary", "dept_id"], "departments": ["name", "id"]}
        
        easy_c, _ = self.complexity.assess_and_get_k(easy_q, schema)
        medium_c, _ = self.complexity.assess_and_get_k(medium_q, schema)
        hard_c, _ = self.complexity.assess_and_get_k(hard_q, schema)
        extra_c, _ = self.complexity.assess_and_get_k(extra_q, schema)
        
        complexity_order = {"easy": 0, "medium": 1, "hard": 2, "extra": 3}
        assert complexity_order[easy_c] <= complexity_order[medium_c]
        assert complexity_order[medium_c] <= complexity_order[hard_c]
        assert complexity_order[hard_c] <= complexity_order[extra_c]
        return True

    def test_evaluator_integration(self):
        """Test evaluator integration"""
        pred_sql = "SELECT name FROM employees WHERE salary > 50000"
        ref_sql = "SELECT name FROM employees WHERE salary > 50000"
        
        cm = self.evaluator.component_match(pred_sql, ref_sql)
        
        assert cm["select"] == True
        assert cm["from"] == True
        assert cm["where"] == True
        return True

    def test_schema_linking_reduces_noise(self):
        """Test that schema linking reduces input noise"""
        question = "Show employee names and salaries"
        
        linked_schema = self.linker.get_simplified_schema(question, self.full_schema)
        
        assert len(linked_schema) <= len(self.full_schema)
        assert "employees" in linked_schema
        return True


def run_tests():
    """Run all tests and print results"""
    print("=" * 60)
    print("Running End-to-End Integration Tests")
    print("=" * 60)
    
    test = TestEndToEnd()
    passed = 0
    failed = 0
    
    test_methods = [
        ("test_case_study_1_join", "Case Study 1: JOIN Query"),
        ("test_case_study_2_nested_subquery", "Case Study 2: Nested Subquery"),
        ("test_case_study_3_having_subquery", "Case Study 3: HAVING with Subquery"),
        ("test_case_study_4_where_vs_having", "Case Study 4: WHERE vs HAVING"),
        ("test_case_study_5_multi_table_aggregation", "Case Study 5: Multi-table Aggregation"),
        ("test_pipeline_integration", "Pipeline Integration"),
        ("test_complexity分层", "Complexity Stratification"),
        ("test_evaluator_integration", "Evaluator Integration"),
        ("test_schema_linking_reduces_noise", "Schema Linking Noise Reduction")
    ]
    
    for method_name, description in test_methods:
        try:
            method = getattr(test, method_name)
            method()
            print("[PASS] " + description)
            passed += 1
        except AssertionError as e:
            print("[FAIL] " + description)
            print("  Error: " + str(e))
            failed += 1
        except Exception as e:
            print("[ERROR] " + description)
            print("  Exception: " + str(e))
            failed += 1
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
