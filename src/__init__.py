"""
SQL-Pilot: LLM-Driven Text-to-SQL with Schema-Aware Prompt Optimization

A modular framework for intelligent Text-to-SQL generation using:
- Schema Linking for relevant table/column selection
- Complexity-aware adaptive retrieval
- Structured prompting with few-shot examples
- Execution-based self-correction
- Multi-model ensemble voting
"""

from .schema_linker import SchemaLinker
from .complexity_estimator import ComplexityEstimator
from .retriever import ExampleRetriever
from .sql_generator import SQLGenerator
from .ensemble import EnsembleVoter
from .evaluator import Evaluator
from .pipeline import SQLPilotPipeline, create_pipeline

__version__ = "1.0.0"
__all__ = [
    "SchemaLinker",
    "ComplexityEstimator",
    "ExampleRetriever",
    "SQLGenerator",
    "EnsembleVoter",
    "Evaluator",
    "SQLPilotPipeline",
    "create_pipeline",
]
