import connexion
import json
from service import emails as service


def route_send_email():
    file1 = connexion.request.files['file1']
    file2 = connexion.request.files['file2']
    body = connexion.request.form
    result = service.send_email(body, file1, file2)
    return result


def send_email_fe():
    body = json.loads(connexion.request.data)
    result = service.sent_email_fe(body['data'])
    return result
