import os
import google.generativeai as genai

def test_gemini():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY is not set.")
        return

    genai.configure(api_key=api_key)
    
    # Instantiate the model
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    try:
        response = model.generate_content("Hello, this is a test. Reply with 'It works!' if you receive this.")
        print("Gemini API SDK Test: SUCCESS")
        print("Response:", response.text)
    except Exception as e:
        print(f"Gemini API SDK Test: FAILED with Exception {e}")

if __name__ == "__main__":
    test_gemini()
