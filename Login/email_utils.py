import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string

def generate_confirmation_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

def send_confirmation_email(email, confirmation_code):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "killerbaohuy@gmail.com"
    app_password = "nmuy ptir phxq wehs"

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = email
    msg["Subject"] = "Xác nhận đặt lại mật khẩu"

    body = f"Mã xác nhận của bạn là: {confirmation_code}"
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, app_password)
        text = msg.as_string()
        server.sendmail(sender_email, email, text)
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Error: {e}")