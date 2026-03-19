"""
Run this script to debug your Groq API key.
Place it in your AI DEV POD folder and run: python debug_groq.py
"""
import os
import sys

print("=" * 50)
print("  Groq API Key Debug")
print("=" * 50)

# Step 1: Check dotenv loading
print("\n[1] Loading .env file...")
try:
    from dotenv import load_dotenv
    result = load_dotenv(override=True)
    print(f"  .env loaded: {result}")
except ImportError:
    print("  python-dotenv not installed")

# Step 2: Check what the key looks like
key = os.getenv("GROQ_API_KEY", "")
print(f"\n[2] GROQ_API_KEY from environment:")
if not key:
    print("  ❌ EMPTY — key not found in environment")
    print("     Make sure .env file is in the SAME folder as this script")
else:
    print(f"  Length  : {len(key)} characters")
    print(f"  Starts  : {key[:10]}...")
    print(f"  Ends    : ...{key[-6:]}")
    print(f"  Has spaces: {' ' in key}")
    print(f"  Has quotes: {key.startswith(chr(39)) or key.startswith(chr(34))}")
    print(f"  Starts with gsk_: {key.startswith('gsk_')}")

# Step 3: Try direct API call
print("\n[3] Testing API call...")
try:
    from groq import Groq
    client = Groq(api_key=key)
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": "Say hello in one word."}],
        max_tokens=10,
    )
    print(f"  ✅ SUCCESS! Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"  ❌ FAILED: {e}")
    print(f"\n  Raw key repr: {repr(key[:20])}")

print("\n" + "=" * 50)