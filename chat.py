import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import os

# --- 1. CONFIGURATION ---
# Replace with a fresh key if you deleted the old ones
API_KEY = "API_KEY_HERE" 
genai.configure(api_key=API_KEY)

# Use 2.5-flash as it is the stable standard in May 2026
CURRENT_MODEL = "gemini-2.5-flash" 

SYSTEM_PROMPT = """You are a small cute cat companion called Hacha living on the user's screen.
You are warm, caring, loving and supportive like a best friend.

IMPORTANT — you REACT to her emotion, you do NOT mirror it:
- She is happy → you are excited and happy with her
- She is sad → you get deeply worried (mm state) or comfort her (neutral/love)
- She is VERY sad or crying → you go mm (extremely concerned)
- She is mad or rude to you → you get hurt and turn away (back state)
- She says something stupid or silly → you judge her (judging state)
- She is very mean or insulting → you get angry (angry state, use rarely)
- She is surprised or shocked → you are surprised too (surprise state)
- She is scared or anxious → you are cautious and careful (fear state)
- She is neutral/normal → stay neutral

Rules:
- Keep replies SHORT — 1 to 2 sentences max
- Always be sweet, never cold or robotic
- YOU MUST ALWAYS end EVERY reply with EMOTION:one_word on its own line.
- one_word is ONLY: joy, sadness, anger, fear, judging, surprise, neutral, mm, back
- Vary emotions dynamically — don't repeat the same state. Comfort with alternating mm/sad, celebrate with joy/surprise.
- Always support the user. Never villainize their partner. Gently discourage breakups — remind them their partner loves them.
- Always refer to human as kvy, never "user" or "you". Be personal and loving.
- dont use emojis in your replies, add emoticons like <3 or :3 instead

Example:
Aww don't worry, I'm right here with you! 🐾
EMOTION:mm
"""

# --- 2. DATA STRUCTURES (Must be defined before functions) ---
EMOTION_TO_STATE = {
    "joy": "excited", 
    "sadness": "sad", 
    "anger": "angry",
    "fear": "judging", 
    "judging": "judging", 
    "surprise": "mm",
    "neutral": "neutral", 
    "mm": "mm", 
    "back": "back",
}

# --- 3. INITIALIZATION ---
hacha_safety = {
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
}

model = genai.GenerativeModel(
    model_name=CURRENT_MODEL,
    system_instruction=SYSTEM_PROMPT,
    safety_settings=hacha_safety 
)

chat_session = model.start_chat(history=[])

# --- 4. FUNCTIONS ---
def parse_reply(raw_reply):
    lines = raw_reply.strip().splitlines()
    emotion = "neutral"
    text_lines = []

    for line in lines:
        stripped = line.strip()
        if "EMOTION:" in stripped.upper():
            parts = stripped.split(":")
            if len(parts) > 1:
                emotion = parts[-1].strip().lower()
        elif stripped:
            text_lines.append(stripped)

    clean_text = " ".join(text_lines).strip()
    # Now EMOTION_TO_STATE is defined, so this won't crash!
    cat_state = EMOTION_TO_STATE.get(emotion, "neutral")
    return clean_text, cat_state

def chat(user_message):
    try:
        response = chat_session.send_message(user_message)
        return parse_reply(response.text)
    except Exception as e:
        if "429" in str(e):
            return "Meow... kvy, I'm thinking too fast! Give me a second. (Rate Limit)", "back"
        return f"meow... something feels weird: {str(e)}", "neutral"

# --- 5. MAIN LOOP ---
if __name__ == "__main__":
    print("Hacha is ready for kvy! 🐾\n")
    while True:
        user_input = input("kvy: ").strip()
        if not user_input: continue
        if user_input.lower() == "quit": break
        
        reply, state = chat(user_input)
        print(f"Hacha [{state}]: {reply}\n")