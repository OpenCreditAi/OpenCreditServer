#!/usr/bin/env python3
"""
Simple email test to verify Gmail App Password
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_gmail_connection():
    """Test Gmail connection with App Password"""
    
    # Your Gmail credentials
    email_user = "yonatansinay@gmail.com"
    email_password = "your-16-character-app-password-here"  # Replace with your actual 16-character App Password
    
    # Test email
    to_email = "yonatansinay@gmail.com"  # Send to yourself
    subject = "Test Email from OpenCredit"
    body = "This is a test email to verify the Gmail App Password is working correctly."
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to Gmail
        print(f"Connecting to Gmail SMTP server...")
        print(f"Email: {email_user}")
        print(f"Password length: {len(email_password)} characters")
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        print("Attempting to login...")
        server.login(email_user, email_password)
        
        print("Login successful! Sending email...")
        server.send_message(msg)
        server.quit()
        
        print("✅ Email sent successfully!")
        print(f"Check your inbox at {to_email}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print("❌ Authentication failed!")
        print(f"Error: {e}")
        print("\nPossible solutions:")
        print("1. Make sure 2FA is enabled on your Google account")
        print("2. Generate a new App Password (16 characters)")
        print("3. Use the App Password, not your regular password")
        print("4. Make sure there are no spaces in the App Password")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("Gmail App Password Test")
    print("======================")
    print("This will test your Gmail App Password directly")
    print()
    
    test_gmail_connection()
