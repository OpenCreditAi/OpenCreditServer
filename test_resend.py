#!/usr/bin/env python3
"""
Test script for Resend email service
"""

import os
import sys
from datetime import datetime, UTC

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_resend_service():
    """Test the Resend email service"""
    
    # Set up environment variables for testing
    os.environ['EMAIL_PROVIDER'] = 'resend'
    os.environ['RESEND_API_KEY'] = '1234567890'
    os.environ['FROM_EMAIL'] = 'onboarding@resend.dev'
    
    # Create a mock Flask app context
    from flask import Flask
    app = Flask(__name__)
    app.config['EMAIL_PROVIDER'] = 'resend'
    app.config['RESEND_API_KEY'] = os.environ.get('RESEND_API_KEY')
    app.config['FROM_EMAIL'] = 'onboarding@resend.dev'
    
    with app.app_context():
        try:
            from app.services.unified_email_service import UnifiedEmailService
            email_service = UnifiedEmailService()
            
            # Test data
            loan_data = {
                'project_name': 'פרויקט דוגמה',
                'amount': 500000,
                'borrower_name': 'יונתן כהן',
                'borrower_email': 'yonatansinay@gmail.com',  # Send test email to yourself
                'updated_at': datetime.now(UTC).strftime("%d/%m/%Y %H:%M")
            }
            
            print("Testing Resend email service...")
            print(f"Email will be sent to: {loan_data['borrower_email']}")
            print("Make sure to update the RESEND_API_KEY in this script!")
            print()
            
            # Test PAID status email
            print("1. Testing PAID status email...")
            success = email_service.send_loan_status_notification(
                loan_data, "ACTIVE_LOAN", "PAID"
            )
            print(f"PAID email sent: {success}")
            
            # Test regular status change email
            print("\n2. Testing regular status change email...")
            success = email_service.send_loan_status_notification(
                loan_data, "MISSING_DOCUMENTS", "PROCESSING_DOCUMENTS"
            )
            print(f"Status change email sent: {success}")
            
        except ImportError as e:
            print(f"❌ Import error: {e}")
            print("Make sure to install resend: pip install resend")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Resend Email Service Test")
    print("========================")
    print("Before running this test:")
    print("1. Get your Resend API key from https://resend.com/api-keys")
    print("2. Update RESEND_API_KEY in this script")
    print("3. Make sure the email address is correct")
    print()
    
    test_resend_service()
