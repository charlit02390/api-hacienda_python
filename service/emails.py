import smtplib
import ssl
from configuration import globalsettings
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

cfg = globalsettings.cfg


def sent_email(pdf,signxml):
    subject = "An email with attachment from Python"
    body = "This is an email with attachment sent from Python"
    sender_email = cfg['email']['user']
    receiver_email = "yozi0808@gmail.com"
    password = cfg['email']['password']

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    filename = "document.pdf"  # In same directory as script

    # Open PDF file in binary mode

    part = MIMEBase("application", "octet-stream")
    part.set_payload(pdf)

    # Encode file in ASCII characters to send by email
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= example.pdf"
    )

    part2 = MIMEBase("application", "octet-stream")
    part2.set_payload(signxml)

    # Encode file in ASCII characters to send by email
    encoders.encode_base64(part2)

    # Add header as key/value pair to attachment part
    part2.add_header(
        "Content-Disposition",
        f"attachment; filename= FE_comprobante.xml",
    )

    # Add attachment to message and convert message to string
    message.attach(part)
    message.attach(part2)
    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP(cfg['email']['host'], cfg['email']['port']) as server:
        server.starttls(context=context)
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)
