import os
import re
from dotenv import load_dotenv

# Defensive runtime patch: some google libraries expect
# importlib.metadata.packages_distributions (added in Python 3.10+).
# If running under older Python (3.9), try to patch from the
# importlib_metadata backport so imports won't fail early.
try:
    import importlib
    if not hasattr(importlib.metadata, 'packages_distributions'):
        try:
            import importlib_metadata as _ilmd  # backport package
            importlib.metadata.packages_distributions = _ilmd.packages_distributions
            print('Patched importlib.metadata.packages_distributions from importlib_metadata')
        except Exception:
            # backport not installed; will surface error later with suggestion to upgrade Python
            pass
except Exception:
    pass

load_dotenv()

GEMINI_KEY = os.getenv('GEMINI_API_KEY')
OPENAI_KEY = os.getenv('OPENAI_API_KEY')


def _simple_extractive(text, max_sentences=5):
    """Simple extractive summarizer: split text into sentences and take first N."""
    sentences = re.split(r'(?<=[.!?\n])\s+', text.strip())
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
    
    if not sentences:
        return text[:500] + "..." if len(text) > 500 else text
    
    summary = ' '.join(sentences[:max_sentences])
    return summary


def summarize_text(text, mode='short'):
    """Summarize text using Gemini, fallback to OpenAI, or simple extractive."""
    max_tokens = 300 if mode == 'short' else 500
    max_sentences = 5 if mode == 'short' else 10
    
    # Try Gemini first (defensive): patch importlib metadata if needed and attempt known model ids
    if GEMINI_KEY:
        try:
            # Some google libs expect importlib.metadata.packages_distributions (added in Python 3.10+).
            # If running on older Python (3.9), try to patch from importlib_metadata backport to avoid early failures.
            try:
                import importlib
                if not hasattr(importlib.metadata, 'packages_distributions'):
                    try:
                        import importlib_metadata as ilmd  # backport package
                        importlib.metadata.packages_distributions = ilmd.packages_distributions
                        print('Patched importlib.metadata.packages_distributions from importlib_metadata')
                    except Exception:
                        # If we can't patch, continue and let google client raise a helpful error
                        pass
            except Exception:
                pass

            import google.generativeai as genai
            genai.configure(api_key=GEMINI_KEY)
            import time

            prompt = f"Lütfen aşağıdaki metnin kısa bir Türkçe özetini oluştur. Özet akademik ve net olsun.\n\nMetin:\n{text}"

            # Show available models (if client exposes a listing method) to aid debugging.
            try:
                if hasattr(genai, 'list_models'):
                    models_iter = genai.list_models()
                    models = list(models_iter)
                    print('Gemini: available models:')
                    for m in models:
                        # model is a types.Model object; print name and supported methods if present
                        name = getattr(m, 'name', None)
                        methods = getattr(m, 'supported_generation_methods', None)
                        print(f" - {name}  supported_methods={methods}")
                elif hasattr(genai, 'get_models'):
                    models = genai.get_models()
                    print('Gemini: get_models returned:', models)
            except Exception as list_e:
                # Not fatal; continue to try well-known model ids
                print(f'Gemini list_models/get_models failed: {list_e}')

            # Try a list of common model identifiers used by different client versions.
            candidate_models = [
                'models/gemini-2.5-flash-live',  # Öncelikli: istek sınırı yok
                'models/gemini-2.5-flash',
                'models/gemini-2.5-pro',
                'models/gemini-pro-latest',
                'models/gemini-flash-latest',
                'models/gemini-2.0-flash-001',
            ]
            for m in candidate_models:
                try:
                    # Keep the existing API usage (generate_content) but try different model identifiers.
                    model = genai.GenerativeModel(m)
                    response = model.generate_content(prompt)
                    summary = getattr(response, 'text', None) or str(response)
                    summary = summary.strip()
                    print(f"✓ Gemini ile özet oluşturuldu (model={m})")
                    return summary
                except Exception as inner_e:
                    print(f"Gemini model {m} failed: {inner_e}")
            # If none of the model attempts succeeded, continue to other fallbacks
            print('Gemini: tüm denemeler başarısız oldu, OpenAI / extractive yedeklerine geçiliyor')
        except Exception as e:
            print(f'Gemini call failed: {e}')
            # Fallback devam et
    
    # Try OpenAI as backup
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
    
    # Fallback: simple extractive (ücretsiz, ama daha basit)
    print("⚠ Fallback: Simple extractive özet")
    return _simple_extractive(text, max_sentences=max_sentences)
