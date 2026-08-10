#!/usr/bin/env python
"""
Basic test from Anthropic documentation
https://docs.anthropic.com/en/api/getting-started
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Method 1: Direct HTTP request (most basic)
print("=" * 60)
print("Method 1: Direct HTTP API call")
print("=" * 60)
import requests

api_key = os.getenv('ANTHROPIC_API_KEY')
url = 'https://api.anthropic.com/v1/messages'

headers = {
    'x-api-key': api_key,
    'anthropic-version': '2023-06-01',
    'content-type': 'application/json',
}

# Try the most basic model that should definitely exist
data = {
    'model': 'claude-3-5-sonnet-20241022',
    'max_tokens': 10,
    'messages': [
        {'role': 'user', 'content': 'Hello'}
    ]
}

print(f"Endpoint: {url}")
print(f"Model: {data['model']}")
print(f"Making request...\n")

response = requests.post(url, json=data, headers=headers)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text[:500]}\n")

if response.status_code == 200:
    print("✅ SUCCESS! API key works with this model!")
    import json
    result = response.json()
    print(f"Response: {result['content'][0]['text']}")
elif response.status_code == 404:
    print("❌ 404 Error - Model not found")
    print("\nLet me try other common models...")
    
    # Try other models
    other_models = [
        'claude-3-haiku-20240307',
        'claude-3-sonnet-20240229',
        'claude-3-opus-20240229',
    ]
    
    for model in other_models:
        data['model'] = model
        r = requests.post(url, json=data, headers=headers)
        if r.status_code == 200:
            print(f"✅ {model} WORKS!")
            import json
            result = r.json()
            print(f"   Response: {result['content'][0]['text']}")
            print(f"\n🎯 UPDATE .env to use model: {model}")
            break
        else:
            print(f"❌ {model} - Status {r.status_code}")
    else:
        print("\n⚠️  Check your API key at: https://console.anthropic.com/settings/keys")
        print("Verify:")
        print("  1. Billing is set up")
        print("  2. You're in the right workspace") 
        print("  3. The key hasn't been deleted/revoked")

print("\n" + "=" * 60)
print("Method 2: Using Anthropic SDK")
print("=" * 60)

import anthropic
client = anthropic.Anthropic(api_key=api_key)

try:
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=10,
        messages=[{"role": "user", "content": "Hello"}]
    )
    print("✅ SDK works!")
    print(f"Response: {message.content[0].text}")
except Exception as e:
    print(f"❌ SDK failed: {e}")
