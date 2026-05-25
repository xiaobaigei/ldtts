from src.schema_linker import SchemaLinker
from src.retriever import ExampleRetriever

def main():
    print("Text-to-SQL Demo - OFFLINE MODE")
    print("=" * 60)
    
    linker = SchemaLinker()
    retriever = ExampleRetriever()
    
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
        }
    ]
    
    retriever.build_index(examples)
    
    questions = [
        "What is the salary of Jane Doe?",
        "List all departments",
        "Show employees hired after 2020"
    ]
    
    for question in questions:
        print(f"\nQuestion: {question}")
        
        simplified_schema = linker.get_simplified_schema(question, full_schema)
        print(f"Linked Tables: {list(simplified_schema.keys())}")
        
        retrieved_examples = retriever.retrieve(question, str(simplified_schema), top_k=2)
        print(f"Retrieved Examples: {len(retrieved_examples)}")
        
        for i, ex in enumerate(retrieved_examples):
            print(f"  Example {i+1}: '{ex['question'][:30]}...' -> {ex['sql']}")
        
        print("-" * 60)
    
    print("\nPipeline completed successfully!")
    print("Note: SQL generation step requires OpenAI API key")

if __name__ == "__main__":
    main()
