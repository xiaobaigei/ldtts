#!/usr/bin/env python3
"""Simple test script for CI/CD"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    print("=" * 50)
    print("Running Simple CI/CD Tests")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    # Test 1: Basic import
    try:
        from src.schema_linker import SchemaLinker
        print("[PASS] Import SchemaLinker")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Import SchemaLinker: {e}")
        failed += 1
    
    # Test 2: Test SchemaLinker
    try:
        linker = SchemaLinker()
        result = linker.get_simplified_schema("What is the salary?", {"employees": ["name", "salary"]})
        assert isinstance(result, dict)
        print("[PASS] SchemaLinker works")
        passed += 1
    except Exception as e:
        print(f"[FAIL] SchemaLinker: {e}")
        failed += 1
    
    # Test 3: Import ComplexityEstimator
    try:
        from src.complexity_estimator import ComplexityEstimator
        print("[PASS] Import ComplexityEstimator")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Import ComplexityEstimator: {e}")
        failed += 1
    
    # Test 4: Test ComplexityEstimator
    try:
        complexity = ComplexityEstimator()
        result, k = complexity.assess_and_get_k("What is the salary?", {"employees": ["name", "salary"]})
        assert result in ["easy", "medium", "hard", "extra"]
        assert isinstance(k, int)
        print("[PASS] ComplexityEstimator works")
        passed += 1
    except Exception as e:
        print(f"[FAIL] ComplexityEstimator: {e}")
        failed += 1
    
    # Test 5: Import Retriever
    try:
        from src.retriever import ExampleRetriever
        print("[PASS] Import ExampleRetriever")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Import ExampleRetriever: {e}")
        failed += 1
    
    # Test 6: Test Retriever
    try:
        retriever = ExampleRetriever()
        examples = retriever.retrieve_adaptive("What is the salary?", "employees", {"employees": ["name", "salary"]})
        assert isinstance(examples, list)
        print("[PASS] ExampleRetriever works")
        passed += 1
    except Exception as e:
        print(f"[FAIL] ExampleRetriever: {e}")
        failed += 1
    
    # Test 7: Import Evaluator
    try:
        from src.evaluator import Evaluator
        print("[PASS] Import Evaluator")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Import Evaluator: {e}")
        failed += 1
    
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50)
    
    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
