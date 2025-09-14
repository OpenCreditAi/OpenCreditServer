#!/usr/bin/env python3
"""
Test script to verify status update fix works with both string and numeric values
"""

import requests
import json

def test_status_update(loan_id, status, jwt_token, description):
    """Test status update with given status value"""
    url = f"http://127.0.0.1:5000/loans/{loan_id}/status"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    data = {"status": status}
    
    print(f"\n🧪 Testing: {description}")
    print(f"   Status: {status} (type: {type(status).__name__})")
    print(f"   URL: {url}")
    print(f"   Data: {json.dumps(data)}")
    
    try:
        response = requests.put(url, headers=headers, json=data)
        result = response.json()
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 200:
            print("   ✅ SUCCESS - Status updated and emails sent!")
            return True
        else:
            print(f"   ❌ FAILED - {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR - {str(e)}")
        return False

def main():
    print("🔧 Testing Loan Status Update Fix")
    print("=" * 50)
    
    # You'll need to replace these with actual values
    loan_id = 1  # Replace with actual loan ID
    jwt_token = "your-jwt-token-here"  # Replace with actual JWT token
    
    print(f"Testing with loan ID: {loan_id}")
    print("Note: Replace loan_id and jwt_token with actual values before running!")
    
    # Test cases
    test_cases = [
        ("ACTIVE_LOAN", "String status name"),
        (4, "Numeric status value"),
        ("PAID", "String PAID status"),
        (5, "Numeric PAID status"),
        ("INVALID_STATUS", "Invalid string status"),
        (999, "Invalid numeric status"),
    ]
    
    success_count = 0
    total_tests = len(test_cases)
    
    for status, description in test_cases:
        success = test_status_update(loan_id, status, jwt_token, description)
        if success:
            success_count += 1
    
    print(f"\n📊 Test Results: {success_count}/{total_tests} tests passed")
    
    if success_count == 4:  # Expected: 4 valid tests should pass
        print("✅ All valid tests passed! The fix is working correctly.")
    else:
        print("❌ Some tests failed. Check the responses above.")

if __name__ == "__main__":
    main()
