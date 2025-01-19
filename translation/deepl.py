import deepl
from dotenv import load_dotenv
import os

load_dotenv()

auth_key = os.getenv("DEEPL_KEY")
translator = deepl.Translator(auth_key)

def translate_deepl(text):
    translation = translator.translate_text(text, target_lang='EN-US')
    return translation
