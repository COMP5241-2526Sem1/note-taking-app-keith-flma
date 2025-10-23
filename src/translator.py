import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def microsoft_translate(text, target_language):
    """
    Translate text using Microsoft Translator API
    """
    # Get API key from environment
    api_key = os.getenv("MICROSOFT_TRANSLATOR_KEY")
    if not api_key:
        raise ValueError("MICROSOFT_TRANSLATOR_KEY environment variable not set")
    
    # Microsoft Translator endpoint
    endpoint = "https://api.cognitive.microsofttranslator.com/translate"
    
    # Language code mapping
    language_codes = {
        'Chinese': 'zh',
        'Spanish': 'es', 
        'French': 'fr',
        'German': 'de',
        'Japanese': 'ja',
        'Korean': 'ko',
        'Russian': 'ru',
        'Portuguese': 'pt',
        'Italian': 'it',
        'Arabic': 'ar',
        'English': 'en'
    }
    
    # Get language code
    to_lang = language_codes.get(target_language, target_language.lower())
    
    # Request parameters
    params = {
        'api-version': '3.0',
        'to': to_lang
    }
    
    # Request headers
    headers = {
        'Ocp-Apim-Subscription-Key': api_key,
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Region': 'global'  # Use 'global' for multi-service key
    }
    
    # Request body
    body = [{'text': text}]
    
    try:
        # Make the request
        response = requests.post(endpoint, params=params, headers=headers, json=body)
        response.raise_for_status()
        
        # Parse response
        result = response.json()
        if result and len(result) > 0 and 'translations' in result[0]:
            translated_text = result[0]['translations'][0]['text']
            return translated_text
        else:
            raise Exception("Unexpected response format from Microsoft Translator")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"Microsoft Translator API error: {str(e)}")
    except Exception as e:
        raise Exception(f"Translation failed: {str(e)}")

def free_translate(text, target_language):
    """
    Free translation service (basic word replacement - very limited)
    This is just a fallback when no API is available
    """
    # Basic word translations (very limited)
    basic_translations = {
        'hello': {'Chinese': '你好', 'Spanish': 'hola', 'French': 'bonjour'},
        'goodbye': {'Chinese': '再见', 'Spanish': 'adiós', 'French': 'au revoir'},
        'thank you': {'Chinese': '谢谢', 'Spanish': 'gracias', 'French': 'merci'},
        'yes': {'Chinese': '是', 'Spanish': 'sí', 'French': 'oui'},
        'no': {'Chinese': '不', 'Spanish': 'no', 'French': 'non'}
    }
    
    text_lower = text.lower().strip()
    if text_lower in basic_translations and target_language in basic_translations[text_lower]:
        return basic_translations[text_lower][target_language]
    
    return f"[Translation to {target_language}]: {text}"

def translate(text, target_language):
    """
    Main translation function - tries Microsoft Translator first, falls back to basic
    """
    try:
        # Try Microsoft Translator first
        return microsoft_translate(text, target_language)
    except Exception as e:
        print(f"Microsoft Translator failed: {e}")
        # Fallback to basic translation
        return free_translate(text, target_language)