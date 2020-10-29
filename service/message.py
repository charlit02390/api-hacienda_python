# this be too overloaded... will refactor/modulate later...
import logging
from base64 import b64encode, b64decode
from datetime import datetime

import requests
from pytz import timezone
from lxml import etree

from . import api_facturae
from . import fe_enums
from helpers.utils import build_response_data
from helpers.entities.messages import RecipientMessage
from helpers.entities.numerics import DecimalMoney
from helpers.entities.strings import IDN, IDNType
from helpers.errors.enums import InputErrorCodes
from helpers.errors.exceptions import InputError
from infrastructure import companies as dao_company
from infrastructure import message as dao_message
from infrastructure import company_smtp as dao_smtp
from infrastructure import documents as dao_document
from infrastructure import email
from configuration import globalsettings


_logger = logging.getLogger(__name__)
_data_statuses = (200, 206)

cfg = globalsettings.cfg


def create(data: dict):
   if 'data' in data:
       data = data['data']

   message = RecipientMessage()
   message.key = data['claveHacienda'] #ignore clavelarga?

   issuer = data['emisor']
   message.issuerIDN = _get_idn(issuer)

   recipient = data['receptor']
   message.recipientIDN = _get_idn(recipient)
   message.recipientSequenceNumber = data['consecutivo']

   message.code = data['mensaje']
   message.detail = data['detalle']
   message.taxTotalAmount = DecimalMoney(data['montoImpuesto'])
   message.invoiceTotalAmount = DecimalMoney(data['total'])
   message.issueDate = _curr_datetime_cr()


   company_id = data['nombre_usuario']
   company = dao_company.get_company_data(company_id)
   cert = company['signature']
   password = company['pin_sig']

   signed = api_facturae.sign_xml(cert,
                         password,
                         message.toXml())

   encoded = b64encode(signed)

   issuer_email = data.get('correoEmisor')

   dao_message.insert(company_id, message, encoded,
                    'creado', issuer_email=issuer_email)

   return build_response_data({'message': 'Message successfully created.'})


def process_message(key_mh: str):
    message = dao_message.select(key_mh)
    if not message:
        raise InputError('message', key_mh,
                         status=InputErrorCodes.NO_RECORD_FOUND)

    company_user = message['company_user']
    company = dao_company.get_company_data(company_user)
    if not company:
        raise InputError('company', company_user,
                         status=InputErrorCodes.NO_RECORD_FOUND)

    try:
        mh_token = api_facturae.get_token_hacienda(company_user,
                                                   company['user_mh'],
                                                   company['pass_mh'],
                                                   company['env'])
    except Exception as ex:
        raise # TODO: should prolly raise a 400 code, but dunno what to say...?

    if message['status'] == 'creado':
        result = _handle_created_message(company, message, mh_token)
    else:
        result = _handle_sent_message(company, message, mh_token)# query_message(key_mh, mh_token, company['env'])

    return build_response_data(result)
   

def send_mail(document: dict):
    smtp_data = dao_smtp.get_company_smtp(document['company_user'])

    if not smtp_data:
        smtp_data = cfg['email']

    primary_recipient = document.get('email') # using this as a way to tell between invoices and messages... # BIG TODO
    if primary_recipient:
        _send_mail_invoice(document, smtp_data)
    else:
        _send_mail_message(document, smtp_data)

    return build_response_data({'message': 'Email succesfully sent'})




def _handle_created_message(company: dict, message: dict, token: str):
    env = company['env']
    issue_date = message['issue_date']
    key = message['key_mh']
    company_user = company['company_user']
    if isinstance(issue_date, datetime):
        issue_date = issue_date.isoformat()
    document = {
        'key_mh': key,
        'issue_date': issue_date,
        'recipient_seq_number': message['recipient_seq_number'],
        'signed_xml': message['signed_xml']
        }
    issuer = { # these could be an helpers.entities.strings.IDN instance...
        'idn_type': message['issuer_idn_type'],
        'idn_num': message['issuer_idn_num']
        }
    recipient = {
        'idn_type': company['type_identification'],
        'idn_num': company['identification_dni']
        } # end possible helpers.entities.strings.IDN instances

    response = send_document(env=env, document=document,
                             issuer=issuer, token=token, recipient=recipient)
    info = _handle_hacienda_api_response(response)
    if 'error' in info:
        if info['error']['http_status'] == 400: # gotta update only if the response is 400...
            dao_message.update_from_answer(company_user,
                                           key, None, 'procesando',
                                           _curr_datetime_cr())
        return info
    elif 'unexpected' in info:
        return info

    dao_message.update_from_answer(company_user,
                                   key, None, 'procesando',
                                   _curr_datetime_cr())

    result = {
        'message': 'Confirmación recibida exitosamente por Hacienda. Revisar este mismo url nuevamente para consultar su estado.',
        'data': info
        }
    return result


def _handle_sent_message(company: dict, message:dict, token: str):
    response = query_document(company['env'], message['key_mh'],
                              token)
    info = _handle_hacienda_api_response(response)
    if 'error' in info or 'unexpected' in info:
        return info

    status = info.get('ind-estado', '')
    answer_xml = info.get('respuesta-xml')
    dao_message.update_from_answer(company['company_user'],
                                   message['key_mh'], answer_xml, status,
                                   _curr_datetime_cr())

    result = {
        'data': {
            'message': status,
            'xml-respuesta': answer_xml
            }
        }
    if status.lower() == 'aceptado' and message['issuer_email']: # should only send mail if one was given for the issuer
        try:
            send_mail(message)
        except Exception as ex:
            _logger.warning("***Email couldn't be sent for some reason:***",
                            exc_info=ex)
            result['data']['warning'] = 'A problem occurred when attempting to send email.'
    elif status.lower() == 'rechazado' and answer_xml:
        decoded = b64decode(answer_xml)
        parsed_answer_xml = etree.fromstring(decoded)
        result['data']['details'] = parsed_answer_xml.findtext('{*}DetalleMensaje')

    return result


# could use a requests.Session for this and be efficient about headers and connection pooling
# dunno how to go about it... this shouldn't receive the token, then... hmmmm
def send_document(env: str, document: dict, issuer: dict, 
                  token: str, recipient: dict = None):
    endpoint = fe_enums.UrlHaciendaRecepcion[env]

    headers = {'Authorization': 'bearer {}'.format(token),
               'Content-Type': 'application/json'
               }

    xml = document['signed_xml']
    if isinstance(xml, bytes):
        xml = xml.decode('utf-8')

    data = {'clave': document['key_mh'],
            'fecha': document['issue_date'],
            'emisor': {
                'tipoIdentificacion': issuer['idn_type'],
                'numeroIdentificacion': issuer['idn_num']
                },
            'comprobanteXml': xml
            }
    if recipient:
        data['receptor'] = {
                'tipoIdentificacion': recipient['idn_type'],
                'numeroIdentificacion': recipient['idn_num']
                }
    rec_seq_num = document.get('recipient_seq_number')
    if rec_seq_num:
        data['consecutivoReceptor'] = rec_seq_num

    try:
        return requests.post(url=endpoint, json=data, headers=headers)
    except requests.exceptions.RequestException as reqex:
        _logger.error('***requests Exception happened:***',
                      exc_info=reqex)
        raise # TODO: raise an IB_Exception so it looks nice on response


def query_document(env: str, key: str, token: str) -> dict:
    endpoint = fe_enums.UrlHaciendaRecepcion[env] + key

    headers = {'Authorization': 'bearer {}'.format(token),
               'Cache-Control': 'no-cache',
               'Content-Type': 'application/x-www-form-urlencoded'
               }

    try:
        return requests.get(endpoint, headers=headers)
    except requests.exceptions.RequestException as reqex:
        _logger.error('***requests Exception happened:***',
                      exc_info=reqex)
        raise # TODO: raise an IB_Exception so it looks nice on response


def _handle_hacienda_api_response(response: requests.Response):
    if response.status_code in _data_statuses: # responses that return info. Usuarlly from a get request
        try:
            info = response.json()
        except ValueError as ver:
            _logger.error("""***Bad response body received:***
            Response body: {}
            """.format(response.text), exc_info=ver)
            info = {
                'error': {
                    'message': 'Bad response body format received from Hacienda.',
                    'http_status': 400,
                    'code': 400
                    }
                }

    elif response.status_code in (201, 202): # response that confirms creation or reception of a resource. Typically from a post request
        location = response.headers.get('Location', '')
        info = {'location': location}

    elif response.status_code == 400: # response that rejected a request due to not passing validation. Usually from post requests
        val_exc = response.headers.get('validation-exception')
        cause = response.headers.get('X-Error-Cause', '')
        _logger.warning("""**Document not accepted by Hacienda**:
        Validation-Exception: {}
        Cause: {}""".format(val_exc, cause))
        info = { 'error': 
                {
                    'http_status': 400,
                    'code': 400,
                    'details': cause
                    }
                }

    elif response.status_code == 404: # not found response. Either the resource wasn't found or we have the wrong url...
        cause = response.headers.get('X-Error-Cause')
        if not cause:
            cause = 'Bad URL'

        _logger.warning("""**Document not found:**
        Cause: {}""".format(cause))
        info = { 'error':
                {
                    'http_status': 404,
                    'code': 404,
                    'details': cause
                    }
                }

    elif response.status_code == 401:
        _logger.error("""***Authorization challenge failed:
        Response Headers: {}
        Response Body: {}
        Request Headers: {}""".format(response.headers, response.text,
                                      response.request.headers))
        info = {'error': 
                {
                    'http_status': 401,
                    'code': 401,
                    'details': response.reason
                    }
                }

    else: # undocumented Hacienda response.
        _logger.info("""*Undocumented Hacienda response:*
        Status: {}
        Reason: {}
        Content: {}""".format(response.status_code, response.reason,
                              response.text))
        try:
            response.raise_for_status()
            info = {
                'unexpected': {
                    'status': response.status_code,
                    'reason': response.reason,
                    'content': response.text
                    }
                }
        except requests.exceptions.HTTPError as httper:
            info = {'error':
                    {
                        'http_status': response.status_code,
                        'code': response.status_code,
                        'details': response.reason + '/' + response.text
                        }
                    }


    return info


def _send_mail_invoice(document: dict, smtp: dict):
    doc_key = document['key_mh']

    primary_recipient = document['email']
    recipients = [primary_recipient]
    additional_recipients = dao_document.get_additional_emails(
        doc_key)
    if isinstance(additional_recipients, list):
        recipients += list(x['email'] for x in additional_recipients)


    doc_type = document['document_type']
    doc_type_desc = fe_enums.tagNamePDF[doc_type]

    mail_data = {
        'subject': "Envio de {} número: {}".format(doc_type_desc,
                                                   doc_key),
        'body': "Adjuntamos los datos de la {}".format(doc_type_desc),
        'name_file1': "{}_{}.pdf".format(doc_type_desc, doc_key),
        'name_file2': "{}_{}.xml".format(doc_type, doc_key),
        'name_file3': "AHC_{}.xml".format(doc_key),
        'file1': b64decode(document['pdfdocument']),
        'file2': b64decode(document['signxml']),
        'file3': b64decode(document['answerxml'])
        }
    return email.send_email(receivers=recipients, **smtp, **mail_data)


def _send_mail_message(document: dict, smtp: dict):
    primary_recipient = [document['issuer_email']]
    doc_key = document['key_mh']
    doc_message_code = document['code']
    doc_message_code_desc = fe_enums.MessageCodeDesc[doc_message_code]
    doc_message_code_acron = fe_enums.MessageCodeAcronym[doc_message_code]

    file1 = _utf_decode(document['signed_xml'])
    file2 = _utf_decode(document['answer_xml'])

    mail_data = {
        'subject': 'Confirmación de documento número: {}'.format(
            doc_key),
        'body': """Se adjunta el Mensaje Receptor y la respuesta de Hacienda para el documento número: {}
Se confirma el documento con un estado de {}.""".format(
            doc_key, doc_message_code_desc),
        'name_file1': '{}_{}.xml'.format(doc_message_code_acron,
                                         doc_key),
        'name_file2': 'AHC_{}.xml'.format(doc_key),
        'name_file3': "",
        'file1': file1,
        'file2': file2,
        'file3': None
        }
    return email.send_email(receiver=primary_recipient, **smtp,
                            **mail_data)


def _get_idn(data: dict):
    idn_type = data['tipoIdentificacion'].zfill(2)
    idn_number = data['numeroIdentificacion']

    return IDN(IDNType(idn_type), idn_number)


def _curr_datetime_cr(as_isof_string: bool = True):
    now = datetime.now(timezone('America/Costa_Rica'))
    return now if not as_isof_string else now.isoformat()


def _utf_decode(file):
    if isinstance(file, bytes):
        return file.decode('utf-8')
    else:
        return file
