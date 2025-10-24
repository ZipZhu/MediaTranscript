#!/usr/bin/env python3
"""
Test script to verify the media transcription setup is working properly
"""

import os
import sys
import time
from openai import OpenAI
import whisper
from pydub import AudioSegment

def test_whisper():
    print("Testing Whisper installation...")
    try:
        model = whisper.load_model("base")
        print("✓ Whisper model loaded successfully")
        return True
    except Exception as e:
        print(f"✗ Whisper test failed: {e}")
        return False

def test_openai_client():
    print("Testing OpenAI client...")
    try:
        # Just test if we can create a client (don't make actual API call without key)
        api_key = os.getenv('OPENAI_API_KEY', 'test-key')
        base_url = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
        client = OpenAI(api_key=api_key, base_url=base_url)
        print("✓ OpenAI client created successfully")
        return True
    except Exception as e:
        print(f"✗ OpenAI client test failed: {e}")
        return False

def test_ffmpeg():
    print("Testing FFmpeg installation...")
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ FFmpeg is installed and working")
            return True
        else:
            print(f"✗ FFmpeg test failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ FFmpeg not found: {e}")
        return False

def test_pydub():
    print("Testing PyDub...")
    try:
        # Test basic functionality
        audio = AudioSegment.silent(duration=1000)  # Create 1 second of silence
        print("✓ PyDub is working")
        return True
    except Exception as e:
        print(f"✗ PyDub test failed: {e}")
        return False

def main():
    print("\n=== Media Transcription Setup Test ===\n")

    tests = [
        ("FFmpeg", test_ffmpeg),
        ("Whisper", test_whisper),
        ("OpenAI Client", test_openai_client),
        ("PyDub", test_pydub)
    ]

    results = []
    for name, test_func in tests:
        print(f"\n--- {name} ---")
        result = test_func()
        results.append((name, result))

    print("\n=== Test Results ===")
    all_passed = True
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{name}: {status}")
        if not result:
            all_passed = False

    print(f"\nOverall: {'SUCCESS' if all_passed else 'FAILED'}")
    return0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())