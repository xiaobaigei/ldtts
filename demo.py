import os
from dotenv import load_dotenv
from src.schema_linker import SchemaLinker
from src.retriever import ExampleRetriever
from src.sql_generator import SQLGenerator

def main():
    load_dotenv()
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("Error: DEEPSEEK_API_KEY not found in .env file")
        print("Please create a .env file with DEEPSEEK_API_KEY=your-api-key")
        return
    
    print("Text-to-SQL Demo - LLM-Driven with Schema-Aware Prompt Optimization")
    print("=" * 60)
    
    linker = SchemaLinker()
    retriever = ExampleRetriever()
    generator = SQLGenerator()
    
    full_schema = {
        "employees": ["id", "name", "department", "salary", "hire_date"],
        "departments": ["id", "name", "budget", "manager_id"],
        "projects": ["id", "name", "department_id", "start_date", "end_date"]
    }
    
    examples = [
        {
            "question": "What is the salary of John Smith?",
            "sql": "SELECT salary FROM employees WHERE name = 'John Smith'",
            "schema": "employees (id, name, salary)"
        },
        {
            "question": "List all departments with budget over 100000",
            "sql": "SELECT name FROM departments WHERE budget > 100000",
            "schema": "departments (id, name, budget)"
        },
        {
            "question": "Show employees in the sales department",
            "sql": "SELECT name FROM employees WHERE department = 'Sales'",
            "schema": "employees (name, department)"
        },
        {
            "question": "Find the average salary of employees in each department",
            "sql": "SELECT department, AVG(salary) FROM employees GROUP BY department",
            "schema": "employees (department, salary)"
        },
        {
            "question": "Which department has the highest total budget?",
            "sql": "SELECT name FROM departments ORDER BY budget DESC LIMIT 1",
            "schema": "departments (name, budget)"
        },
        {
            "question": "Count the number of employees hired in each year",
            "sql": "SELECT strftime('%Y', hire_date) as year, COUNT(*) FROM employees GROUP BY year",
            "schema": "employees (hire_date)"
        },
        {
            "question": "Show all projects that started after 2020",
            "sql": "SELECT * FROM projects WHERE start_date > '2020-12-31'",
            "schema": "projects (start_date)"
        }
    ]
    
    retriever.build_index(examples)
    
    questions = [
        "What is the salary of Jane Doe?",
        "List all departments",
        "Show employees hired after 2020",
        "Find the average salary by department",
        "Which department has the most employees?"
    ]
    
    for question in questions:
        print(f"\nQuestion: {question}")
        
        simplified_schema = linker.get_simplified_schema(question, full_schema)
        print(f"Linked Schema: {list(simplified_schema.keys())}")
        
        retrieved_examples = retriever.retrieve_adaptive(
            question, 
            str(simplified_schema),
            simplified_schema
        )
        print(f"Retrieved {len(retrieved_examples)} examples")
        
        sql = generator.generate_sql(question, simplified_schema, retrieved_examples)
        print(f"Generated SQL: {sql}")
        print("-" * 60)

if __name__ == "__main__":
    main()
