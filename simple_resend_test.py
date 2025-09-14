#!/usr/bin/env python3
"""
Simple Resend test using the exact code that works
"""

import resend

def test_resend_direct():
    """Test Resend directly with the working code"""
    
    resend.api_key = getenv('RESEND_API_KEY')
    
    try:
        r = resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": "yonatansinay@gmail.com",
            "subject": "Hello World from OpenCredit",
            "html": "<p>Congrats on sending your <strong>first email</strong> from OpenCredit!</p>"
        })
        
        print("✅ Email sent successfully!")
        print(f"Response: {r}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("Direct Resend Test")
    print("=================")
    test_resend_direct()
