import base64
import logging
from functools import partial

from lxml import etree

from . import api_facturae
from . import makepdf
from . import emails
from infrastructure import companies
from infrastructure import documents
from infrastructure.dbadapter import connectToMySql
from helpers.errors.enums import InputErrorCodes, InternalErrorCodes
from helpers.errors.exceptions import InputError, ServerError
from helpers.utils import build_response_data, run_and_summ_collec_job, get_smtp_error_code
from helpers.debugging import log_section
from helpers.validations import document as document_validator
from helpers.arrangers import document as document_arranger

docLogger = logging.getLogger(__name__)


def create_document(data):
    _company_user = data['nombre_usuario']

    company_data = companies.get_company_data(_company_user)
    if not company_data:
        raise InputError('company',
                         _company_user,
                         status=InputErrorCodes.NO_RECORD_FOUND)

    if not company_data['is_active']:
        raise InputError(status=InputErrorCodes.INACTIVE_COMPANY)

    _key_mh = data['clavelarga']
    if documents.verify_exists(_key_mh):
        raise InputError('Document with key {}'.format(_key_mh),
                         status=InputErrorCodes.DUPLICATE_RECORD)

    signature = companies.get_sign_data(_company_user)
    if not signature:
        raise InputError(status=InputErrorCodes.NO_RECORD_FOUND,
                         message=("No signature information was found"
                                  " for the company; can't sign the document,"
                                  " so the document can't be created."))

    xml_data, pdf_data = document_arranger.arrange_data(data)
    document_validator.validate_data(xml_data)

    _type_document = xml_data['tipo']
    _email_costs = None  # MARKED FOR DEATH . Using _additional_emails now
    _additional_emails = []
    _email = None

    _receptor = xml_data.get('receptor')
    if _receptor:
        _email = _receptor['correo']
        _additional_emails = _receptor['correosAdicionales']

    _total_taxes = xml_data['totalImpuestos']
    _lines = xml_data['detalles']
    _total_document = xml_data['totalComprobantes']

    datecr = api_facturae.get_time_hacienda(True)

    try:
        xml = api_facturae.gen_xml_v43(
            company_data=company_data,
            document_type=_type_document,
            key_mh=_key_mh,
            consecutive=xml_data['consecutivo'],
            date=xml_data['fechafactura'],
            sale_conditions=xml_data['condicionVenta'],
            activity_code=xml_data['codigoActividad'],
            receptor=_receptor,
            total_servicio_gravado=xml_data['totalServGravados'],
            total_servicio_exento=xml_data['totalServExentos'],
            totalServExonerado=xml_data['totalServExonerado'],
            total_mercaderia_gravado=xml_data['totalMercanciasGravados'],
            total_mercaderia_exento=xml_data['totalMercanciasExentos'],
            totalMercExonerada=xml_data['totalMercExonerada'],
            totalOtrosCargos=xml_data['totalOtrosCargos'],
            base_total=xml_data['totalVentasNetas'],
            total_impuestos=_total_taxes,
            total_descuento=xml_data['totalDescuentos'],
            lines=_lines,
            otrosCargos=xml_data.get('otrosCargos'),
            invoice_comments=xml_data.get('otros'),
            referencia=xml_data.get('referencia'),
            payment_methods=xml_data['medioPago'],
            plazo_credito=xml_data['plazoCredito'],
            moneda=xml_data['codigoTipoMoneda'],
            total_taxed=xml_data['totalGravados'],
            total_exone=xml_data['totalExonerado'],
            total_untaxed=xml_data['totalExentos'],
            total_sales=xml_data['totalVentas'],
            total_return_iva=xml_data['totalIVADevuelto'],
            total_document=_total_document
        )
    except KeyError as ker:  # atm, this is just a baseImponible exception.
        raise  # TODO : return {'error' : str(ker)} # INVALID DOCUMENT ERROR #TODO

    xml_to_sign = str(xml)

    try:
        xml_sign = api_facturae.sign_xml(
            signature['signature'],
            company_data['pin_sig'], xml_to_sign
        )
    except Exception as ex:  # todo: be more specific about exceptions #TODO
        raise  # TODO : return {'error' : 'A problem occurred when signing the XML Document.'}  # INTERNAL ERROR

    xmlencoded = base64.b64encode(xml_sign)

    pdfencoded = None  # Por si ES tiquete que guarde nada como pdf
    if pdf_data is not None:  # _type_document != 'TE':
        _logo = companies.get_logo_data(_company_user)
        _logo = _logo['logo']
        if _logo is not None:
            _logo = _logo.decode('utf-8')

        try:
            pdf = makepdf.render_pdf(company_data,
                                     _logo,
                                     pdf_data)
        except Exception as ex:  # TODO : be more specific about exceptions
            raise  # TODO : 'A problem occured when creating the PDF File for the document.' # INTERNAL ERROR
        # Prueba de creacion de correo
        # emails.sent_email(pdf, xml_sign)
        pdfencoded = base64.b64encode(pdf)

    # return {'status': 'procesando...'}
    # Managing connection here...
    conn = connectToMySql()

    try:
        documents.save_document(_company_user, _key_mh, xmlencoded,
                                'creado', datecr, _type_document,
                                _receptor, _total_document, _total_taxes,
                                pdfencoded, _email, _email_costs,
                                connection=conn)

        _id_company = company_data['id']

        if len(_additional_emails) > 0:
            save_additional_emails(_key_mh, _additional_emails, conn)

        save_document_lines(_lines, _id_company, _key_mh, conn)
        conn.commit()
    finally:
        conn.close()

    return {
        'status': 'procesando',
        'message': 'Document successfully created.'
    }


def save_document_lines(lines, id_company, key_mh, conn):
    for _line in lines:
        _line_number = _line['numero']
        _quantity = _line['cantidad']
        _unity = _line['unidad']
        _detail = _line['detalle']
        _unit_price = _line['precioUnitario']
        _net_tax = _line['impuestoNeto']
        _total_line = _line['totalLinea']

        documents.save_document_line_info(id_company, _line_number,
                                          _quantity, _unity, _detail, _unit_price,
                                          _net_tax, _total_line, key_mh, connection=conn)

        _taxes = _line.get('impuesto')
        if _taxes:
            save_document_taxes(_taxes, id_company, _line_number,
                                key_mh, conn)

    return True


def save_document_taxes(taxes, id_company, line_number, key_mh, conn):
    for _tax in taxes:
        _rate_code = _tax.get('codigoTarifa')
        _code = _tax['codigo']
        _rate = _tax['tarifa']
        _amount = _tax['monto']

        documents.save_document_line_taxes(id_company, line_number,
                                           _rate_code, _code, _rate, _amount,
                                           key_mh, connection=conn)

    return True


def save_additional_emails(key_mh, _emails, conn):
    for email in _emails:
        documents.save_document_additional_email(key_mh, email,
                                                 connection=conn)

    return True


@log_section('Sending Documents')
def validate_documents():
    item_cb = validate_document
    collec_cb_args = (0,)
    return _run_and_summ_docs_job(item_cb=item_cb,
                                  collec_cb_args=collec_cb_args)


def validate_document(company_user, key_mh):
    document_data = documents.get_document(key_mh)
    if not document_data:
        raise InputError('document', str(key_mh),
                         status=InputErrorCodes.NO_RECORD_FOUND)

    company_data = companies.get_company_data(company_user)
    if not company_data:
        raise InputError('company', str(company_user),
                         status=InputErrorCodes.NO_RECORD_FOUND)

    if not company_data['is_active']:
        raise InputError(status=InputErrorCodes.INACTIVE_COMPANY)

    date_cr = api_facturae.get_time_hacienda(False)
    date = api_facturae.get_time_hacienda(True)

    try:
        token_m_h = api_facturae.get_token_hacienda(company_user,
                                                    company_data['user_mh'],
                                                    company_data['pass_mh'],
                                                    company_data['env'])
    except Exception as ex:  # TODO : be more specific about exceptions
        raise  # TODO : 'A problem occured when attempting to get the token from Hacienda.' # INTERNAL ERROR

    try:
        response_json = api_facturae.send_xml_fe(company_data,
                                                 document_data, key_mh, token_m_h,
                                                 date_cr,
                                                 document_data['signxml'],
                                                 company_data['env'])
    except Exception as ex:  # TODO : be more specific about exceptions
        raise  # TODO: 'error' : 'A problem occurred when attempting to send the document to Hacienda.' # INTERNAL ERROR

    response_status = response_json.get('status')
    response_text = response_json.get('text')

    if 200 <= response_status <= 299:
        state_tributacion = 'procesando'
        return_message = state_tributacion
    else:
        if response_text.find('ya fue recibido anteriormente') != -1:
            state_tributacion = 'procesando'
            return_message = 'Ya recibido anteriormente, se pasa a consultar'
        else:
            state_tributacion = 'procesando'
            return_message = response_text

    documents.update_document(company_user, key_mh, None,
                              state_tributacion, date)

    return {
        'status': state_tributacion,
        'message': return_message
    }


@log_section('Fetching Documents\' Statuses')
def consult_documents():
    item_cb = consult_document
    collec_cb_args = (1,)
    return _run_and_summ_docs_job(item_cb=item_cb,
                                  collec_cb_args=collec_cb_args)


def consult_document(company_user, key_mh):
    document_data = documents.get_document(key_mh)
    if not document_data:
        raise InputError('document', key_mh,
                         status=InputErrorCodes.NO_RECORD_FOUND)

    company_data = companies.get_company_data(company_user)
    if not company_data:
        raise InputError('company', company_user,
                         status=InputErrorCodes.NO_RECORD_FOUND)

    if not company_data['is_active']:
        raise InputError(status=InputErrorCodes.INACTIVE_COMPANY)

    date = api_facturae.get_time_hacienda(True)

    try:
        token_m_h = api_facturae.get_token_hacienda(company_user,
                                                    company_data['user_mh'],
                                                    company_data['pass_mh'],
                                                    company_data['env'])
    except Exception as ex:  # TODO
        raise  # TODO : 'error' : 'A problem occured when attempting to get the token from Hacienda.' # INTERNAL ERROR

    try:
        response_json = api_facturae.consulta_documentos(key_mh,
                                                         company_data['env'], token_m_h,
                                                         date,
                                                         document_data['document_type'])
    except Exception as ex:  # TODO : be more specific about exceptions
        raise  # TODO : A problem occurred when attempting to query the document to Hacienda.' # INTERNAL ERROR

    response_status = response_json.get('ind-estado')
    response_text = response_json.get('respuesta-xml')

    documents.update_document(company_user, key_mh, response_text,
                              response_status, date)

    result = {
        'status': response_status,
        'data': {
            'date': date
        }
    }
    if response_status == 'aceptado' \
            and document_data['document_type'] != "TE" \
            and document_data['isSent'] is None:
        mail_sent = 0
        try:
            emails.sent_email_fe(document_data)
        except Exception as ex:  # TODO : be more specific about exceptions
            docLogger.warning("***Email couldn't be sent for some reason:***", exc_info=ex)
            result['data']['warning'] = 'A problem occurred when attempting to send the email.'  # WARNING
            # temp juggling insanity... nevermind, don't look at it...
            mail_sent = get_smtp_error_code(ex)

        documents.update_isSent(key_mh, mail_sent)

    if response_text:
        decoded = base64.b64decode(response_text)
        parsed_answer_xml = etree.fromstring(decoded)
        result['data']['detail'] = parsed_answer_xml.findtext(
            '{*}DetalleMensaje'
        ) or ''

    result['data']['xml-respuesta'] = response_text
    return result


def consult_document_notdatabase(company_user, key_mh, document_type):
    company_data = companies.get_company_data(company_user)
    if not company_data:
        raise InputError('company', company_user,
                         status=InputErrorCodes.NO_RECORD_FOUND)

    date = api_facturae.get_time_hacienda(True)

    try:
        token_m_h = api_facturae.get_token_hacienda(company_user,
                                                    company_data['user_mh'],
                                                    company_data['pass_mh'],
                                                    company_data['env'])
    except Exception as ex:  # TODO : be more specific about exceptions
        raise  # TODO 'A problem occurred when attempting to get the token from Hacienda.' # INTERNAL ERROR

    try:
        response_json = api_facturae.consulta_documentos(key_mh,
                                                         company_data['env'],
                                                         token_m_h, date, document_type)
    except Exception as ex:  # TODO : be more specific about exceptions
        raise  # TODO: 'A problem occurred when attempting to fetch the document from Hacienda.' # INTERNAL ERROR

    response_status = response_json.get('ind-estado')
    response_text = response_json.get('respuesta-xml')

    if response_text:
        return build_response_data({'message': response_status,
                                    'data': {'xml-respuesta': response_text}})
    else:
        raise ServerError(status=InternalErrorCodes.INTERNAL_ERROR)  # TODO : new code: 2 bad data hacienda


def processing_documents(company_user, key_mh, is_consult):
    if is_consult:
        result = consult_document(company_user, key_mh)
    else:
        result = validate_document(company_user, key_mh)
    return result


def document_report(company_user, document_type):
    result = documents.get_documentsreport(company_user, document_type)
    return build_response_data({'data': {'documents': result}})


def consult_vouchers(company_user, emisor, receptor, offset, limit):
    company_data = companies.get_company_data(company_user)
    if not company_data:
        raise InputError('company', company_user,
                         status=InputErrorCodes.NO_RECORD_FOUND)

    try:
        token_m_h = api_facturae.get_token_hacienda(company_user,
                                                    company_data['user_mh'],
                                                    company_data['pass_mh'],
                                                    company_data['env'])
    except Exception as ex:  # TODO : be more specific with exceptions
        raise  # TODO:new InternalErrorCode 3 token. A problem occurred when attempting to get the token from Hacienda.'

    parameters = {}
    if emisor is not None:
        parameters['emisor'] = emisor
    if receptor is not None:
        parameters['receptor'] = receptor
    if offset is not None:
        parameters['offset'] = offset
    if limit is not None:
        parameters['limit'] = limit

    try:
        response_json = api_facturae.get_vouchers(token_m_h, parameters)
    except Exception as ex:  # TODO : be more specific with exceptions
        raise  # TODO : "A problem occurred when attempting to get the company's vouchers." # INTERNAL ERROR

    response_status = response_json.get('status')
    response_text = response_json.get('text')

    if 200 <= response_status <= 206:
        return build_response_data({'data': {'Comprobantes': response_text}})
    else:
        raise ServerError(InternalErrorCodes.INTERNAL_ERROR)  # TODO : Hacienda Unauthorized
        # return errors.build_internalerror_error('Hacienda considered the query as unauthorized.')


def consult_voucher_byid(company_user, clave):
    company_data = companies.get_company_data(company_user)
    if not company_data:
        raise InputError('company', company_user,
                         status=InputErrorCodes.NO_RECORD_FOUND)

    try:
        token_m_h = api_facturae.get_token_hacienda(company_user,
                                                    company_data['user_mh'],
                                                    company_data['pass_mh'],
                                                    company_data['env'])
    except Exception as ex:  # TODO : be more specific with exceptions
        raise  # TODO : hacienda token error return 'A problem occurred when attempting to get the token from Hacienda.'

    try:
        response_json = api_facturae.get_voucher_byid(clave, token_m_h)
    except Exception as ex:  # TODO : be more specific with exceptions
        raise  # TODO : Internal get voucher error "A problem occurred when attempting to fetch the specified document."

    response_status = response_json.get('status')
    response_text = response_json.get('text')
    if response_status == 200:
        return build_response_data({'data': {'Comprobante': response_text}})
    else:
        raise ServerError(InternalErrorCodes.INTERNAL_ERROR)
        # return errors.build_internalerror_error('Hacienda considered the query as unauthorized.')


def get_pdf(key: str):
    document = documents.get_document(key)
    if not document:
        raise InputError('document', key,
                         status=InputErrorCodes.NO_RECORD_FOUND)

    if document['pdfdocument']:
        data = {'data': {'pdf': document['pdfdocument']}}
    else:
        data = {
            'message': """The specified document does not have a PDF file.
Document Type: {}
*If the document type is not 'TE', please contact the API Admin.""".format(
                document['document_type'])
        }

    return build_response_data(data)


# if this fails horribly, I will rollback and apply a simpler solution...
_run_and_summ_docs_job = partial(
    run_and_summ_collec_job,
    collec_cb=documents.get_documents,
    item_id_keys='key_mh',
    item_cb_kwargs_map={
        'company_user': 'company_user',
        'key_mh': 'key_mh'
    })
