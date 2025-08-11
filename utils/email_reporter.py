import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config
from datetime import datetime

class EmailReporter:
    def __init__(self):
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        self.email_user = Config.EMAIL_USER
        self.email_password = Config.EMAIL_PASSWORD
        self.manager_email = Config.MANAGER_EMAIL
    
    def send_report(self, report_data):
        msg = MIMEMultipart()
        msg['From'] = self.email_user
        msg['To'] = self.manager_email
        msg['Subject'] = f"Real Estate Leads Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Create HTML email content
        html = f"""
        <html>
            <body>
                <h2>Real Estate Leads Report</h2>
                <p><strong>Generated at:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                
                <h3>Summary</h3>
                <ul>
                    <li>Total leads: {report_data['total_leads']}</li>
                    <li>High score leads: {report_data['high_score_leads']}</li>
                    <li>New leads in last hour: {report_data['new_leads_last_hour']}</li>
                </ul>
                
                <h3>Top Locations</h3>
                <ol>
                    {''.join(f'<li>{loc[0]} ({loc[1]} leads)</li>' for loc in report_data['top_locations'])}
                </ol>
                
                <h3>Top Property Types</h3>
                <ol>
                    {''.join(f'<li>{ptype[0]} ({ptype[1]} leads)</li>' for ptype in report_data['top_property_types'])}
                </ol>
            </body>
        </html>
        """
        
        msg.attach(MIMEText(html, 'html'))
        
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False