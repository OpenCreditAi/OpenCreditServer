#!/usr/bin/env python3
"""
Test script for dual email notifications (borrower + financier)
"""

import os
import sys
from datetime import datetime, UTC

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_dual_email_notifications():
    """Test sending emails to both borrower and financier"""
    
    # Set up environment variables for testing
    os.environ['EMAIL_PROVIDER'] = 'resend'
    os.environ['RESEND_API_KEY'] = 're_x8eHadn8_Cn4aK2FaSXp9rJEKCtbSSNQC'
    os.environ['FROM_EMAIL'] = 'onboarding@resend.dev'
    
    # Create a mock Flask app context
    from flask import Flask
    app = Flask(__name__)
    app.config['EMAIL_PROVIDER'] = 'resend'
    app.config['RESEND_API_KEY'] = 're_x8eHadn8_Cn4aK2FaSXp9rJEKCtbSSNQC'
    app.config['FROM_EMAIL'] = 'onboarding@resend.dev'
    
    with app.app_context():
        try:
            from app.services.unified_email_service import UnifiedEmailService
            email_service = UnifiedEmailService()
            
            # Test data with both borrower and financier info
            loan_data = {
                'project_name': 'פרויקט דוגמה',
                'amount': 500000,
                'borrower_name': 'יונתן כהן',
                'borrower_email': 'yonatansinay@gmail.com',
                'financier_name': 'בנק הפועלים',
                'financier_email': 'yonatansinay@gmail.com',  # Send to same email for testing
                'updated_at': datetime.now(UTC).strftime("%d/%m/%Y %H:%M")
            }
            
            print("Testing dual email notifications...")
            print(f"Borrower email: {loan_data['borrower_email']}")
            print(f"Financier email: {loan_data['financier_email']}")
            print()
            
            # Test PAID status email to borrower
            print("1. Testing PAID status email to BORROWER...")
            borrower_success = email_service.send_loan_status_notification(
                loan_data, "ACTIVE_LOAN", "PAID", "borrower"
            )
            print(f"Borrower PAID email sent: {borrower_success}")
            
            # Test PAID status email to financier
            print("\n2. Testing PAID status email to FINANCIER...")
            financier_success = email_service.send_loan_status_notification(
                loan_data, "ACTIVE_LOAN", "PAID", "financier"
            )
            print(f"Financier PAID email sent: {financier_success}")
            
            # Test regular status change to borrower
            print("\n3. Testing status change email to BORROWER...")
            borrower_status_success = email_service.send_loan_status_notification(
                loan_data, "MISSING_DOCUMENTS", "PROCESSING_DOCUMENTS", "borrower"
            )
            print(f"Borrower status change email sent: {borrower_status_success}")
            
            # Test regular status change to financier
            print("\n4. Testing status change email to FINANCIER...")
            financier_status_success = email_service.send_loan_status_notification(
                loan_data, "MISSING_DOCUMENTS", "PROCESSING_DOCUMENTS", "financier"
            )
            print(f"Financier status change email sent: {financier_status_success}")
            
            print(f"\n📊 Summary:")
            print(f"Borrower emails sent: {borrower_success} + {borrower_status_success}")
            print(f"Financier emails sent: {financier_success} + {financier_status_success}")
            print(f"Total emails sent: {sum([borrower_success, financier_success, borrower_status_success, financier_status_success])}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("Dual Email Notification Test")
    print("============================")
    print("This will test sending emails to both borrower and financier")
    print("You should receive 4 emails total (2 PAID + 2 status change)")
    print()
    
    test_dual_email_notifications()
