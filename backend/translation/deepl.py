import deepl
from dotenv import load_dotenv
import os

load_dotenv()

auth_key = os.getenv("DEEPL_KEY")
translator = deepl.Translator(auth_key)

def translate_deepl(text):
    # Skip translation if empty text
    if not text or text.strip() == '':
        return ''
    
    try:
        translation = translator.translate_text(text, target_lang='EN-US')
        # Return as string to ensure serialization works
        return str(translation)
    except Exception as e:
        print(f"Translation error: {str(e)}")
        # Return original text if translation fails
        return text
