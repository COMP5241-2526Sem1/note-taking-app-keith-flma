# import libraries
import os
from dotenv import load_dotenv

load_dotenv()  # Loads environment variables from .env

# Check for API keys - prioritize Hugging Face
hf_api_key = os.getenv("HF_API_KEY")
api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GITHUB_TOKEN")

# Determine which LLM provider to use
use_huggingface = bool(hf_api_key)

# Determine which model to use
if use_huggingface:
    # Using Hugging Face
    default_model = os.getenv("HF_MODEL", "google/flan-t5-large")
elif os.getenv("GITHUB_TOKEN") and not os.getenv("OPENAI_API_KEY"):
    # Using GitHub Models
    default_model = "gpt-4o-mini"
else:
    # Using OpenAI API
    default_model = "gpt-3.5-turbo"

# A function to call an LLM model and return the response
def call_llm_model(model, messages, temperature=1.0, top_p=1.0):
    # Use Hugging Face if available
    if use_huggingface:
        try:
            from src.hf_helpers import hf_chat_completion
            # Convert temperature (0-2 range) to HF range (0-1)
            hf_temperature = min(temperature / 2.0, 1.0)
            return hf_chat_completion(messages, temperature=hf_temperature, max_new_tokens=500)
        except Exception as e:
            raise Exception(f"Hugging Face API call failed: {str(e)}")
    
    # Fallback to OpenAI/GitHub Models
    if not api_key:
        raise ValueError("Either HF_API_KEY, OPENAI_API_KEY, or GITHUB_TOKEN environment variable must be set")
    
    try:
        # Try using openai library (v0.28.0 style)
        import openai
        openai.api_key = api_key
        
        # If using GitHub token, use GitHub Models endpoint
        if os.getenv("GITHUB_TOKEN") and not os.getenv("OPENAI_API_KEY"):
            openai.api_base = "https://models.inference.ai.azure.com"
        
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            top_p=top_p
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"LLM API call failed: {str(e)}")

# A function to translate text using the LLM model
def translate(text, target_language):
    # Use Hugging Face translation if available
    if use_huggingface:
        try:
            from src.hf_helpers import hf_translate, hf_generate
            
            # Map common language names to codes
            lang_map = {
                "spanish": "es", "french": "fr", "german": "de", "italian": "it",
                "portuguese": "pt", "chinese": "zh", "japanese": "ja", "korean": "ko",
                "russian": "ru", "arabic": "ar", "hindi": "hi", "english": "en"
            }
            target_code = lang_map.get(target_language.lower(), target_language.lower()[:2])
            
            # Try translation model first
            translation_model = os.getenv("HF_TRANSLATION_MODEL", "")
            if translation_model:
                try:
                    return hf_translate(text, source_lang="auto", target_lang=target_code)
                except Exception as e:
                    print(f"Translation model failed, falling back to generation: {e}")
            
            # Fallback: use generation model for translation
            prompt = f"Translate the following text to {target_language}. Return ONLY the translated text, no explanations:\n\n{text}"
            return hf_generate(prompt, max_new_tokens=300, temperature=0.3)
            
        except Exception as e:
            raise Exception(f"Hugging Face translation failed: {str(e)}")
    
    # Fallback to OpenAI/GitHub Models
    prompt = f"Translate the following text to {target_language}. Return ONLY the translated text, no explanations or additional text:\n\n{text}"
    messages = [{"role": "user", "content": prompt}]
    return call_llm_model(default_model, messages)

system_prompt = '''
Extract the user's notes into the following structured fields:
1. Title: A concise title of the notes less than 5 words
2. Notes: The notes based on user input written in full sentences.
3. Tags (A list): At most 3 Keywords or tags that categorize the content of the notes.
4. Event Date: Extract any date mentioned in the input. If no date is mentioned, use an empty string "".
5. Event Time: Extract any time mentioned in the input. If no time is mentioned, use an empty string "".

Today's date and time {Current_DateTime}.

When extracting dates and times:
- Convert relative dates like "yesterday", "today", "tomorrow", "next week" to actual dates
- For "yesterday", calculate the actual date based on today's date (today - 1 day)
- For "today", use today's date
- For "tomorrow", calculate the actual date based on today's date (today + 1 day)
- Date format should be dd-mmm-yyyy (e.g., 18-Oct-2025)
- Time format should be HH:MM in 24-hour format (e.g., 15:00)
- If only date is mentioned without time, leave Event Time as ""
- If only time is mentioned without date, leave Event Date as ""

Output in JSON format without ```json. Output title and notes in the language: {lang}.

Examples:
Input: "Badminton tmr 5pm @polyu"
Output:
{{
"Title": "Badminton at PolyU", 
"Notes": "Remember to play badminton at 5pm tomorrow at PolyU.",
"Tags": ["badminton", "sports"],
"Event Date": "18-Oct-2025",
"Event Time": "17:00"
}}

Input: "Meeting with John tomorrow 3:00pm"
Output:
{{
"Title": "Meeting with John",
"Notes": "Meeting with John tomorrow at 3:00pm.",
"Tags": ["meeting", "John"],
"Event Date": "18-Oct-2025",
"Event Time": "15:00"
}}

Input: "Meeting with John yesterday 3:00pm"
Output:
{{
"Title": "Meeting with John",
"Notes": "Meeting with John yesterday at 3:00pm.",
"Tags": ["meeting", "John"],
"Event Date": "16-Oct-2025",
"Event Time": "15:00"
}}
'''

# A function to extract structured notes using the LLM model
def extract_structured_notes(text, lang="English"):
    from datetime import datetime
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prompt = system_prompt.format(lang=lang, Current_DateTime=current_datetime) + f"\nInput: \"{text}\""
    messages = [{"role": "user", "content": prompt}]
    response = call_llm_model(default_model, messages)
    return response

# Main function
def main():
    #test the extract_structured_notes function
    text = "I will meet you tomorrow at 3pm in the cafe."
    lang = "English"
    structured_notes = extract_structured_notes(text, lang)
    print(f"Input: {text}")
    print(f"Structured Notes: {structured_notes}")
    
    # Try to parse JSON if it's valid JSON
    try:
        import json
        parsed_notes = json.loads(structured_notes)
        print(f"Tags: {parsed_notes.get('Tags', [])}")
        print(f"Event Date: {parsed_notes.get('Event Date', '')}")
        print(f"Event Time: {parsed_notes.get('Event Time', '')}")
    except json.JSONDecodeError:
        print("Note: Response is not valid JSON format")

if __name__ == "__main__":
    main()
