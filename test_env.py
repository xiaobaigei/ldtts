import os
from dotenv import load_dotenv

load_dotenv()

print("=== Environment Variables ===")
print(f"DEEPSEEK_API_KEY exists: {'DEEPSEEK_API_KEY' in os.environ}")
print(f"DEEPSEEK_API_KEY value: '{os.environ.get('DEEPSEEK_API_KEY', 'NOT FOUND')}'")
print(f"OPENAI_API_KEY exists: {'OPENAI_API_KEY' in os.environ}")
print(f"OPENAI_API_KEY value: '{os.environ.get('OPENAI_API_KEY', 'NOT FOUND')}'")

deepseek_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
print(f"\nDEEPSEEK_API_KEY after strip: '{deepseek_key}'")
print(f"Is deepseek_key empty? {deepseek_key == ''}")
