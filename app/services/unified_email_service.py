import logging
from typing import Dict, Any
from flask import current_app

logger = logging.getLogger(__name__)


class UnifiedEmailService:
    def __init__(self):
        self.provider = current_app.config.get('EMAIL_PROVIDER', 'resend')
        self._service = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize the appropriate email service based on configuration"""
        if self.provider == 'resend':
            try:
                from app.services.resend_service import ResendService
                self._service = ResendService()
                logger.info("Using Resend email service")
            except ImportError:
                logger.error("Resend service not available. Install with: pip install resend")
                raise
            except Exception as e:
                logger.error(f"Failed to initialize Resend service: {e}")
                raise
        elif self.provider == 'gmail':
            try:
                from app.services.email_service import EmailService
                self._service = EmailService()
                logger.info("Using Gmail SMTP email service")
            except Exception as e:
                logger.error(f"Failed to initialize Gmail service: {e}")
                raise
        else:
            raise ValueError(f"Unsupported email provider: {self.provider}")
    
    def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None) -> bool:
        """Send email using the configured provider"""
        try:
            return self._service.send_email(to_email, subject, html_content, text_content)
        except Exception as e:
            logger.error(f"Failed to send email via {self.provider}: {e}")
            return False
    
    def send_loan_status_notification(self, loan_data: Dict[str, Any], old_status: str, new_status: str) -> bool:
        """Send loan status change notification"""
        try:
            return self._service.send_loan_status_notification(loan_data, old_status, new_status)
        except Exception as e:
            logger.error(f"Failed to send loan status notification via {self.provider}: {e}")
            return False
