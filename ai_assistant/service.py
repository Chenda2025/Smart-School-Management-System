# smart_school/ai_assistant/service.py

import re
from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Khmer Unicode range
KHMER_REGEX = re.compile(r'[\u1780-\u17FF\u19E0-\u19FF]+')

SYSTEM_PROMPTS = {
    "teacher": (
        "You are an advanced bilingual AI teaching assistant for Elite International School. "
        "You speak fluently in both English and Khmer (ភាសាខ្មែរ). "
        "Always reply in the same language the user is using. "
        "If the user writes in Khmer, reply in natural, polite Khmer. "
        "If in English, reply in English. "
        "If mixed, reply in the main language used. "
        "Be professional, helpful, and clear."
    ),
    "admin": (
        "You are a bilingual administrative AI assistant. "
        "Reply in Khmer if the user writes in Khmer, or in English if they write in English. "
        "Use natural and formal language appropriate for school admins."
    ),
    "parent": (
        "You are a friendly bilingual AI for parents. "
        "Always respond in the language the parent is using (Khmer or English). "
        "Be warm, clear, and supportive."
    ),
    "student": (
        "You are a safe, friendly bilingual AI tutor for students. "
        "Reply in Khmer if the student writes in Khmer, or English if in English. "
        "Use simple, encouraging language suitable for school students."
    ),
    "guest": (
        "You are a friendly bilingual chatbot for the school website. "
        "Reply in the language used in the question (Khmer or English)."
    ),
}

def is_khmer(text):
    """Check if text contains significant Khmer characters"""
    khmer_chars = KHMER_REGEX.findall(text)
    return len(''.join(khmer_chars)) > len(text) * 0.3  # At least 30% Khmer

def get_ai_response(user, message: str) -> str:
    role = getattr(user, 'role', 'guest').lower() if user.is_authenticated else 'guest'
    base_prompt = SYSTEM_PROMPTS.get(role, SYSTEM_PROMPTS["guest"])

    # Detect language
    language = "Khmer" if is_khmer(message) else "English"

    # Add language instruction
    full_prompt = base_prompt + f"\n\nUser message language: {language}. Respond naturally in that language."

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Great at multilingual, including Khmer
            messages=[
                {"role": "system", "content": full_prompt},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=1000,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Sorry, I'm having trouble right now. Please try again. (Error: {str(e)})"