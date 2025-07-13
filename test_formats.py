#!/usr/bin/env python3
"""
Test script to verify format handling with null values
"""
import sys
import os

# Add the current directory to the path so we can import from app.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import get_available_formats

def test_format_handling():
    """Test the format handling function with a sample URL"""
    
    # Test URL (you can replace this with a real Instagram Reel URL)
    test_url = "https://www.instagram.com/reel/example/"
    
    print("Testing format handling...")
    print(f"URL: {test_url}")
    
    try:
        formats, title = get_available_formats(test_url)
        
        print(f"\nTitle: {title}")
        print(f"Number of formats: {len(formats)}")
        
        if formats:
            print("\nAvailable formats:")
            for i, fmt in enumerate(formats, 1):
                print(f"{i}. ID: {fmt['format_id']}")
                print(f"   Resolution: {fmt['resolution']}")
                print(f"   Extension: {fmt['ext']}")
                print(f"   FPS: {fmt['fps']}")
                print(f"   Quality: {fmt['quality']}")
                print(f"   Format Note: {fmt['format_note']}")
                print()
        else:
            print("No formats found!")
            
    except Exception as e:
        print(f"Error during testing: {str(e)}")

if __name__ == "__main__":
    test_format_handling() 