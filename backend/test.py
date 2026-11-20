
import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

# 1. Load root .env file
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# 2. Read configuration
API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("GROQ_MODEL")

if not API_KEY:
    raise ValueError("GROQ_API_KEY missing in .env")

if not MODEL:
    raise ValueError("GROQ_MODEL missing in .env")

# 3. Initialize Groq
client = Groq(api_key=API_KEY)

# 4. Conversation history
messages = [
    {
        "role": "system",
        "content": "You are a helpful AI assistant. "
                   "Provide clear, accurate and useful answers."
    }
]


def chat_with_groq(user_input):

    messages.append({
        "role": "user",
        "content": user_input
    })

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.7,
            max_completion_tokens=1000
        )

        reply = response.choices[0].message.content

        messages.append({
            "role": "assistant",
            "content": reply
        })

        return reply

    except Exception as e:
        messages.pop()
        return f"Groq API Error: {e}"


def main():

    print("\n" + "=" * 55)
    print("             GROQ AI CHATBOT")
    print("=" * 55)
    print(f"Model: {MODEL}")
    print("Type 'exit' to quit.")
    print("=" * 55)

    while True:

        user_input = input("\nYou: ").strip()

        if user_input.lower() in ["exit", "quit", "bye"]:
            print("\nChatbot: Goodbye!")
            break

        if not user_input:
            continue

        print("\nChatbot: ", end="", flush=True)

        response = chat_with_groq(user_input)

        print(response)


if __name__ == "__main__":
    main()
