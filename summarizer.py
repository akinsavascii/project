import os
import re
from dotenv import load_dotenv

try:
    import importlib
    if not hasattr(importlib.metadata, 'packages_distributions'):
        try:
            import importlib_metadata as _ilmd
            importlib.metadata.packages_distributions = _ilmd.packages_distributions
            print('Patched importlib.metadata.packages_distributions from importlib_metadata')
        except Exception:
            pass
except Exception:
    pass

load_dotenv()

GEMINI_KEY = os.getenv('GEMINI_API_KEY')
OPENAI_KEY = os.getenv('OPENAI_API_KEY')


def _simple_extractive(text, max_sentences=5):
    sentences = re.split(r'(?<=[.!?\n])\s+', text.strip())
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
    
    if not sentences:
        return text[:500] + "..." if len(text) > 500 else text
    
    summary = ' '.join(sentences[:max_sentences])
    return summary


def summarize_text(text, mode='short'):
    max_tokens = 300 if mode == 'short' else 500
    max_sentences = 5 if mode == 'short' else 10
    
    if GEMINI_KEY:
        try:
            try:
                import importlib
                if not hasattr(importlib.metadata, 'packages_distributions'):
                    try:
                        import importlib_metadata as ilmd
                        importlib.metadata.packages_distributions = ilmd.packages_distributions
                        print('Patched importlib.metadata.packages_distributions from importlib_metadata')
                    except Exception:
                        pass
            except Exception:
                pass

            import google.generativeai as genai
            genai.configure(api_key=GEMINI_KEY)
            import time

            prompt = f"Lütfen aşağıdaki metnin kısa bir Türkçe özetini oluştur. Özet akademik ve net olsun.\n\nMetin:\n{text}"

            try:
                if hasattr(genai, 'list_models'):
                    models_iter = genai.list_models()
                    models = list(models_iter)
                    print('Gemini: available models:')
                    for m in models:
                        name = getattr(m, 'name', None)
                        methods = getattr(m, 'supported_generation_methods', None)
                        print(f" - {name}  supported_methods={methods}")
                elif hasattr(genai, 'get_models'):
                    models = genai.get_models()
                    print('Gemini: get_models returned:', models)
            except Exception as list_e:
                print(f'Gemini list_models/get_models failed: {list_e}')

            candidate_models = [
                'models/gemini-2.5-flash-live',
                'models/gemini-2.5-flash',
                'models/gemini-2.5-pro',
                'models/gemini-pro-latest',
                'models/gemini-flash-latest',
                'models/gemini-2.0-flash-001',
            ]
            for m in candidate_models:
                try:
                    model = genai.GenerativeModel(m)
                    response = model.generate_content(prompt)
                    summary = getattr(response, 'text', None) or str(response)
                    summary = summary.strip()
                    print(f"✓ Gemini ile özet oluşturuldu (model={m})")
                    return summary
                except Exception as inner_e:
                    print(f"Gemini model {m} failed: {inner_e}")
            print('Gemini: tüm denemeler başarısız oldu, OpenAI / extractive yedeklerine geçiliyor')
        except Exception as e:
            print(f'Gemini call failed: {e}')
    
    if OPENAI_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_KEY)
            
            prompt = f"Lütfen aşağıdaki metnin kısa bir Türkçe özetini oluştur. Özet akademik ve net olsun.\n\nMetin:\n{text}"
            
            response = client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=[
                    {"role": "system", "content": "Türkçe dilinde yardımcı bir asistan, kısa ve öz özetler üretir."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=max_tokens
            )
            summary = response.choices[0].message.content.strip()
            print("✓ OpenAI ile özet oluşturuldu")
            return summary
        except Exception as e:
            print(f'OpenAI call failed: {e}')
    
    print("⚠ Fallback: Simple extractive özet")
    return _simple_extractive(text, max_sentences=max_sentences)
