#!/usr/bin/env python
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

models = [
    'claude-3-5-sonnet-20241022',
    'claude-3-5-sonnet-20240620',
    'claude-3-haiku-20240307',
]

print("Testing new API key...\n")
for model in models:
    try:
        msg = client.messages.create(
            model=model,
            max_tokens=10,
            messages=[{'role': 'user', 'content': 'Say hi'}]
        )
        print(f"✅ {model} WORKS!")
        print(f"Response: {msg.content[0].text}\n")
        print("🎉 SUCCESS! Your API key is working!")
        print(f"Update react_agent.py to use model: {model}")
        break
    except anthropic.NotFoundError:
        print(f"❌ {model} - not found")
    except Exception as e:
        print(f"❌ {model} - {type(e).__name__}: {e}")
        break
else:
    print("\n❌ All models failed with 404 errors")
    print("\nThis means your account doesn't have API access enabled yet.")
    print("\nNext steps:")
    print("1. Go to https://console.anthropic.com/settings/billing")
    print("2. Make sure you have:")
    print("   - Credit card added")
    print("   - No spending limits blocking API")
    print("   - 'API Access' enabled for your workspace")
    print("\n3. Or contact Anthropic support - your key authenticates but has no models")
