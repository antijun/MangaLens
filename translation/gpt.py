from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def translate_gpt(text):
    
    prompt = f"Translate the following Japanese text into natural, conversational English:\n\n{text}\n\nEnglish Translation:"
    completion = client.chat.completions.create(
        model="gpt-4o", 
        messages=[
            {"role": "system", "content": "You are helping with the translation of Japanese text from manga panels to English. The text is often informal and conversational. Please translate the following text into natural, conversational English."}, 
            {"role": "user", "content": prompt}  
        ]
    )
    
    translation = completion.choices[0].message.content
    return translation