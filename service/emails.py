import base64
from infrastructure import company_smtp
from infrastructure import documents
from configuration import globalsettings
from infrastructure.emails import send_email
from service import fe_enums
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import ssl
from infrastructure.dbadapter import DatabaseError
import logging
from helpers.errors.enums import InputErrorCodes
from helpers.errors.exceptions import InputError
from helpers.utils import build_response_data

cfg = globalsettings.cfg


def sent_email_fe(data):
    smtp_data = company_smtp.get_company_smtp(data['company_user'])

    if smtp_data:
        host = smtp_data['host']
        sender = smtp_data['sender']
        username = smtp_data['user']
        password = smtp_data['password']
        port = smtp_data['port']
        encrypt_type = smtp_data['encrypt_type']
    else:
        host = cfg['email']['host']
        sender = cfg['email']['sender']
        username = cfg['email']['user']
        password = cfg['email']['password']
        port = cfg['email']['port']
        encrypt_type = cfg['email']['encrypt_type']

    document = documents.get_document(data['key_mh'])
    if not document:
        raise InputError('document', data['key_mh'], status=InputErrorCodes.NO_RECORD_FOUND)

    primaryRecipient = document['email']
    receivers = [primaryRecipient]
    additionalRecipients = documents.get_additional_emails(data['key_mh'])
    if isinstance(additionalRecipients, list):
        receivers += list(x['email'] for x in additionalRecipients)

    subject = "Envio de "+fe_enums.tagNamePDF[document['document_type']] + ' Numero: ' + document['key_mh']
    body = 'Adjuntamos los datos de la ' + fe_enums.tagNamePDF[document['document_type']]

    name_file1 = fe_enums.tagNamePDF[document['document_type']] + '_' + document['key_mh']+'.pdf'
    name_file2 = document['document_type'] + "_" + document['key_mh']+'.xml'
    name_file3 = "AHC_" + document['key_mh']+'.xml'
    file1 = base64.b64decode(document['pdfdocument'])
    file2 = base64.b64decode(document['signxml'])
    file3 = base64.b64decode(document['answerxml'])

    attachments = [
        {'name': name_file1, 'file': file1},
        {'name': name_file2, 'file': file2},
        {'name': name_file3, 'file': file3}
    ]

    send_email(receivers, host, sender, port, encrypt_type,
               username, password, subject, body, attachments)
    return build_response_data({'message' : 'Email successfully sent.'})


def send_custom_email(data, file1, file2, file3):
    smtp_data = company_smtp.get_company_smtp(data['company_id'])
    if not smtp_data:
        raise InputError('company SMTP', data['company_id'], InputErrorCodes.NO_RECORD_FOUND)

    receivers = data['receivers'].split(',')
    if not receivers[0]:
        raise InputError(status=InputErrorCodes.MISSING_PROPERTY, message='No recipient(s) specified.')

    subject = data['subject']
    content = data['content']
    # wish these were just a list...
    # files are optional, so, let's create a list containing any files given
    attachments = []
    if file1:
        name_file1 = file1.filename
        file1 = file1.stream.read() # if this is a FileStorage werkzeug thingie, could prolly just file1.read()... to lazy to test...
        attachments.append({'file': file1, 'name': name_file1})
        
    if file2:
        name_file2 = file2.filename
        file2 = file2.stream.read()
        attachments.append({'file': file2, 'name': name_file2})

    if file3:
        name_file3 = file3.filename
        file3 = file3.stream.read()
        attachments.append({'file': file3, 'name': name_file3})
        
    
    host = smtp_data['host']
    sender = smtp_data['sender']
    username = smtp_data['user']
    password = smtp_data['password']
    port = smtp_data['port']
    encrypt_type = smtp_data['encrypt_type']
    send_email(receivers, host, sender, port, encrypt_type,
               username, password, subject, content, attachments)
    return build_response_data({'message': 'email sent successfully'})


def sent_email(pdf, signxml): # not used. Prolly a prototype to infrastructure.email.send_email

    subject = "An email with attachment from Python"
    body = "This is an email with attachment sent from Python"
    sender_email = cfg['email']['user']
    receiver_email = "charlit02390@gmail.com"
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

