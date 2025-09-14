#!/usr/bin/env python3
"""
Simple email test with correct API key
"""

import requests
import json

def test_loan_status_update():
    """Test loan status update to trigger email sending"""
    url = "http://127.0.0.1:5000/loans/21/status"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTczNjg5NzQwMCwianRpIjoiYjQ5YzQ5YjAtYjQ5Yy00YjQ5LWI0OTktYjQ5YzQ5YjQ5YzQ5IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6Inlvbml0YW5zaW5heUBnbWFpbC5jb20iLCJuYmYiOjE3MzY4OTc0MDAsImV4cCI6MTczNjkwMTAwMH0.example",  # Replace with real token
        "Content-Type": "application/json"
    }
    data = {"status": "ACTIVE_LOAN"}
    
    print("🧪 Testing loan status update with email sending...")
    print(f"URL: {url}")
    print(f"Data: {json.dumps(data)}")
    
    try:
        response = requests.put(url, headers=headers, json=data)
        result = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 200:
            if result.get('borrower_email_sent') and result.get('financier_email_sent'):
                print("✅ SUCCESS - Both emails sent!")
                return True
            else:
                print("⚠️  Status updated but emails not sent")
                print(f"   Borrower email: {result.get('borrower_email_sent')}")
                print(f"   Financier email: {result.get('financier_email_sent')}")
                return False
        else:
            print(f"❌ FAILED - {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR - {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Testing Email Sending Fix")
    print("=" * 40)
    print("Note: Make sure to replace the JWT token with a real one!")
    test_loan_status_update()