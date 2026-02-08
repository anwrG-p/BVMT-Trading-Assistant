import google.generativeai as genai
import os

api_key = "AIzaSyD_YIpoubkm_ET4IbTJD4stqKdlzhS58aE"
if not api_key:
    print("No API Key")
else:
    genai.configure(api_key=api_key)
    try:
        print("Listing models...")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)
    except Exception as e:
        print(f"Error: {e}")
