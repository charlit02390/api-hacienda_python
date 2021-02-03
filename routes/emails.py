import connexion
import json
from service import emails as service
from helpers import utils
from smtplib import SMTPException
from helpers.errors.exceptions import EmailError
from helpers.errors.enums import EmailErrorCodes

def route_send_email():
    file1 = connexion.request.files.get('file1')
    file2 = connexion.request.files.get('file2')
    file3 = connexion.request.files.get('file3')
    body = connexion.request.form
    try: # handling possible exception here until some function refactoring is done...
        result = service.send_custom_email(body, file1, file2, file3)
    except SMTPException as smtpex:
        http_status = EmailError.code
        status = EmailErrorCodes._BASE + utils.get_smtp_error_code(smtpex)
        detail = EmailError.message_dictionary.get(status, EmailError.default_message)
        result = {'http_status': http_status,
                  'status': status,
                  'detail': detail}
    return utils.build_response(result)


def send_email_fe():
    body = json.loads(connexion.request.data)
    try: # handling possible exception here until some function refactoring is done...
        result = service.sent_email_fe(body)
    except SMTPException as smtpex:
        http_status = EmailError.code
        status = EmailErrorCodes._BASE + utils.get_smtp_error_code(smtpex)
        detail = EmailError.message_dictionary.get(status, EmailError.default_message)
        result = {'http_status': http_status,
                  'status': status,
                  'detail': detail}
    return utils.build_response(result)
