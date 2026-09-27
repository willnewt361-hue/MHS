"""
Email Service Module for Mengo-Hub
Supports multiple email providers: Gmail, SendGrid, Mailgun, AWS SES
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
import json

class EmailService:
    def __init__(self):
        self.provider = os.getenv('EMAIL_PROVIDER', 'gmail').lower()
        self.sender_email = os.getenv('EMAIL_SENDER', 'noreply@mengo-hub.com')
        self.sender_name = os.getenv('EMAIL_SENDER_NAME', 'Mengo-Hub System')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_username = os.getenv('EMAIL_USERNAME')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
        self.mailgun_domain = os.getenv('MAILGUN_DOMAIN')
        self.mailgun_api_key = os.getenv('MAILGUN_API_KEY')
        self.aws_ses_region = os.getenv('AWS_SES_REGION', 'us-east-1')
        
    def send_email(self, to_email, subject, html_content, plain_text=None, cc=None, bcc=None):
        """Send email using configured provider"""
        try:
            if self.provider == 'sendgrid':
                return self._send_sendgrid(to_email, subject, html_content, plain_text, cc, bcc)
            elif self.provider == 'mailgun':
                return self._send_mailgun(to_email, subject, html_content, plain_text, cc, bcc)
            elif self.provider == 'aws_ses':
                return self._send_aws_ses(to_email, subject, html_content, plain_text, cc, bcc)
            else:  # Default to Gmail SMTP
                return self._send_smtp(to_email, subject, html_content, plain_text, cc, bcc)
        except Exception as e:
            print(f'Error sending email to {to_email}: {str(e)}')
            return False
            
    def _send_smtp(self, to_email, subject, html_content, plain_text=None, cc=None, bcc=None):
        """Send email via SMTP (Gmail, etc)"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
            msg['To'] = to_email
            
            if cc:
                msg['Cc'] = cc if isinstance(cc, str) else ','.join(cc)
                
            # Attach plain text and HTML versions
            if plain_text:
                msg.attach(MIMEText(plain_text, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))
            
            # Connect and send
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_username, self.email_password)
            
            recipients = [to_email]
            if cc:
                recipients.extend(cc if isinstance(cc, list) else [cc])
            if bcc:
                recipients.extend(bcc if isinstance(bcc, list) else [bcc])
                
            server.sendmail(self.sender_email, recipients, msg.as_string())
            server.quit()
            
            print(f'Email sent via SMTP to {to_email}')
            return True
        except Exception as e:
            print(f'SMTP error: {str(e)}')
            return False
            
    def _send_sendgrid(self, to_email, subject, html_content, plain_text=None, cc=None, bcc=None):
        """Send email via SendGrid API"""
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail, Email, To, Cc, Bcc, Content
            
            message = Mail(
                from_email=Email(self.sender_email, self.sender_name),
                to_emails=To(to_email),
                subject=subject,
                plain_text_content=plain_text or 'Check HTML version',
                html_content=html_content
            )
            
            if cc:
                for email in (cc if isinstance(cc, list) else [cc]):
                    message.add_cc(Cc(email))
            if bcc:
                for email in (bcc if isinstance(bcc, list) else [bcc]):
                    message.add_bcc(Bcc(email))
                    
            sg = SendGridAPIClient(self.sendgrid_api_key)
            response = sg.send(message)
            
            print(f'Email sent via SendGrid to {to_email}')
            return response.status_code == 202
        except Exception as e:
            print(f'SendGrid error: {str(e)}')
            return False
            
    def _send_mailgun(self, to_email, subject, html_content, plain_text=None, cc=None, bcc=None):
        """Send email via Mailgun API"""
        try:
            import requests
            
            data = {
                'from': f'{self.sender_name} <{self.sender_email}>',
                'to': to_email,
                'subject': subject,
                'html': html_content,
                'text': plain_text or 'Check HTML version'
            }
            
            if cc:
                data['cc'] = cc if isinstance(cc, str) else ','.join(cc)
            if bcc:
                data['bcc'] = bcc if isinstance(bcc, str) else ','.join(bcc)
                
            response = requests.post(
                f'https://api.mailgun.net/v3/{self.mailgun_domain}/messages',
                auth=('api', self.mailgun_api_key),
                data=data
            )
            
            print(f'Email sent via Mailgun to {to_email}')
            return response.status_code == 200
        except Exception as e:
            print(f'Mailgun error: {str(e)}')
            return False
            
    def _send_aws_ses(self, to_email, subject, html_content, plain_text=None, cc=None, bcc=None):
        """Send email via AWS SES"""
        try:
            import boto3
            
            client = boto3.client('ses', region_name=self.aws_ses_region)
            
            destination = {'ToAddresses': [to_email]}
            if cc:
                destination['CcAddresses'] = cc if isinstance(cc, list) else [cc]
            if bcc:
                destination['BccAddresses'] = bcc if isinstance(bcc, list) else [bcc]
                
            response = client.send_email(
                Source=f'{self.sender_name} <{self.sender_email}>',
                Destination=destination,
                Message={
                    'Subject': {'Data': subject},
                    'Body': {
                        'Text': {'Data': plain_text or 'Check HTML version'},
                        'Html': {'Data': html_content}
                    }
                }
            )
            
            print(f'Email sent via AWS SES to {to_email}')
            return True
        except Exception as e:
            print(f'AWS SES error: {str(e)}')
            return False
            
    def send_notification(self, to_email, title, message):
        """Send a simple notification email"""
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px;">
                <div style="background-color: #f5f5f5; padding: 20px; border-radius: 5px;">
                    <h2>{title}</h2>
                    <p>{message}</p>
                    <hr>
                    <p style="color: #999; font-size: 12px;">
                        This is an automated message from Mengo-Hub System.
                    </p>
                </div>
            </body>
        </html>
        """
        return self.send_email(to_email, f'[Mengo-Hub] {title}', html_content)
        
    def send_certificate_notification(self, to_email, student_name, certificate_name):
        """Send certificate award notification"""
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px;">
                <div style="background-color: #f0f4f8; padding: 30px; border-radius: 10px; text-align: center;">
                    <h1>🎓 Certificate Awarded</h1>
                    <p>Congratulations, <strong>{student_name}</strong>!</p>
                    <p style="font-size: 18px; color: #27ae60; margin: 20px 0;">
                        You have been awarded the <strong>{certificate_name}</strong>
                    </p>
                    <p>This is a recognition of your dedication and hard work.</p>
                    <p style="color: #999; font-size: 12px; margin-top: 20px;">
                        View your certificates in your Mengo-Hub dashboard.
                    </p>
                </div>
            </body>
        </html>
        """
        return self.send_email(to_email, 'Certificate Awarded - Mengo-Hub', html_content)
        
    def send_payment_receipt(self, to_email, user_name, amount, transaction_id, method):
        """Send payment receipt email"""
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px;">
                <div style="background-color: #f5f5f5; padding: 20px; border-radius: 5px;">
                    <h2>Payment Receipt</h2>
                    <p>Dear {user_name},</p>
                    <p>Your payment has been successfully processed.</p>
                    <div style="background-color: white; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>Amount:</strong> {amount}</p>
                        <p><strong>Transaction ID:</strong> {transaction_id}</p>
                        <p><strong>Payment Method:</strong> {method}</p>
                        <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                    <p style="color: #999; font-size: 12px;">
                        If you have any questions, please contact our support team.
                    </p>
                </div>
            </body>
        </html>
        """
        return self.send_email(to_email, 'Payment Receipt - Mengo-Hub', html_content)
        
    def send_admin_alert(self, admin_emails, alert_title, alert_message, severity='info'):
        """Send alert to admin users"""
        severity_color = {
            'critical': '#e74c3c',
            'warning': '#f39c12',
            'info': '#3498db'
        }.get(severity, '#3498db')
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px;">
                <div style="background-color: {severity_color}; color: white; padding: 15px; border-radius: 5px;">
                    <h2>[{severity.upper()}] {alert_title}</h2>
                </div>
                <div style="background-color: #f5f5f5; padding: 20px; border-radius: 5px; margin-top: 10px;">
                    <p>{alert_message}</p>
                    <p style="color: #999; font-size: 12px; margin-top: 20px;">
                        Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    </p>
                </div>
            </body>
        </html>
        """
        
        recipients = admin_emails if isinstance(admin_emails, list) else [admin_emails]
        for admin_email in recipients:
            self.send_email(admin_email, f'[ALERT] {alert_title}', html_content)
        
        return True

# Global instance
email_service = EmailService()
