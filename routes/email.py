import connexion
from service import email as service


def route_send_email(id):
    file1 = connexion.request.files['file1']
    file2 = connexion.request.files['file2']
    body = connexion.request.form
    result = service.send_email(body, file1, file2, id)
    return result
