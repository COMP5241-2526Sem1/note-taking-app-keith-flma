"""
Hugging Face Inference API helpers
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
HF_API_URL = "https://api-inference.huggingface.co/models/"

def hf_call_model(model, payload, retry_count=3):
    """
    Generic function to call Hugging Face Inference API
    
    Args:
        model: Model name in format "owner/model"
        payload: Dictionary with model-specific parameters
        retry_count: Number of retries if model is loading
    
    Returns:
        API response as dict or string
    """
    if not HF_API_KEY:
        raise ValueError("HF_API_KEY environment variable must be set")
    
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    api_url = f"{HF_API_URL}{model}"
    
    for attempt in range(retry_count):
        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            
            # Handle model loading state
            if response.status_code == 503:
                result = response.json()
                if "estimated_time" in result:
                    # Model is loading, wait and retry
                    import time
                    wait_time = min(result.get("estimated_time", 20), 20)  # Cap at 20 seconds
                    print(f"Model loading, waiting {wait_time}s... (attempt {attempt + 1}/{retry_count})")
                    time.sleep(wait_time)
                    continue
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            if attempt < retry_count - 1:
                continue
            raise Exception(f"Request timed out after {retry_count} attempts")
        except requests.exceptions.RequestException as e:
            if attempt < retry_count - 1 and response.status_code in [503, 429]:
                import time
                time.sleep(5)
                continue
            raise Exception(f"Hugging Face API error: {str(e)} - Status: {response.status_code if 'response' in locals() else 'N/A'}")
    
    raise Exception(f"Failed to get response from model after {retry_count} attempts")

def hf_generate(prompt, max_new_tokens=200, temperature=0.7):
    """
    Generate text using a Hugging Face language model
    
    Args:
        prompt: Input text prompt
        max_new_tokens: Maximum number of tokens to generate
        temperature: Sampling temperature (0.0 to 1.0)
    
    Returns:
        Generated text as string
    """
    model = os.getenv("HF_MODEL", "google/flan-t5-large")
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            "return_full_text": False
        }
    }
    
    response = hf_call_model(model, payload)
    
    # Handle different response formats
    if isinstance(response, list) and len(response) > 0:
        if isinstance(response[0], dict) and "generated_text" in response[0]:
            return response[0]["generated_text"].strip()
        elif isinstance(response[0], str):
            return response[0].strip()
    elif isinstance(response, dict) and "generated_text" in response:
        return response["generated_text"].strip()
    elif isinstance(response, str):
        return response.strip()
    
    raise Exception(f"Unexpected response format: {response}")

def hf_translate(text, source_lang="en", target_lang="es"):
    """
    Translate text using Hugging Face translation model
    
    Args:
        text: Text to translate
        source_lang: Source language code (default: "en")
        target_lang: Target language code (default: "es")
    
    Returns:
        Translated text as string
    """
    model = os.getenv("HF_TRANSLATION_MODEL", "Helsinki-NLP/opus-mt-mul-en")
    
    # For opus-mt models, the input format depends on the model variant
    # opus-mt-mul-en: translates FROM multiple languages TO English
    # opus-mt-en-mul: translates FROM English TO multiple languages
    
    # Determine if we need English as target or source
    if "mul-en" in model.lower():
        # This model translates TO English
        payload = {"inputs": text}
    else:
        # For other models, might need language prefix
        # Some models require format like ">>es<< text" for target language
        if target_lang.lower() != "en":
            payload = {"inputs": f">>{target_lang}<< {text}"}
        else:
            payload = {"inputs": text}
    
    response = hf_call_model(model, payload)
    
    # Handle different response formats
    if isinstance(response, list) and len(response) > 0:
        if isinstance(response[0], dict) and "translation_text" in response[0]:
            return response[0]["translation_text"].strip()
        elif isinstance(response[0], dict) and "generated_text" in response[0]:
            return response[0]["generated_text"].strip()
        elif isinstance(response[0], str):
            return response[0].strip()
    elif isinstance(response, dict):
        if "translation_text" in response:
            return response["translation_text"].strip()
        elif "generated_text" in response:
            return response["generated_text"].strip()
    
    raise Exception(f"Unexpected translation response format: {response}")

def hf_chat_completion(messages, temperature=0.7, max_new_tokens=500):
    """
    Simulate chat completion using text generation model
    Converts chat messages into a prompt for text generation
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        temperature: Sampling temperature
        max_new_tokens: Maximum tokens to generate
    
    Returns:
        Generated response text
    """
    # Convert chat messages to a single prompt
    prompt_parts = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "system":
            prompt_parts.append(f"System: {content}")
        elif role == "user":
            prompt_parts.append(f"User: {content}")
        elif role == "assistant":
            prompt_parts.append(f"Assistant: {content}")
    
    prompt = "\n".join(prompt_parts) + "\nAssistant:"
    
    return hf_generate(prompt, max_new_tokens=max_new_tokens, temperature=temperature)
