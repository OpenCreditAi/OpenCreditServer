# Email Notification System Setup

This document explains how to set up and use the email notification system for loan status changes in the OpenCredit Flask backend.

## Features

- ✅ **Beautiful HTML Email Templates** - Professional Hebrew emails with RTL support
- ✅ **Special PAID Status Email** - Celebration template with green gradient
- ✅ **Status Change Notifications** - Regular updates for all status changes
- ✅ **Responsive Design** - Works on all email clients
- ✅ **Error Handling** - Graceful failure if email service is down
- ✅ **Security** - Uses environment variables for credentials

## Quick Setup

### 1. Install Dependencies

The email functionality uses Python's built-in `smtplib` and `email` libraries, so no additional packages are needed beyond what's already in `requirements.txt`.

### 2. Environment Variables

Add these environment variables to your `.env` file or set them in your system:

```bash
# Email Configuration
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### 3. Gmail Setup (Recommended)

If using Gmail, follow these steps:

1. **Enable 2-Factor Authentication** on your Google account
2. **Generate an App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a password for "Mail"
   - Use this password in `EMAIL_PASSWORD`

### 4. Test the Email Service

Run the test script to verify your email configuration:

```bash
python test_email.py
```

**Important**: Update the email addresses in `test_email.py` before running!

## API Usage

### Update Loan Status with Email Notification

**Endpoint**: `PUT /loans/{id}/status`

**Headers**:
```
Authorization: Bearer <your-jwt-token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "status": "PAID"
}
```

**Valid Status Values**:
- `PROCESSING_DOCUMENTS` (0)
- `MISSING_DOCUMENTS` (1)
- `PENDING_OFFERS` (2)
- `WAITING_FOR_OFFERS` (3)
- `ACTIVE_LOAN` (4)
- `PAID` (5)
- `EXPIRED` (6)

**Response**:
```json
{
  "message": "Loan status updated successfully",
  "loan_id": 123,
  "old_status": "ACTIVE_LOAN",
  "new_status": "PAID",
  "email_sent": true
}
```

### Example Usage

```python
import requests

# Update loan status to PAID
response = requests.put(
    'http://127.0.0.1:5000/loans/123/status',
    headers={
        'Authorization': 'Bearer your-jwt-token',
        'Content-Type': 'application/json'
    },
    json={'status': 'PAID'}
)

print(response.json())
```

## Email Templates

### PAID Status Email
- 🎉 **Special celebration design** with green gradient
- **Large celebration emoji** and congratulatory message
- **Project details** prominently displayed
- **Call-to-action button** for future loans

### Regular Status Change Email
- **Clean, professional design** with blue accent
- **Status change indicator** showing old → new status
- **Project information** in organized format
- **Support contact information**

## Configuration Options

### SMTP Settings

The system supports various SMTP providers:

**Gmail**:
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

**Outlook/Hotmail**:
```bash
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
```

**Custom SMTP**:
```bash
SMTP_SERVER=your-smtp-server.com
SMTP_PORT=587
```

### Email Templates Customization

Templates are defined in `app/services/email_service.py`:

- `_generate_paid_email_template()` - PAID status template
- `_generate_status_change_email_template()` - Regular status changes
- `_generate_text_content()` - Plain text fallback

## Troubleshooting

### Common Issues

1. **"Email credentials not configured"**
   - Check that `EMAIL_USER` and `EMAIL_PASSWORD` are set
   - Verify environment variables are loaded correctly

2. **"Authentication failed"**
   - For Gmail: Use App Password, not regular password
   - Check 2FA is enabled on your Google account
   - Verify email address is correct

3. **"Connection refused"**
   - Check SMTP server and port settings
   - Verify network connectivity
   - Some networks block SMTP ports

4. **"Email not received"**
   - Check spam/junk folder
   - Verify recipient email address
   - Check email service logs

### Debug Mode

Enable debug logging to see detailed email service information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Testing Without Sending Emails

To test the system without actually sending emails, you can modify the `EmailService.send_email()` method to return `True` without sending.

## Security Considerations

- ✅ **Environment Variables** - Credentials stored securely
- ✅ **App Passwords** - Use app-specific passwords, not main passwords
- ✅ **TLS Encryption** - All emails sent over encrypted connection
- ✅ **Input Validation** - Email addresses and content validated
- ✅ **Error Handling** - Sensitive information not exposed in errors

## Production Deployment

### Docker Environment Variables

Add to your `docker-compose.yml`:

```yaml
services:
  web:
    environment:
      - EMAIL_USER=${EMAIL_USER}
      - EMAIL_PASSWORD=${EMAIL_PASSWORD}
      - FROM_EMAIL=${FROM_EMAIL}
      - SMTP_SERVER=${SMTP_SERVER}
      - SMTP_PORT=${SMTP_PORT}
```

### Environment File

Create `.env` file:

```bash
EMAIL_USER=your-production-email@company.com
EMAIL_PASSWORD=your-production-app-password
FROM_EMAIL=noreply@opencredit.co.il
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

## Support

For issues or questions:

1. Check the logs for error messages
2. Verify email configuration
3. Test with the provided test script
4. Contact the development team

---

**Note**: This email system is designed to work with the existing Flask backend. Make sure your Flask app is running and the database is properly configured before testing email functionality.
