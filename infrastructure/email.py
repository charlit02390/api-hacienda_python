import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# @todo: use the new email.message api

def send_email(receiver, subject, content, file1, file2, file3,
               host, sender, password, port, encrypt_type,
               name_file1, name_file2, name_file3): # encrypt_type not used.
    sender_email = sender
        
    # recipient circus 'cuz don't know python well enough
    # use deque for this...
    receiver_email = receiver.pop(0)
    bccs = receiver.copy()
    receiver.insert(0,receiver_email)

    # Create a multipart message and set headers
    # todo: use 'alternative' subtype for crazy formatting?
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # shouldn't this be Cc?
    # Like, if a client specified additional address to receive their mail,
    # it should be fine showing that these other addresses received a Cc.
    if len(bccs) > 0:
        message["Bcc"] = ', '.join(bccs)  # Recommended for mass emails

    # Add body to email
    # todo: use html subtype and specify utf8 charset?
    message.attach(MIMEText(content, "plain"))

    # Open PDF file in binary mode
    if name_file1 != "":
        part = create_email_files(file1, name_file1)
        message.attach(part)

    if name_file2 != "":
        part2 = create_email_files(file2, name_file2)
        message.attach(part2)

    if name_file3 != "":
        part3 = create_email_files(file3, name_file3)
        message.attach(part3)
    # Add attachment to message and convert message to string

    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP(host, port) as server:
        server.starttls(context=context)
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver, text)
    return True

    # TODO : throw this into a custom SMTPError handler
    # for now, all these exceptions are being captured by the InternalServerError
    # handler, being logged and returned with a "nice" message to the user.
    #
    #except smtplib.SMTPConnectError as conne:
    #    raise smtplib.SMTPException(50,
    #                                """There was a problem with the connection to the server.""",
    #                                str(conne)) from conne
    #except smtplib.SMTPNotSupportedError as nosue:
    #    raise smtplib.SMTPException(51,
    #                                """The operation attempted was not supported by the server.""",
    #                                str(nosue)) from nosue
    #except smtplib.SMTPAuthenticationError as authe:
    #    raise smtplib.SMTPException(52,
    #                                """The authentication process failed.""",
    #                                str(authe)) from authe
    #except smtplib.SMTPSenderRefused as sende:
    #    raise smtplib.SMTPException(53,
    #                                """The sender's server refused the request.""",
    #                                str(sende)) from sende
    #except smtplib.SMTPDataError as datae:
    #    raise smtplib.SMTPException(54,
    #                                """The data sent to the server was refused.""",
    #                                str(datae)) from datae
    #except smtplib.SMTPRecipientsRefused as recie:
    #    raise smtplib.SMTPException(55,
    #                                """Mail was refused by all the recipients.""",
    #                                str(recie)) from recie
    

def create_email_files(file, filename):
    part = MIMEBase("application", "octet-stream")
    part.set_payload(file)

    # Encode file in ASCII characters to send by email
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= " + filename
    )
    return part
