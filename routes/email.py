import connexion
import json
from service import emails as service


def route_send_email():
    try:
        file1 = connexion.request.files['file1']
        file2 = connexion.request.files['file2']
        file3 = connexion.request.files['file3']
    except KeyError as ker:
        return {'error' : 'Missing file in property: ' + str(ker)}
    body = connexion.request.form
    result = service.send_custom_email(body, file1, file2, file3)
    return result


def send_email_fe():
    body = json.loads(connexion.request.data)
    try:
        result = service.sent_email_fe(body['data'])
    except KeyEror as ker:
        result = {'error' : 'Missing property: ' + str(ker)}
    return result
