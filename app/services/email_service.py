import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from flask import current_app
import logging

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.smtp_server = current_app.config.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = current_app.config.get('SMTP_PORT', 587)
        self.email_user = current_app.config.get('EMAIL_USER')
        self.email_password = current_app.config.get('EMAIL_PASSWORD')
        self.from_email = current_app.config.get('FROM_EMAIL', self.email_user)
        
    def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None) -> bool:
        """
        Send an email to the specified recipient
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text content (optional)
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.email_user or not self.email_password:
            logger.warning("Email credentials not configured. Email not sent.")
            return False
            
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add text content if provided
            if text_content:
                text_part = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(text_part)
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Create secure connection and send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
                
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_loan_status_notification(self, loan_data: Dict[str, Any], old_status: str, new_status: str, recipient_type: str = "borrower") -> bool:
        """
        Send loan status change notification email
        
        Args:
            loan_data: Dictionary containing loan information
            old_status: Previous loan status
            new_status: New loan status
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        # Get recipient email based on type
        if recipient_type == "financier":
            recipient_email = loan_data.get('financier_email')
            recipient_name = loan_data.get('financier_name', 'Financier')
        else:  # borrower
            recipient_email = loan_data.get('borrower_email')
            recipient_name = loan_data.get('borrower_name', 'Borrower')
        
        if not recipient_email:
            logger.warning(f"No {recipient_type} email found for loan status notification")
            return False
            
        # Generate email content based on status
        if new_status == "PAID":
            subject = "🎉 הלוואה שולמה בהצלחה! - OpenCredit"
            html_content = self._generate_paid_email_template(loan_data, old_status, new_status, recipient_type)
        else:
            subject = f"עדכון סטטוס הלוואה - OpenCredit"
            html_content = self._generate_status_change_email_template(loan_data, old_status, new_status, recipient_type)
            
        text_content = self._generate_text_content(loan_data, old_status, new_status, recipient_type)
        
        return self.send_email(recipient_email, subject, html_content, text_content)
    
    def _generate_paid_email_template(self, loan_data: Dict[str, Any], old_status: str, new_status: str, recipient_type: str = "borrower") -> str:
        """Generate HTML template for PAID status email"""
        project_name = loan_data.get('project_name', 'הפרויקט שלך')
        amount = loan_data.get('amount', 0)
        formatted_amount = f"{amount:,}" if amount else "0"
        
        # Personalize greeting based on recipient type
        if recipient_type == "financier":
            recipient_name = loan_data.get('financier_name', 'Financier')
            greeting = f"שלום {recipient_name},"
            message = f"אנו שמחים להודיע לך שהלוואה שהענקת שולמה בהצלחה! 🎊"
        else:  # borrower
            recipient_name = loan_data.get('borrower_name', 'יקר/ה')
            greeting = f"שלום {recipient_name},"
            message = f"אנו שמחים להודיע לך שהלוואה שלך שולמה בהצלחה! 🎊"
        
        return f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="he">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>הלוואה שולמה בהצלחה!</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background: white;
                    border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    margin-top: 20px;
                    margin-bottom: 20px;
                }}
                .header {{
                    text-align: center;
                    background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 15px 15px 0 0;
                    margin: -20px -20px 30px -20px;
                }}
                .celebration {{
                    font-size: 48px;
                    margin-bottom: 10px;
                }}
                .title {{
                    font-size: 28px;
                    font-weight: bold;
                    margin: 0;
                }}
                .subtitle {{
                    font-size: 16px;
                    opacity: 0.9;
                    margin-top: 10px;
                }}
                .content {{
                    padding: 0 20px;
                }}
                .loan-details {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 10px;
                    margin: 20px 0;
                    border-right: 4px solid #4CAF50;
                }}
                .detail-row {{
                    display: flex;
                    justify-content: space-between;
                    margin: 10px 0;
                    padding: 8px 0;
                    border-bottom: 1px solid #e9ecef;
                }}
                .detail-row:last-child {{
                    border-bottom: none;
                }}
                .detail-label {{
                    font-weight: bold;
                    color: #495057;
                }}
                .detail-value {{
                    color: #212529;
                }}
                .amount {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #4CAF50;
                }}
                .status-badge {{
                    background: #4CAF50;
                    color: white;
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-weight: bold;
                    display: inline-block;
                    margin: 10px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding: 20px;
                    background: #f8f9fa;
                    border-radius: 10px;
                    color: #6c757d;
                }}
                .cta-button {{
                    display: inline-block;
                    background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                    color: white;
                    padding: 15px 30px;
                    text-decoration: none;
                    border-radius: 25px;
                    font-weight: bold;
                    margin: 20px 0;
                    transition: transform 0.2s;
                }}
                .cta-button:hover {{
                    transform: translateY(-2px);
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="celebration">🎉</div>
                    <h1 class="title">הלוואה שולמה בהצלחה!</h1>
                    <p class="subtitle">ברכות! הפרויקט שלך הושלם בהצלחה</p>
                </div>
                
                <div class="content">
                    <p>{greeting}</p>
                    
                    <p>{message}</p>
                    
                    <div class="loan-details">
                        <h3 style="margin-top: 0; color: #4CAF50;">פרטי ההלוואה</h3>
                        <div class="detail-row">
                            <span class="detail-label">שם הפרויקט:</span>
                            <span class="detail-value">{project_name}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">סכום ההלוואה:</span>
                            <span class="detail-value amount">{formatted_amount} ₪</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">סטטוס נוכחי:</span>
                            <span class="status-badge">שולם</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">תאריך עדכון:</span>
                            <span class="detail-value">{loan_data.get('updated_at', 'היום')}</span>
                        </div>
                    </div>
                    
                    <p>תודה שבחרת ב-OpenCredit! אנו גאים להיות חלק מהצלחת הפרויקט שלך.</p>
                    
                    <div style="text-align: center;">
                        <a href="#" class="cta-button">צפה בהלוואות נוספות</a>
                    </div>
                </div>
                
                <div class="footer">
                    <p>OpenCredit - הפלטפורמה המובילה להלוואות נדלן</p>
                    <p>לשאלות או תמיכה, צור קשר: support@opencredit.co.il</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _generate_status_change_email_template(self, loan_data: Dict[str, Any], old_status: str, new_status: str, recipient_type: str = "borrower") -> str:
        """Generate HTML template for general status change email"""
        project_name = loan_data.get('project_name', 'הפרויקט שלך')
        amount = loan_data.get('amount', 0)
        formatted_amount = f"{amount:,}" if amount else "0"
        
        # Personalize greeting based on recipient type
        if recipient_type == "financier":
            recipient_name = loan_data.get('financier_name', 'Financier')
            greeting = f"שלום {recipient_name},"
        else:  # borrower
            recipient_name = loan_data.get('borrower_name', 'יקר/ה')
            greeting = f"שלום {recipient_name},"
        
        status_messages = {
            "PROCESSING_DOCUMENTS": "מעבד מסמכים",
            "MISSING_DOCUMENTS": "חסרים מסמכים",
            "PENDING_OFFERS": "ממתין להצעות",
            "WAITING_FOR_OFFERS": "ממתין להצעות",
            "ACTIVE_LOAN": "הלוואה פעילה",
            "PAID": "שולם",
            "EXPIRED": "פג תוקף"
        }
        
        old_status_he = status_messages.get(old_status, old_status)
        new_status_he = status_messages.get(new_status, new_status)
        
        return f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="he">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>עדכון סטטוס הלוואה</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 0;
                    background: #f4f6f9;
                    min-height: 100vh;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                    margin-top: 20px;
                    margin-bottom: 20px;
                }}
                .header {{
                    text-align: center;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 25px;
                    border-radius: 10px 10px 0 0;
                    margin: -20px -20px 25px -20px;
                }}
                .title {{
                    font-size: 24px;
                    font-weight: bold;
                    margin: 0;
                }}
                .subtitle {{
                    font-size: 14px;
                    opacity: 0.9;
                    margin-top: 8px;
                }}
                .content {{
                    padding: 0 20px;
                }}
                .status-change {{
                    background: #e3f2fd;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 20px 0;
                    border-right: 4px solid #2196F3;
                }}
                .status-row {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin: 10px 0;
                }}
                .status-arrow {{
                    font-size: 20px;
                    color: #2196F3;
                }}
                .status-badge {{
                    padding: 6px 12px;
                    border-radius: 15px;
                    font-weight: bold;
                    font-size: 12px;
                }}
                .status-old {{
                    background: #ffecb3;
                    color: #f57c00;
                }}
                .status-new {{
                    background: #c8e6c9;
                    color: #2e7d32;
                }}
                .loan-details {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 20px 0;
                }}
                .detail-row {{
                    display: flex;
                    justify-content: space-between;
                    margin: 8px 0;
                    padding: 6px 0;
                    border-bottom: 1px solid #e9ecef;
                }}
                .detail-row:last-child {{
                    border-bottom: none;
                }}
                .detail-label {{
                    font-weight: bold;
                    color: #495057;
                }}
                .detail-value {{
                    color: #212529;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 25px;
                    padding: 15px;
                    background: #f8f9fa;
                    border-radius: 8px;
                    color: #6c757d;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 class="title">עדכון סטטוס הלוואה</h1>
                    <p class="subtitle">OpenCredit - עדכון חשוב על ההלוואה שלך</p>
                </div>
                
                <div class="content">
                    <p>{greeting}</p>
                    
                    <p>אנו מעדכנים אותך על שינוי בסטטוס ההלוואה שלך:</p>
                    
                    <div class="status-change">
                        <div class="status-row">
                            <span class="status-badge status-old">{old_status_he}</span>
                            <span class="status-arrow">→</span>
                            <span class="status-badge status-new">{new_status_he}</span>
                        </div>
                    </div>
                    
                    <div class="loan-details">
                        <h3 style="margin-top: 0; color: #495057;">פרטי ההלוואה</h3>
                        <div class="detail-row">
                            <span class="detail-label">שם הפרויקט:</span>
                            <span class="detail-value">{project_name}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">סכום ההלוואה:</span>
                            <span class="detail-value">{formatted_amount} ₪</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">תאריך עדכון:</span>
                            <span class="detail-value">{loan_data.get('updated_at', 'היום')}</span>
                        </div>
                    </div>
                    
                    <p>אם יש לך שאלות או זקוק לעזרה, אל תהסס לפנות אלינו.</p>
                </div>
                
                <div class="footer">
                    <p>OpenCredit - הפלטפורמה המובילה להלוואות נדלן</p>
                    <p>לשאלות או תמיכה: support@opencredit.co.il</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _generate_text_content(self, loan_data: Dict[str, Any], old_status: str, new_status: str, recipient_type: str = "borrower") -> str:
        """Generate plain text content for email"""
        project_name = loan_data.get('project_name', 'הפרויקט שלך')
        amount = loan_data.get('amount', 0)
        formatted_amount = f"{amount:,}" if amount else "0"
        
        # Personalize greeting based on recipient type
        if recipient_type == "financier":
            recipient_name = loan_data.get('financier_name', 'Financier')
            greeting = f"שלום {recipient_name},"
        else:  # borrower
            recipient_name = loan_data.get('borrower_name', 'יקר/ה')
            greeting = f"שלום {recipient_name},"
        
        if new_status == "PAID":
            return f"""
            הלוואה שולמה בהצלחה! 🎉
            
            {greeting}
            
            אנו שמחים להודיע לך שהלוואה שלך שולמה בהצלחה!
            
            פרטי ההלוואה:
            - שם הפרויקט: {project_name}
            - סכום ההלוואה: {formatted_amount} ₪
            - סטטוס: שולם
            - תאריך עדכון: {loan_data.get('updated_at', 'היום')}
            
            תודה שבחרת ב-OpenCredit!
            
            OpenCredit - הפלטפורמה המובילה להלוואות נדלן
            לשאלות: support@opencredit.co.il
            """
        else:
            status_messages = {
                "PROCESSING_DOCUMENTS": "מעבד מסמכים",
                "MISSING_DOCUMENTS": "חסרים מסמכים", 
                "PENDING_OFFERS": "ממתין להצעות",
                "WAITING_FOR_OFFERS": "ממתין להצעות",
                "ACTIVE_LOAN": "הלוואה פעילה",
                "PAID": "שולם",
                "EXPIRED": "פג תוקף"
            }
            
            old_status_he = status_messages.get(old_status, old_status)
            new_status_he = status_messages.get(new_status, new_status)
            
            return f"""
            עדכון סטטוס הלוואה
            
            {greeting}
            
            אנו מעדכנים אותך על שינוי בסטטוס ההלוואה שלך:
            {old_status_he} → {new_status_he}
            
            פרטי ההלוואה:
            - שם הפרויקט: {project_name}
            - סכום ההלוואה: {formatted_amount} ₪
            - תאריך עדכון: {loan_data.get('updated_at', 'היום')}
            
            OpenCredit - הפלטפורמה המובילה להלוואות נדלן
            לשאלות: support@opencredit.co.il
            """
