# import libraries
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # Loads environment variables from .env
token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.github.ai/inference"
model = "openai/gpt-4.1-mini"

# A function to call an LLM model and return the response
def call_llm_model(model, messages, temperature=1.0, top_p=1.0):    
    client = OpenAI(base_url=endpoint, api_key=token)
    response = client.chat.completions.create(
        messages=messages,
        temperature=temperature, top_p=top_p, model=model)
    return response.choices[0].message.content

# A function to translate text using the LLM model
def translate(text, target_language):
    prompt = f"Translate the following text to {target_language}. Return ONLY the translated text, no explanations or additional text:\n\n{text}"
    messages = [{"role": "user", "content": prompt}]
    return call_llm_model(model, messages)

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
    response = call_llm_model(model, messages)
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
