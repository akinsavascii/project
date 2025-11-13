import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

if not GEMINI_KEY:
    print('No GEMINI_API_KEY found in .env')
    raise SystemExit(1)

import google.generativeai as genai

try:
    genai.configure(api_key=GEMINI_KEY)
except Exception as e:
    print('Failed to configure genai:', e)
    raise

try:
    if hasattr(genai, 'list_models'):
        models = list(genai.list_models())
        print(f'Found {len(models)} models:')
        for m in models:
            name = getattr(m, 'name', None)
            methods = getattr(m, 'supported_generation_methods', None)
            print('-', name, 'methods=', methods)
    else:
        print('genai.list_models not available')
except Exception as e:
    print('Error while listing models:', e)
    raise
