import os
import logging
from typing import Optional, Dict, Any
from flask import current_app

logger = logging.getLogger(__name__)

try:
    import resend
    RESEND_AVAILABLE = True
except ImportError:
    RESEND_AVAILABLE = False
    logger.warning("Resend not installed. Install with: pip install resend")


class ResendService:
    def __init__(self):
        if not RESEND_AVAILABLE:
            raise ImportError("Resend is not installed")
        
        self.api_key = current_app.config.get('RESEND_API_KEY')
        if not self.api_key:
            raise ValueError("RESEND_API_KEY not configured")
        
        self.from_email = current_app.config.get('FROM_EMAIL', 'onboarding@resend.dev')
        resend.api_key = self.api_key
    
    def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None) -> bool:
        """
        Send an email using Resend
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text content (optional)
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            params = {
                "from": self.from_email,
                "to": to_email,  # Resend expects string, not list
                "subject": subject,
                "html": html_content
            }
            
            if text_content:
                params["text"] = text_content
            
            response = resend.Emails.send(params)
            
            if response and isinstance(response, dict) and 'id' in response:
                logger.info(f"Email sent successfully to {to_email}. ID: {response['id']}")
                return True
            else:
                logger.error(f"Failed to send email to {to_email}. Response: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            print(f"Resend error details: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def send_loan_status_notification(self, loan_data: Dict[str, Any], old_status: str, new_status: str) -> bool:
        """
        Send loan status change notification email using Resend
        """
        # Import the email service to reuse templates
        from app.services.email_service import EmailService
        
        # Create a temporary EmailService instance to generate templates
        temp_email_service = EmailService()
        
        # Generate email content
        if new_status == "PAID":
            subject = "🎉 הלוואה שולמה בהצלחה! - OpenCredit"
            html_content = temp_email_service._generate_paid_email_template(loan_data, old_status, new_status)
        else:
            subject = f"עדכון סטטוס הלוואה - OpenCredit"
            html_content = temp_email_service._generate_status_change_email_template(loan_data, old_status, new_status)
        
        text_content = temp_email_service._generate_text_content(loan_data, old_status, new_status)
        
        return self.send_email(loan_data['borrower_email'], subject, html_content, text_content)
