import os
import logging
from typing import Optional, Dict, Any
from flask import current_app

logger = logging.getLogger(__name__)

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False
    logger.warning("SendGrid not installed. Install with: pip install sendgrid")


class SendGridService:
    def __init__(self):
        if not SENDGRID_AVAILABLE:
            raise ImportError("SendGrid is not installed")
        
        self.api_key = current_app.config.get('SENDGRID_API_KEY')
        if not self.api_key:
            raise ValueError("SENDGRID_API_KEY not configured")
        
        self.from_email = current_app.config.get('FROM_EMAIL', 'noreply@opencredit.co.il')
        self.client = SendGridAPIClient(api_key=self.api_key)
    
    def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None) -> bool:
        """
        Send an email using SendGrid
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text content (optional)
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            
            if text_content:
                message.add_content(text_content, content_type="text/plain")
            
            response = self.client.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"Failed to send email to {to_email}. Status: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_loan_status_notification(self, loan_data: Dict[str, Any], old_status: str, new_status: str) -> bool:
        """
        Send loan status change notification email using SendGrid
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
