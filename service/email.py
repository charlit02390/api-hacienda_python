from infrastructure import email
import json
from infrastructure import company_smtp


def send_email(data, file1, file2, id_company):
    smtp_data = company_smtp.get_company_smtp(id_company)

    _receivers = data['receivers']
    _header = data['header']
    _message = data['message']

    _name_file1 = file1.filename
    _name_file2 = file2.filename
    _file1 = file1.stream.read()
    _file2 = file2.stream.read()

    _host = smtp_data[0]['host']
    _sender = smtp_data[0]['user']
    _password = smtp_data[0]['password']
    _port = smtp_data[0]['port']
    _encrypt_type = smtp_data[0]['encrypt_type']

    # todo: lista de receptores pasar a receptor (enviar email a varios usuarios)
    result = email.send_email(_receivers, _header, _message, _file1, _file2
                              , _host, _sender, _password, _port, _encrypt_type,
                              _name_file1, _name_file2)
    return result


