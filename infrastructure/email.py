import smtplib
import ssl
import logging
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from mimetypes import guess_type
# @todo: use the new email.message api

_logger = logging.getLogger(__name__)

def send_email(receiver, host, sender, port, encrypt_type,
               user, password, subject, content, attachments): # encrypt_type not used.       
    # recipient circus 'cuz don't know python well enough
    # use deque for this...
    recipient_email = receiver.pop(0)
    bccs = receiver.copy()
    receiver.insert(0, recipient_email)

    # Create a multipart message and set headers
    # todo: use 'alternative' subtype for crazy formatting?
    message = MIMEMultipart()
    message["From"] = sender
    message["To"] = recipient_email
    message["Subject"] = subject

    # shouldn't this be Cc?
    # Like, if a client specified additional address to receive their mail,
    # it should be fine showing that these other addresses received a Cc.
    if len(bccs) > 0:
        message["Bcc"] = ', '.join(bccs)  # Recommended for mass emails

    # Add body to email
    # todo: use html subtype and specify utf8 charset? move this to last if using html
    message.attach(MIMEText(content, "plain"))

    if isinstance(attachments, list):
        for att in attachments:
            try: # each attachment should be a dictionary
                file = att['file']
                name = att['name']
            except KeyError as ker:
                _logger.error('Attachment must have a '.format(ker),
                              exc_info=ker)
                raise
            part = create_email_files(file, name)
            message.attach(part)

    # Add attachment to message and convert message to string

    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP(host, port) as server:
        #server.set_debuglevel(2) # comment this out for prod or suffer b64 garbage in logs
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(user, password)
        server.sendmail(sender, receiver, text)
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
    type = guess_type(filename);
    if not type:
        part = MIMEBase("application", "octet-stream")
    else:
        type = type[0].split('/')
        part = MIMEBase(type[0], type[1])
    part.set_payload(file)

    # Encode file in ASCII characters to send by email
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        'attachment; filename="{}"'.format(filename)
    )
    return part
