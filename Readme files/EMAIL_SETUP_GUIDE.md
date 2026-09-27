# Email Setup Guide for Mengo-Hub

## Overview
Mengo-Hub supports multiple email providers for sending notifications, alerts, and reports. Choose the one that works best for your setup.

## Option 1: Gmail with App Password (Recommended for Testing)
### Step 1: Enable 2-Factor Authentication
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification
3. Complete verification steps

### Step 2: Create App Password
1. Return to Security settings
2. Find "App passwords" (only visible if 2FA is enabled)
3. Select "Mail" and "Windows Computer"
4. Generate password (16-character code)

### Step 3: Configure .env
```
EMAIL_PROVIDER=gmail
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-16-char-app-password
EMAIL_SENDER=your-email@gmail.com
EMAIL_SENDER_NAME=Mengo-Hub System
```

### Pros & Cons
✅ Free, easy setup
✅ Reliable delivery
❌ Limited to 500 emails/day for free accounts
---

## Option 2: SendGrid (Recommended for Production)
### Step 1: Create Account
1. Visit https://sendgrid.com/
2. Sign up for free account
3. Create API key in Settings

### Step 2: Configure .env
```
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=SG.your-api-key-here
EMAIL_SENDER=noreply@mengo-hub.com
EMAIL_SENDER_NAME=Mengo-Hub System
```

### Step 3: Verify Sender Email
1. Go to Sender Authentication in SendGrid
2. Add your domain or sender email
3. Complete verification

### Pros & Cons
✅ 100 emails/day free
✅ Great for scaling
✅ Good deliverability
✅ Excellent support
❌ Requires account setup

---
## Option 3: Mailgun (Alternative)
### Step 1: Create Account
1. Visit https://www.mailgun.com/
2. Sign up for free tier
3. Create domain

### Step 2: Configure .env
```
EMAIL_PROVIDER=mailgun
MAILGUN_DOMAIN=your-domain.mailgun.org
MAILGUN_API_KEY=key-your-api-key
EMAIL_SENDER=noreply@mengo-hub.com
EMAIL_SENDER_NAME=Mengo-Hub System
```

### Pros & Cons
✅ 5000 emails/month free
✅ Developer friendly
✅ Excellent API
❌ Needs domain verification

---

## Option 4: AWS SES (For Large Scale)
### Step 1: Create AWS Account
1. Visit https://aws.amazon.com/
2. Create account
3. Go to SES service

### Step 2: Verify Email/Domain
1. In SES console, add your sender email
2. Click verification link
3. Wait for verification status

### Step 3: Configure .env
```
EMAIL_PROVIDER=aws_ses
AWS_SES_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
EMAIL_SENDER=noreply@mengo-hub.com
EMAIL_SENDER_NAME=Mengo-Hub System
```

### Pros & Cons
✅ 200 emails/day free first month
✅ Scales to millions/month
✅ Excellent reputation
❌ Complex setup, requires AWS knowledge

---
## Testing Email Configuration
### Test Endpoint
```bash
curl -X POST http://localhost:5000/api/admin/test-email \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"to_email": "test@example.com"}'
```

### Expected Response
```json
{
  "success": true,
  "message": "Test email sent successfully",
  "email": "test@example.com"
}
```

---
## Environment Variables Summary
|      Variable     |   Required   |              Example              |
|-------------------|--------------|-----------------------------------|
| EMAIL_PROVIDER    |      Yes     | gmail, sendgrid, mailgun, aws_ses |
| EMAIL_SENDER      |      Yes     | noreply@mengo-hub.com             |
| EMAIL_SENDER_NAME |      Yes     | Mengo-Hub System                  |
| SMTP_SERVER       |   For SMTP   | smtp.gmail.com                    |
| SMTP_PORT         |   For SMTP   |               587                 |
| EMAIL_USERNAME    |   For SMTP   | your-email@gmail.com              |
| EMAIL_PASSWORD    |  For SMTP    | app-password-or-regular-password  |
| SENDGRID_API_KEY  | For SendGrid | SG.xxx...                         |
| MAILGUN_DOMAIN    | For Mailgun  | domain.mailgun.org                |
| MAILGUN_API_KEY   | For Mailgun  | key-xxx...                        |
| AWS_SES_REGION    | For AWS SES  | us-east-1                         |
---

## Email Configuration API Endpoints
### Configure Email Provider (Admin Only)
```
POST /api/admin/email-config
Headers: Authorization: Bearer ADMIN_TOKEN
Body: {
  "provider": "gmail",
  "config": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "email@gmail.com",
    "password": "app-password"
  }
}
```

### Get Email Configuration
```
GET /api/admin/email-config
Headers: Authorization: Bearer ADMIN_TOKEN
```

### Send Test Email
```
POST /api/admin/email-config/test
Headers: Authorization: Bearer ADMIN_TOKEN
Body: {
  "to_email": "admin@mengo.com"
}
```

---
## Troubleshooting
### Issue: "Connection refused" on SMTP
**Solution**: Check SMTP server and port in .env, ensure port 587 is open

### Issue: "Authentication failed"
**Solution**: Verify username/password, for Gmail use app password not regular password

### Issue: "Emails not arriving"
**Solution**: Check spam folder, verify sender email is confirmed with provider

### Issue: "Rate limit exceeded"
**Solution**: Upgrade plan or use SendGrid/AWS SES for higher limits

---
## Best Practices
1. **Always use HTTPS** - Email credentials should never be sent over HTTP
2. **Rotate API keys** - Change SendGrid/Mailgun keys regularly
3. **Monitor quota** - Set alerts for email usage
4. **Use separate domains** - Keep transactional emails separate from marketing
5. **Test thoroughly** - Test before deploying to production
6. **Log email failures** - Check logs for delivery issues
7. **Set sender reputation** - Build sender reputation for better deliverability
8. **Use templates** - Use email templates for consistency

---
## Free Tier Limits
| Provider | Free Limit |           Cost/Extra       |
|----------|------------|----------------------------|
|   Gmail  |   500/day  | Included in Google account |
| SendGrid |   100/day  |    $14.95 for 10k/month    |
| Mailgun  | 5000/month |  $0.00048 per email after  |
| AWS SES  | 200/day (first month) | $0.10 per 1000 emails |
---

For more help, visit:
- Gmail: https://support.google.com/mail
- SendGrid: https://sendgrid.com/docs/
- Mailgun: https://documentation.mailgun.com/
- AWS SES: https://docs.aws.amazon.com/ses/
