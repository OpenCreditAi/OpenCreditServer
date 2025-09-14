#!/usr/bin/env python3
"""
Test script to verify the authorization fix works
"""

import requests
import json

def test_loan_status_update(loan_id, status, jwt_token):
    """Test loan status update with proper error handling"""
    url = f"http://127.0.0.1:5000/loans/{loan_id}/status"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    data = {"status": status}
    
    print(f"🧪 Testing loan {loan_id} status update to '{status}'")
    print(f"   URL: {url}")
    
    try:
        response = requests.put(url, headers=headers, json=data)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ SUCCESS!")
            print(f"   📧 Borrower email sent: {result.get('borrower_email_sent', False)}")
            print(f"   📧 Financier email sent: {result.get('financier_email_sent', False)}")
            return True
        else:
            try:
                result = response.json()
                print(f"   ❌ FAILED: {result.get('error', 'Unknown error')}")
            except:
                print(f"   ❌ FAILED: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False

def main():
    print("🔧 Testing Authorization Fix")
    print("=" * 40)
    
    # You'll need to replace these with actual values
    loan_id = 1  # Replace with actual loan ID
    jwt_token = "your-jwt-token-here"  # Replace with actual JWT token
    
    print(f"Testing with loan ID: {loan_id}")
    print("Note: Replace loan_id and jwt_token with actual values before running!")
    print("\nThe fix should resolve the 'InstrumentedList' error.")
    print("Now the authorization check uses Python's any() function instead of filter_by().")

if __name__ == "__main__":
    main()
