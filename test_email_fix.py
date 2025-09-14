#!/usr/bin/env python3
"""
Test email sending with correct API key
"""

import os
import sys
sys.path.append('/app')

from app import create_app
from app.services.unified_email_service import UnifiedEmailService

def test_email_sending():
    app = create_app()
    
    with app.app_context():
        print('🧪 Testing email sending with correct API key...')
        print(f'EMAIL_PROVIDER: {app.config.get("EMAIL_PROVIDER")}')
        print(f'RESEND_API_KEY: {app.config.get("RESEND_API_KEY")[:10]}...')
        
        email_service = UnifiedEmailService()
        
        # Test data
        loan_data = {
            'project_name': 'Test Project',
            'amount': 100000,
            'borrower_name': 'Test Borrower',
            'borrower_email': 'yonatansinay@gmail.com',
            'financier_name': 'Test Financier',
            'financier_email': 'yonatansinay@gmail.com',
            'updated_at': '01/01/2024 12:00'
        }
        
        try:
            result = email_service.send_loan_status_notification(
                loan_data, 'PROCESSING_DOCUMENTS', 'ACTIVE_LOAN', 'borrower'
            )
            print(f'✅ Email sent successfully: {result}')
            return True
        except Exception as e:
            print(f'❌ Email failed: {str(e)}')
            return False

if __name__ == "__main__":
    test_email_sending()
