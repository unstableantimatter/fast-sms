#!/usr/bin/env python3
"""
Simple script to test the TextBelt API connection.
"""

import requests
import sys
import json

def test_textbelt():
    """Test the TextBelt API connection."""
    print("Testing TextBelt API connection...")
    
    api_url = "https://textbelt.com/text"
    
    # Use a test phone number
    test_phone = '5555555555'
    
    # Prepare test payload with test flag
    payload = {
        'phone': test_phone,
        'message': 'Test connection',
        'key': 'textbelt',  # Free tier API key
        'test': '1'  # This tells TextBelt this is just a test
    }
    
    try:
        print(f"Sending request to {api_url}...")
        response = requests.post(api_url, data=payload)
        
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {json.dumps(dict(response.headers), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response JSON: {json.dumps(data, indent=2)}")
            
            if 'success' in data:
                print(f"Test result: {'Success' if data['success'] else 'Failed'}")
                if 'quotaRemaining' in data:
                    print(f"Remaining quota: {data['quotaRemaining']}")
                if 'error' in data:
                    print(f"Error message: {data['error']}")
            else:
                print("Invalid response format - 'success' field missing")
        else:
            print(f"Request failed with status code: {response.status_code}")
            print(f"Response text: {response.text}")
    
    except Exception as e:
        print(f"Error testing TextBelt API: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_textbelt()
    print("\nDone. Press Enter to exit...")
    input() 