import json
import os
import urllib.request
import urllib.error

API_KEY = os.environ.get("GEMINI_API_KEY")

def test_gemini():
    if not API_KEY:
        print("GEMINI_API_KEY is not set.")
        return

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"
    
    data = {
        "contents": [{
            "parts": [{"text": "Hello, this is a test. Reply with 'It works!' if you receive this."}]
        }]
    }
    
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), method="POST")
    req.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read())
            print("Gemini API Test: SUCCESS")
            print("Response:", result["candidates"][0]["content"]["parts"][0]["text"])
    except urllib.error.HTTPError as e:
        print(f"Gemini API Test: FAILED with HTTP {e.code}")
        print("Error details:", e.read().decode())
    except Exception as e:
        print(f"Gemini API Test: FAILED with Exception {e}")

if __name__ == "__main__":
    test_gemini()
