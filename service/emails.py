import base64
from infrastructure import company_smtp
from infrastructure import documents
from configuration import globalsettings
from infrastructure.emails import send_email
from service import fe_enums
from helpers.errors.enums import InputErrorCodes
from helpers.errors.exceptions import InputError
from helpers.utils import build_response_data
from helpers.validations.document import KEY_PARTS_SLICES

cfg = globalsettings.cfg


def sent_email_fe(data):
    smtp_data = company_smtp.get_company_smtp(data['nombre_usuario'])

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

    document = documents.get_document(data['clavelarga'])
    if not document:
        raise InputError('document', data['clavelarga'], error_code=InputErrorCodes.NO_RECORD_FOUND)

    primary_recipient = document['email']
    receivers = [primary_recipient]
    additional_recipients = documents.get_additional_emails(data['key_mh'])
    if isinstance(additional_recipients, list):
        receivers += list(x['email'] for x in additional_recipients)

    sequence_slice = KEY_PARTS_SLICES['sequence']
    subject = "Envio de {}: {} del Emisor: {}".format(
        fe_enums.tagNamePDF[document['document_type']],
        document['key_mh'][sequence_slice],
        document['name']
    )

    body = 'Adjuntamos los datos de la ' + fe_enums.tagNamePDF[document['document_type']]

    name_file1 = fe_enums.tagNamePDF[document['document_type']] + '_' + document['key_mh'] + '.pdf'
    name_file2 = document['document_type'] + "_" + document['key_mh'] + '.xml'
    name_file3 = "AHC_" + document['key_mh'] + '.xml'
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
    return build_response_data({'message': 'Email successfully sent.'})


def send_custom_email(data, file1, file2, file3):
    smtp_data = company_smtp.get_company_smtp(data['company_id'])
    if not smtp_data:
        raise InputError('company SMTP', data['company_id'],
                         error_code=InputErrorCodes.NO_RECORD_FOUND)

    receivers = data['receivers'].split(',')
    if not receivers[0]:
        raise InputError(error_code=InputErrorCodes.MISSING_PROPERTY, message='No recipient(s) specified.')

    subject = data['subject']
    content = data['content']
    # wish these were just a list...
    # files are optional, so, let's create a list containing any files given
    attachments = []
    if file1:
        name_file1 = file1.filename
        file1 = file1.stream.read()
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
