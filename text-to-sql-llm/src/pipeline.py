"""
SQL-Pilot Pipeline: End-to-End Text-to-SQL System

This module implements the complete SQL-Pilot pipeline as described in the paper:
- Schema Linking: Identify relevant tables and columns
- Complexity Assessment: Evaluate question difficulty
- Adaptive Retrieval: Fetch difficulty-matched examples
- Structured Prompting: Build optimized prompts
- SQL Generation: Generate SQL with self-correction
- Ensemble Voting: Multi-model consensus (optional)
"""

from typing import Dict, List, Optional, Tuple
import os

from .schema_linker import SchemaLinker
from .complexity_estimator import ComplexityEstimator
from .retriever import ExampleRetriever
from .sql_generator import SQLGenerator
from .ensemble import EnsembleVoter
from .evaluator import Evaluator


class SQLPilotPipeline:
    """
    Main pipeline class that orchestrates all modules.
    Implements the SQL-Pilot framework from the paper.
    """

    def __init__(
        self,
        use_ensemble: bool = False,
        use_self_correction: bool = True,
        max_correction_attempts: int = 3
    ):
        """
        Initialize the SQL-Pilot pipeline.

        Args:
            use_ensemble: Whether to use multi-model ensemble voting
            use_self_correction: Whether to enable execution-based self-correction
            max_correction_attempts: Maximum retry attempts for self-correction
        """
        self.linker = SchemaLinker()
        self.complexity_estimator = ComplexityEstimator()
        self.retriever = ExampleRetriever()
        self.generator = SQLGenerator(
            use_self_correction=use_self_correction,
            max_attempts=max_correction_attempts
        )
        self.ensemble = EnsembleVoter() if use_ensemble else None
        self.evaluator = Evaluator()

    def build_index(self, examples: List[Dict[str, str]]):
        """
        Build the retrieval index from training examples.

        Args:
            examples: List of examples with 'question', 'sql', 'schema' keys
        """
        self.retriever.build_index(examples)
        print(f"[Pipeline] Built index with {len(examples)} examples")

    def process(
        self,
        question: str,
        full_schema: Dict[str, List[str]],
        db_path: Optional[str] = None
    ) -> Dict:
        """
        Process a single question through the complete pipeline.

        Args:
            question: Natural language question
            full_schema: Full database schema {table_name: [columns]}
            db_path: Path to SQLite database (for self-correction)

        Returns:
            Dictionary containing:
                - linked_schema: Simplified schema
                - complexity: Question complexity level
                - examples: Retrieved few-shot examples
                - sql: Generated SQL query
                - correction_attempts: Number of self-correction attempts
        """
        result = {
            "question": question,
            "linked_schema": None,
            "complexity": None,
            "example_count": 0,
            "sql": None,
            "correction_attempts": 0
        }

        # Step 1: Schema Linking
        linked_schema = self.linker.get_simplified_schema(question, full_schema)
        result["linked_schema"] = linked_schema
        print(f"[Pipeline] Schema linked: {list(linked_schema.keys())}")

        # Step 2: Complexity Assessment
        complexity, k = self.complexity_estimator.assess_and_get_k(
            question, linked_schema
        )
        result["complexity"] = complexity
        print(f"[Pipeline] Complexity assessed: {complexity} (k={k})")

        # Step 3: Adaptive Retrieval
        schema_str = str(linked_schema)
        examples = self.retriever.retrieve_adaptive(
            question, schema_str, linked_schema
        )
        result["example_count"] = len(examples)
        print(f"[Pipeline] Retrieved {len(examples)} examples")

        # Step 4: SQL Generation
        if self.ensemble and db_path:
            # Use ensemble voting
            sql = self.ensemble.vote(
                question, linked_schema, examples, db_path
            )
            result["sql"] = sql
            result["correction_attempts"] = -1  # Ensemble mode
        else:
            # Use single model generation
            sql = self.generator.generate_sql(
                question, linked_schema, examples, db_path
            )
            result["sql"] = sql
            result["correction_attempts"] = self.generator.attempts

        print(f"[Pipeline] Generated SQL: {result['sql']}")

        return result

    def evaluate(
        self,
        predictions: List[str],
        references: List[str],
        db_path: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Evaluate predictions against references.

        Args:
            predictions: List of predicted SQL queries
            references: List of reference SQL queries
            db_path: Path to database (for execution-based metrics)

        Returns:
            Dictionary with EX, ESM, CM metrics
        """
        return self.evaluator.evaluate_all(predictions, references, db_path)


def create_pipeline(
    use_ensemble: bool = False,
    use_self_correction: bool = True,
    examples: Optional[List[Dict[str, str]]] = None
) -> SQLPilotPipeline:
    """
    Factory function to create a configured pipeline.

    Args:
        use_ensemble: Enable multi-model ensemble
        use_self_correction: Enable self-correction
        examples: Training examples for retrieval index

    Returns:
        Configured SQLPilotPipeline instance
    """
    pipeline = SQLPilotPipeline(
        use_ensemble=use_ensemble,
        use_self_correction=use_self_correction
    )

    if examples:
        pipeline.build_index(examples)

    return pipeline
