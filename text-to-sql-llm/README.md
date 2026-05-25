# LLM-Driven Text-to-SQL with Schema-Aware Prompt Optimization

A Text-to-SQL system that combines Schema Linking, Few-shot Example Retrieval, and Structured Prompt Generation to improve SQL generation accuracy.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and add your OpenAI API key:

```bash
cp .env.example .env
```

Edit `.env`:
```
OPENAI_API_KEY=your-api-key-here
```

### 3. Run Demo

```bash
python demo.py
```

### 4. Run Tests

```bash
pytest tests/
```

## Project Structure

```
text-to-sql-llm/
├── src/
│   ├── schema_linker.py    # Schema Linking module
│   ├── retriever.py        # Few-shot example retrieval
│   ├── sql_generator.py    # SQL generation with self-correction
│   ├── ensemble.py         # Multi-model ensemble voting
│   └── evaluator.py        # Evaluation metrics
├── tests/                  # Test cases
├── configs/                # Configuration files
├── demo.py                 # Quick demo script
└── requirements.txt        # Dependencies
```

## Pipeline Overview

1. **Schema Linking**: Identify relevant tables/columns from the question
2. **Example Retrieval**: Retrieve similar NL-SQL examples from training data
3. **SQL Generation**: Generate SQL using structured prompts with retrieved examples

## Usage Example

```python
from src import SchemaLinker, ExampleRetriever, SQLGenerator

linker = SchemaLinker()
retriever = ExampleRetriever()
generator = SQLGenerator()

schema = {"employees": ["id", "name", "salary"]}
examples = [{"question": "...", "sql": "...", "schema": "..."}]

retriever.build_index(examples)
simplified_schema = linker.get_simplified_schema("What is John's salary?", schema)
sql = generator.generate_sql("What is John's salary?", simplified_schema)
```
