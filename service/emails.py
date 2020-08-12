import base64
from infrastructure import company_smtp
from infrastructure import documents
from configuration import globalsettings
from infrastructure.email import send_email
from service import fe_enums

cfg = globalsettings.cfg


def sent_email_fe(data):
    smtp_data = company_smtp.get_company_smtp(data['company_user'])

    if smtp_data.get('host'):
        host = smtp_data[0]['host']
        sender = smtp_data[0]['user']
        password = smtp_data[0]['password']
        port = smtp_data[0]['port']
        encrypt_type = smtp_data[0]['encrypt_type']
    else:
        host = cfg['email']['host']
        sender = cfg['email']['user']
        password = cfg['email']['password']
        port = cfg['email']['port']
        encrypt_type = cfg['email']['type']

    document = documents.get_document(data['key_mh'])[0]
    receivers = document['email']
    subject = "Envio de "+fe_enums.tagNamePDF[document['document_type']] + ' Numero: ' + document['key_mh']
    body = 'Adjuntamos los datos de la ' + fe_enums.tagNamePDF[document['document_type']]

    name_file1 = fe_enums.tagNamePDF[document['document_type']] + '_' + document['key_mh']+'.pdf'
    name_file2 = document['document_type'] + "_" + document['key_mh']+'.xml'
    name_file3 = "AHC_" + document['key_mh']+'.xml'
    file1 = base64.b64decode(document['pdfdocument'])
    file2 = base64.b64decode(document['signxml'])
    file3 = base64.b64decode(document['answerxml'])

    result = send_email(receivers, subject, body, file1, file2, file3, host, sender, password, port,
                        encrypt_type, name_file1, name_file2, name_file3)
    return result


def send_custom_email(data, file1, file2):
    smtp_data = company_smtp.get_company_smtp(data['company_id'])

    receivers = data['receivers']
    subject = data['subject']
    body = data['body']

    name_file1 = file1.filename
    name_file2 = file2.filename
    file1 = file1.stream.read()
    file2 = file2.stream.read()

    host = smtp_data[0]['host']
    sender = smtp_data[0]['user']
    password = smtp_data[0]['password']
    port = smtp_data[0]['port']
    encrypt_type = smtp_data[0]['encrypt_type']


    # todo: lista de receptores pasar a receptor (enviar email a varios usuarios)
    result = send_email(receivers, subject, body, file1, file2,host, sender, password, port,
                        encrypt_type,name_file1, name_file2)
    return result

