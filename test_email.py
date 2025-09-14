#!/usr/bin/env python3
"""
Test script for email functionality
Run this script to test the email service without running the full Flask app
"""

import os
import sys
from datetime import datetime, UTC

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.email_service import EmailService

def test_email_service():
    """Test the email service with sample data"""
    
    # Set up environment variables for testing
    os.environ['EMAIL_USER'] = 'yonatansinay@gmail.com'
    os.environ['EMAIL_PASSWORD'] = 'your-16-character-app-password-here'  # Replace with your actual app password
    os.environ['FROM_EMAIL'] = 'yonatansinay@gmail.com'
    
    # Create a mock Flask app context
    from flask import Flask
    app = Flask(__name__)
    app.config['EMAIL_USER'] = os.environ.get('EMAIL_USER')
    app.config['EMAIL_PASSWORD'] = os.environ.get('EMAIL_PASSWORD')
    app.config['FROM_EMAIL'] = os.environ.get('FROM_EMAIL')
    app.config['SMTP_SERVER'] = 'smtp.gmail.com'
    app.config['SMTP_PORT'] = 587
    
    with app.app_context():
        email_service = EmailService()
        
        # Test data
        loan_data = {
            'project_name': 'פרויקט דוגמה',
            'amount': 500000,
            'borrower_name': 'יונתן כהן',
            'borrower_email': 'yonatansinay@gmail.com',  # Send test email to yourself
            'updated_at': datetime.now(UTC).strftime("%d/%m/%Y %H:%M")
        }
        
        print("Testing email service...")
        print(f"Email will be sent to: {loan_data['borrower_email']}")
        print("Make sure to update the email addresses in this script before running!")
        
        # Test PAID status email
        print("\n1. Testing PAID status email...")
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

if __name__ == "__main__":
    print("Email Service Test")
    print("=================")
    print("Before running this test:")
    print("1. Update the email addresses in this script")
    print("2. Set up Gmail App Password if using Gmail")
    print("3. Make sure EMAIL_USER and EMAIL_PASSWORD are set correctly")
    print()
    
    test_email_service()
