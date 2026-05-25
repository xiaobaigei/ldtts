import os
from typing import List, Dict

class SQLGenerator:
    def __init__(self, model: str = "deepseek-chat"):
        # Lazy import to avoid loading openai when not needed
        from openai import OpenAI
        from dotenv import load_dotenv
        
        load_dotenv()
        
        deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        api_key = deepseek_key or openai_key

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        self.model = model
    
    def generate_sql(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    
    def generate_with_correction(self, prompt: str, db_path: str = None, max_retries: int = 3) -> str:
        sql = self.generate_sql(prompt)
        
        if db_path:
            from .evaluator import Evaluator
            for _ in range(max_retries):
                success, result = Evaluator.execute_sql(db_path, sql)
                if success:
                    return sql
                error_msg = str(result)
                correction_prompt = f"Fix the SQL error:\nSQL: {sql}\nError: {error_msg}\nProvide only the corrected SQL:"
                sql = self.generate_sql(correction_prompt)
        
        return sql
