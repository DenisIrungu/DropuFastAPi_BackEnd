import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_verification_code(to_email: str, code: str):
    # Gmail SMTP settings
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "dennisirungu73@gmail.com"  
    sender_password = "lmyp jztl vtkb csbp"  

    # Create the email
    subject = "Verification Code for Dropu Profile Update"
    body = f"Your verification code is {code}. It expires in 10 minutes."
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)

        # Send the email
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def send_welcome_email(to_email: str, name: str, temp_password: str, reset_link: str):
    # Gmail SMTP settings
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "dennisirungu73@gmail.com"  
    sender_password = "lmyp jztl vtkb csbp"  

    # Create the email
    subject = "Welcome to Dropu - Your Account Details"
    body = f"""
    Hello {name},

    Your account has been created by an admin. Use the temporary password below to log in within 5 minutes:

    Temporary Password: {temp_password}

    Please reset your password immediately at the following link:
    {reset_link}

    If the link expires, request a new password reset at https://yourapp.com/login.

    Welcome to Dropu!
    """
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)

        # Send the email
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False