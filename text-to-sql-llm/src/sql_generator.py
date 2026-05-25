import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

class SQLGenerator:
    def __init__(self, model: str = "deepseek-chat"):
        deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        api_key = deepseek_key or openai_key

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        self.model = model

    def build_prompt(self, question: str, schema: Dict[str, List[str]], examples: List[Dict[str, str]] = None) -> str:
        schema_str = "\n".join([f"Table: {table}\nColumns: {', '.join(columns)}"
                               for table, columns in schema.items()])

        examples_str = ""
        if examples:
            examples_str = "\n\nExamples:\n"
            for i, ex in enumerate(examples, 1):
                examples_str += f"Example {i}:\nQuestion: {ex['question']}\nSQL: {ex['sql']}\n\n"

        prompt = f"""You are a SQL expert. Given a natural language question and database schema, generate a valid SQL query.

Database Schema:
{schema_str}

{examples_str}
Question: {question}

Generate only the SQL query without any explanations. Use SQLite syntax.
"""
        return prompt

    def generate_sql(self, question: str, schema: Dict[str, List[str]], examples: List[Dict[str, str]] = None) -> str:
        prompt = self.build_prompt(question, schema, examples)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a SQL generator that outputs only valid SQLite queries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )

        return response.choices[0].message.content.strip()

    def generate_with_correction(self, question: str, schema: Dict[str, List[str]],
                                examples: List[Dict[str, str]] = None, max_corrections: int = 2) -> str:
        sql = self.generate_sql(question, schema, examples)

        for attempt in range(max_corrections):
            validation = self._validate_sql(sql)
            if validation["valid"]:
                return sql

            prompt = f"""The following SQL has an error: {sql}
Error: {validation.get('error', 'Syntax error')}
Question: {question}
Schema: {schema}

Please fix the SQL query. Output only the corrected SQL.
"""
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a SQL debugger. Fix the SQL query to be valid SQLite."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            sql = response.choices[0].message.content.strip()

        return sql

    def _validate_sql(self, sql: str) -> Dict[str, str]:
        import sqlite3
        try:
            conn = sqlite3.connect(":memory:")
            cursor = conn.cursor()
            cursor.execute(sql)
            return {"valid": True, "error": None}
        except Exception as e:
            return {"valid": False, "error": str(e)}
        finally:
            conn.close()
