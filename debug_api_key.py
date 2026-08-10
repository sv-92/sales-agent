#!/usr/bin/env python
"""Debug Anthropic API key loading and validation"""
import os
import sys
from dotenv import load_dotenv

print("=" * 60)
print("Anthropic API Key Debug Report")
print("=" * 60)

# Step 1: Check .env file exists
env_path = os.path.join(os.getcwd(), '.env')
print(f"\n1. .env file check:")
print(f"   Path: {env_path}")
print(f"   Exists: {os.path.exists(env_path)}")

if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        lines = f.readlines()
    print(f"   Lines in file: {len(lines)}")
    for i, line in enumerate(lines, 1):
        if 'ANTHROPIC_API_KEY' in line:
            # Show the line with key partially masked
            parts = line.split('=', 1)
            if len(parts) == 2:
                key_value = parts[1].strip()
                print(f"   Line {i}: ANTHROPIC_API_KEY={key_value[:20]}...{key_value[-10:] if len(key_value) > 30 else ''}")
                print(f"   Key length: {len(key_value)}")
                print(f"   Starts with 'sk-ant': {key_value.startswith('sk-ant')}")
                has_quotes = key_value.startswith('"') or key_value.startswith("'")
                print(f"   Has quotes: {has_quotes}")
                print(f"   Has whitespace: {key_value != key_value.strip()}")
                has_newline = '\\n' in repr(key_value) or '\\r' in repr(key_value)
                print(f"   Has newline: {has_newline}")

# Step 2: Load with dotenv
print(f"\n2. Loading .env with python-dotenv:")
load_dotenv(override=True)
api_key_from_env = os.getenv('ANTHROPIC_API_KEY')
print(f"   Key loaded: {api_key_from_env is not None}")
if api_key_from_env:
    print(f"   Value: {api_key_from_env[:20]}...{api_key_from_env[-10:]}")
    print(f"   Length: {len(api_key_from_env)}")
    print(f"   Format valid: {api_key_from_env.startswith('sk-ant')}")
else:
    print("   ERROR: No key loaded!")

# Step 3: Test with Anthropic SDK
print(f"\n3. Testing with Anthropic SDK:")
try:
    import anthropic
    
    if not api_key_from_env:
        print("   SKIP: No API key to test")
    else:
        client = anthropic.Anthropic(api_key=api_key_from_env)
        
        # Try the latest model first
        models_to_test = [
            'claude-3-5-sonnet-20241022',
            'claude-3-5-sonnet-20240620',
            'claude-3-opus-20240229',
        ]
        
        for model in models_to_test:
            try:
                message = client.messages.create(
                    model=model,
                    max_tokens=10,
                    messages=[{'role': 'user', 'content': 'hi'}]
                )
                print(f"   ✅ {model} WORKS!")
                print(f"   Response: {message.content[0].text}")
                sys.exit(0)  # Success!
            except anthropic.NotFoundError as e:
                print(f"   ❌ {model} - 404 not found")
            except anthropic.AuthenticationError as e:
                print(f"   ❌ {model} - Authentication error: {e}")
                print("   This means the API key is INVALID or EXPIRED")
                break
            except Exception as e:
                print(f"   ❌ {model} - {type(e).__name__}: {str(e)[:100]}")
        
        print("\n   ⚠️  All models failed. Possible causes:")
        print("      - API key doesn't have model access (check console)")
        print("      - Workspace restrictions")
        print("      - Key was revoked")
        
except ImportError:
    print("   ERROR: anthropic package not installed")
except Exception as e:
    print(f"   ERROR: {e}")

print("\n" + "=" * 60)
print("Recommendation:")
print("1. Copy your working API key (from this chat)")
print("2. Open .env file")
print("3. Replace the entire line with: ANTHROPIC_API_KEY=sk-ant-...")
print("4. NO quotes, NO spaces, NO newlines")
print("5. Save and re-run this script")
print("=" * 60)
