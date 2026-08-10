"""
Test with the vs-code-personal-mac key that works for chat
"""
import anthropic

# PASTE YOUR vs-code-personal-mac KEY HERE (the one that works for this chat)
WORKING_KEY = "sk-ant-api03-0Pd..."  # Replace with your full vs-code-personal-mac key

client = anthropic.Anthropic(api_key=WORKING_KEY)

# Try different model names
models = [
    'claude-sonnet-4-20250514',
    'claude-3-5-sonnet-20241022', 
    'claude-3-5-sonnet-20240620',
    'claude-3-opus-20240229',
]

print("Testing with vs-code-personal-mac key...")
for model in models:
    try:
        message = client.messages.create(
            model=model,
            max_tokens=10,
            messages=[{'role': 'user', 'content': 'test'}]
        )
        print(f"✅ {model} WORKS!")
        print(f"   Response: {message.content[0].text}")
        print(f"\n💡 Use this model in your code: {model}")
        break
    except Exception as e:
        print(f"❌ {model} - {type(e).__name__}")
