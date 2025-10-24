#!/usr/bin/env python3
"""
Simple test for core functionality
"""
import subprocess
import sys

def main():
    print("Testing core components...")

    # Test FFmpeg
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
        print(f"FFmpeg: {'OK' if result.returncode == 0 else 'FAILED'}: {result.stdout.split('\n')[0] if result.stdout else 'No output'}")
    except Exception as e:
        print(f"FFmpeg: FAILED - {str(e)}")
        return1

    # Test Python imports
    try:
        __import__('whisper')
        print("Whisper import: OK")
    except Exception as e:
        print(f"Whisper import: FAILED - {str(e)}")
        return 1

    try:
        from openai import OpenAI
        print("OpenAI import: OK")
    except Exception as e:
        print(f"OpenAI import: FAILED - {str(e)}")
        return 1

    print("\nAll core components are working! Flask app can be started with: python app.py")
    return 0

if __name__ == "__main__":
    sys.exit(main())