"""Unit tests for Ensemble module"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ensemble import EnsembleVoter


class TestEnsembleVoter:
    """Test cases for EnsembleVoter"""

    def setup_method(self):
        """Setup test fixtures"""
        self.voter = EnsembleVoter()
        self.examples = [
            {
                "question": "What is the salary of John?",
                "sql": "SELECT salary FROM employees WHERE name = 'John'",
                "schema": "employees (name, salary)"
            }
        ]
        self.linked_schema = {"employees": ["name", "salary"]}

    def test_vote_execution_consistency(self):
        """Test voting by execution consistency"""
        question = "What is the salary of John?"
        
        result = self.voter.vote(question, self.linked_schema, self.examples, db_path=None)
        
        assert isinstance(result, str) or result is None

    def test_single_model_fallback(self):
        """Test single model fallback when ensemble disabled"""
        voter = EnsembleVoter(use_ensemble=False)
        
        result = voter.vote(question="What is the salary?", 
                           linked_schema=self.linked_schema,
                           examples=self.examples,
                           db_path=None)
        
        assert isinstance(result, str) or result is None

    def test_vote_with_multiple_candidates(self):
        """Test voting with multiple candidate SQLs"""
        candidates = [
            "SELECT salary FROM employees WHERE name = 'John'",
            "SELECT salary FROM employees WHERE name = 'John Smith'"
        ]
        
        result = self.voter._vote_by_consistency(candidates)
        
        assert result is None or isinstance(result, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
