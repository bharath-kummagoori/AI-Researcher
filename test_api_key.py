"""
Quick test script to verify your LLM API key works before running AI-Researcher.
Usage: python test_api_key.py
"""
import os
import ssl
import sys

# Bypass SSL verification for corporate proxies
os.environ.setdefault('CURL_CA_BUNDLE', '')
os.environ.setdefault('REQUESTS_CA_BUNDLE', '')
os.environ['PYTHONHTTPSVERIFY'] = '0'
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError:
    pass
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
_original_request = requests.Session.request
def _patched_request(self, *args, **kwargs):
    kwargs.setdefault('verify', False)
    return _original_request(self, *args, **kwargs)
requests.Session.request = _patched_request

from dotenv import load_dotenv

load_dotenv()

def test_gemini():
    key = os.getenv('GEMINI_API_KEY')
    if not key or key == 'your_gemini_api_key_here':
        print("[SKIP] GEMINI_API_KEY not set")
        return False
    print(f"[TEST] Testing Gemini API key: {key[:10]}...")
    try:
        import requests
        # Test: list models
        r = requests.get(
            f"https://generativelanguage.googleapis.com/v1beta/models?key={key}&pageSize=3",
            timeout=10
        )
        if r.status_code == 200:
            models = [m['name'] for m in r.json().get('models', [])]
            print(f"[PASS] Gemini API key works! Available models: {models[:3]}")
            # Test: generate content
            r2 = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}",
                json={"contents": [{"parts": [{"text": "Say hello in one word"}]}]},
                timeout=15
            )
            if r2.status_code == 200:
                text = r2.json()['candidates'][0]['content']['parts'][0]['text']
                print(f"[PASS] Gemini generation works! Response: {text.strip()}")
                return True
            else:
                print(f"[FAIL] Gemini generation failed: {r2.status_code} - {r2.text[:200]}")
                return False
        elif r.status_code == 403:
            print("[FAIL] API key is FORBIDDEN (403). The key doesn't have the Gemini API enabled.")
            print("       Create a new key at: https://aistudio.google.com/apikey")
            return False
        else:
            print(f"[FAIL] Gemini API returned {r.status_code}: {r.text[:200]}")
            return False
    except Exception as e:
        print(f"[FAIL] Gemini test error: {e}")
        return False

def test_groq():
    key = os.getenv('GROQ_API_KEY')
    if not key or key == 'your_groq_api_key_here':
        print("[SKIP] GROQ_API_KEY not set")
        return False
    print(f"[TEST] Testing Groq API key: {key[:10]}...")
    try:
        import requests
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": "Say hello in one word"}], "max_tokens": 10},
            timeout=15
        )
        if r.status_code == 200:
            text = r.json()['choices'][0]['message']['content']
            print(f"[PASS] Groq API key works! Response: {text.strip()}")
            return True
        else:
            print(f"[FAIL] Groq API returned {r.status_code}: {r.text[:200]}")
            return False
    except Exception as e:
        print(f"[FAIL] Groq test error: {e}")
        return False

def test_openai():
    key = os.getenv('OPENAI_API_KEY')
    if not key or key == 'your_openai_api_key':
        print("[SKIP] OPENAI_API_KEY not set")
        return False
    print(f"[TEST] Testing OpenAI API key: {key[:10]}...")
    try:
        import requests
        r = requests.get(
            "https://api.openai.com/v1/models",
            headers={"Authorization": f"Bearer {key}"},
            timeout=10
        )
        if r.status_code == 200:
            print("[PASS] OpenAI API key works!")
            return True
        else:
            print(f"[FAIL] OpenAI API returned {r.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] OpenAI test error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("AI-Researcher API Key Test")
    print("=" * 50)

    model = os.getenv('COMPLETION_MODEL', 'not set')
    print(f"\nConfigured model: {model}\n")

    results = {}
    results['gemini'] = test_gemini()
    print()
    results['groq'] = test_groq()
    print()
    results['openai'] = test_openai()

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)

    working = [k for k, v in results.items() if v]
    if working:
        print(f"\nWorking providers: {', '.join(working)}")
        if 'gemini' in working and 'gemini' in model:
            print("\nYour Gemini setup is ready! Run: python web_ai_researcher.py")
        elif 'groq' in working and 'groq' in model:
            print("\nYour Groq setup is ready! Run: python web_ai_researcher.py")
        elif working:
            provider = working[0]
            if provider == 'gemini':
                print(f"\nTo use Gemini, set in .env:")
                print(f"  COMPLETION_MODEL=gemini/gemini-2.0-flash")
                print(f"  CHEEP_MODEL=gemini/gemini-2.0-flash")
            elif provider == 'groq':
                print(f"\nTo use Groq, set in .env:")
                print(f"  COMPLETION_MODEL=groq/llama-3.3-70b-versatile")
                print(f"  CHEEP_MODEL=groq/llama-3.1-8b-instant")
    else:
        print("\nNo working API keys found!")
        print("\nEasiest free option - Groq:")
        print("  1. Go to https://console.groq.com/keys")
        print("  2. Sign up (free) and create an API key")
        print("  3. Add to .env: GROQ_API_KEY=your_key")
        print("  4. Set in .env: COMPLETION_MODEL=groq/llama-3.3-70b-versatile")
        print("  5. Set in .env: CHEEP_MODEL=groq/llama-3.1-8b-instant")
