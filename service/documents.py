from . import api_facturae
from . import fe_enums
from . import makepdf
from . import utils

import base64

from service import emails
from infrastructure import companies
from infrastructure import documents
from infrastructure.dbadapter import DbAdapterError, connectToMySql
from email.headerregistry import Address
from datetime import datetime, timedelta
from flask import g

from helpers.errors.enums import InputErrorCodes, ValidationErrorCodes, InternalErrorCodes
from helpers.errors.exceptions import InputError, ValidationError, ServerError
from helpers.utils import build_response_data


def create_document(data):
    _company_user = data['nombre_usuario']
    
    company_data = companies.get_company_data(_company_user)
    if '_error' in company_data:
        return {'error': 'A problem occurred when obtaining the data for the company.'}
    elif '_warning' in company_data:
        return {'error': 'The specified company is not registered in the system.'}

    signature = companies.get_sign_data(_company_user)
    if '_error' in signature:
        return {'error': 'A problem occurred when obtaining the signature information for the company.'}
    elif '_warning' in signature:
        return {
            'error': "No signature information was found for the company; can't sign the document, so the document can't be created."}

    _email_costs = None  # marked for death. Using _additional_emails now
    _additional_emails = []
    _email = None
    _receptor = data.get('receptor')
    # time for spaghetti
    if _receptor:
        try:
            _email = _receptor['correo']
        except KeyError as ker:
            return {'error': 'Missing property in receptor: ' + str(ker)}

        # validate emails
        try:
            _additional_emails = _receptor.get('correosAdicionales')
            if _additional_emails is None or not isinstance(_additional_emails, list):
                _temp = _receptor.get('correo_gastos', '')
                _additional_emails = [_temp] if _temp != '' else []  # falling back to correo_gastos
            else:
                # remove duplicates
                _additional_emails = list(set(_additional_emails))
            validate_email(_email)
            for mail in _additional_emails:
                validate_email(mail)
        except ValueError as ver:  # if we catch a ValueError, email validation failed
            return {'error': 'Invalid email: ' + str(ver)}

    try:
        _type_document = fe_enums.TipoDocumentoApi[data['tipo']]
        _situation = data['situacion']
        _consecutive = data['consecutivo']
        _key_mh = data['clavelarga']
        _terminal = data['terminal']
        _branch = data['sucursal']
        _activity_code = data['codigoActividad']
        _other_phone = data['otro_telefono']
        _sale_condition = data['condicionVenta']
        _credit_term = data['plazoCredito']
        _payment_methods = data['medioPago']
        _lines = data['detalles']
        _currency = data['codigoTipoMoneda']
        _total_serv_taxed = data['totalServGravados']
        _total_serv_untaxed = data['totalServExentos']
        _total_serv_exone = data['totalServExonerado']
        _total_merch_taxed = data['totalMercanciasGravados']
        _total_merch_untaxed = data['totalMercanciasExentos']
        _total_merch_exone = data['totalMercExonerada']
        _total_taxed = data['totalGravados']
        _total_untaxed = data['totalExentos']
        _total_exone = data['totalExonerado']
        _total_sales = data['totalVentas']
        _total_discount = data['totalDescuentos']
        _total_net_sales = data['totalVentasNetas']
        _total_taxes = data['totalImpuestos']
        _total_return_iva = data['totalIVADevuelto']
        _total_other_charges = data['totalOtrosCargos']
        _total_document = data['totalComprobantes']
        _other_charges = data['otrosCargos']
        _reference = data['referencia']
        _others = data['otros']
    except KeyError as ker:
        return {'error': 'Missing property: ' + str(ker)}

    _datestr = api_facturae.get_time_hacienda()
    datecr = api_facturae.get_time_hacienda(True)

    try:
        xml = api_facturae.gen_xml_v43(company_data, _type_document, _key_mh, _consecutive, _datestr, _sale_condition,
                                       _activity_code, _receptor, _total_serv_taxed, _total_serv_untaxed,
                                       _total_serv_exone,
                                       _total_merch_taxed, _total_merch_untaxed, _total_merch_exone,
                                       _total_other_charges,
                                       _total_net_sales, _total_taxes, _total_discount, _lines, _other_charges, _others,
                                       _reference, _payment_methods, _credit_term, _currency, _total_taxed,
                                       _total_exone,
                                       _total_untaxed, _total_sales, _total_return_iva, _total_document)
    except KeyError as ker:  # atm, this is just a baseImponible exception.
        return {'error': str(ker)}
    except Exception as ex:  # todo: be more specific about exceptions
        return {'error': 'An issue was found when building the XML Document: ' + ex}

    xml_to_sign = str(xml)

    try:
        xml_sign = api_facturae.sign_xml(
            signature['signature'],
            company_data['pin_sig'], xml_to_sign)
    except Exception as ex:  # todo: be more specific about exceptions
        return {'error': 'A problem occurred when signing the XML Document.'}

    xmlencoded = base64.b64encode(xml_sign)

    pdfencoded = None;  # Por si no es tiquete que guarde nada como pdf
    if _type_document != 'TE':

        _logo = companies.get_logo_data(_company_user)
        if '_error' in _logo:
            return {'error': 'A problem occuren when attempting to get the Company Logo.'}
        elif '_warning' in _logo:
            return {
                'error': 'No logo was found for the Company.'}  # this shouldn't happen at all, 'cuz we've validated that the company exists above, but... never hurts to leave here, I guess...

        _logo = _logo['logo'].decode('utf-8')
        try:
            pdf = makepdf.render_pdf(company_data, fe_enums.tagNamePDF[_type_document], _key_mh, _consecutive,
                                     datecr.strftime("%d-%m-%Y"), _sale_condition,
                                     _activity_code, _receptor, _total_serv_taxed, _total_serv_untaxed, _total_serv_exone,
                                     _total_merch_taxed, _total_merch_untaxed, _total_merch_exone, _total_other_charges,
                                     _total_net_sales, _total_taxes, _total_discount, _lines, _other_charges, _others,
                                     _reference, _payment_methods, _credit_term, _currency, _total_taxed, _total_exone,
                                     _total_untaxed, _total_sales, _total_return_iva, _total_document, _logo);
        except Exception as ex:  # todo: be more specific about exceptions
            return {'error': 'A problem occured when creating the PDF File for the document.'}
        # Prueba de creacion de correo
        # emails.sent_email(pdf, xml_sign)

        pdfencoded = base64.b64encode(pdf);

    # Managing connection here...
    try:
        conn = connectToMySql()
    except DatabaseError as dbe:
        return {'error': str(dbe) + " The document can't be saved."}

    try:
        try:
            documents.save_document(_company_user, _key_mh, xmlencoded, 'creado', datecr, _type_document,
                                    _receptor, _total_document, _total_taxes, pdfencoded, _email, _email_costs,
                                    connection=conn)
        except DatabaseError as dbe:
            conn.rollback()
            return {'error': str(dbe)}
        except KeyError as ker:
            conn.rollback()
            return {'error': str(ker)}

        try:
            _id_company = company_data['id']
        except KeyError as ker:
            conn.rollback()
            return {'error': 'A problem occurred when saving the document.'}

        if len(_additional_emails) > 0:
            try:
                save_additional_emails(_key_mh, _additional_emails, conn)
            except DatabaseError as dbe:
                conn.rollback()
                return {'error': str(dbe)}

        try:
            save_document_lines(_lines, _id_company, _key_mh, conn)
        except DatabaseError as dbe:
            conn.rollback()
            return {'error': str(dbe)}
        except KeyError as ker:
            conn.rollback()
            return {'error': str(ker)}

        conn.commit()
    finally:
        conn.close()

    return {'message': 'Document successfully created.'}
  

def save_document_lines(lines, id_company, key_mh, conn):
    for _line in lines:
        try:
            _line_number = _line['numero']
            _quantity = _line['cantidad']
            _unity = _line['unidad']
            _detail = _line['detalle']
            _unit_price = _line['precioUnitario']
            _net_tax = _line['impuestoNeto']
            _total_line = _line['totalLinea']
        except KeyError as ker:
            raise KeyError('Missing property in detalles: ' + str(ker))

        try:
            documents.save_document_line_info(id_company, _line_number, _quantity, _unity
                                              , _detail, _unit_price, _net_tax, _total_line, key_mh, connection=conn)
        except DatabaseError as dbe:
            raise

        _taxes = _line.get('impuesto')
        if _taxes:
            try:
                save_document_taxes(_taxes, id_company, _line_number, key_mh, conn)
            except DatabaseError as dbe:
                raise
            except KeyError as ker:
                raise
    return True


def save_document_taxes(taxes, id_company, line_number, key_mh, conn):
    for _tax in taxes:
        try:
            _rate_code = _tax['codigoTarifa']
            _code = _tax['codigo']
            _rate = _tax['tarifa']
            _amount = _tax['monto']
        except KeyError as ker:
            raise KeyError('Missing property in impuesto: ' + str(ker))
        try:
            documents.save_document_line_taxes(id_company, line_number, _rate_code,
                                               _code, _rate, _amount, key_mh, connection=conn)
        except DatabaseError as dbe:
            raise

    return True


def save_additional_emails(key_mh, emails, conn):
    for email in emails:
        documents.save_document_additional_email(key_mh, email, connection=conn)

    return True


def validate_documents():
    return


def validate_document(company_user, key_mh):
    document_data = documents.get_document(key_mh)
    if '_error' in document_data:
        return {'error': 'A problem occurred when attempting to get the document from the database.'}
    elif '_warning' in document_data:
        return {'error': "The specified document wasn't found in the database."}

    company_data = companies.get_company_data(company_user)
    if '_error' in company_data:
        return {'error': 'A problem occurred when attempting to get the company from the database'}
    elif '_warning' in company_data:
        return {'error': "The specified company wasn't found in the database."}

    date_cr = api_facturae.get_time_hacienda(False)
    date = api_facturae.get_time_hacienda(True)

    try:
        token_m_h = api_facturae.get_token_hacienda(company_user, company_data['user_mh'], company_data['pass_mh'],
                                                    company_data['env'])
    except Exception as ex:  # todo: be more specific about exceptions
        return {'error': 'A problem occured when attempting to get the token from Hacienda.'}

    try:
        response_json = api_facturae.send_xml_fe(company_data, document_data, key_mh, token_m_h, date_cr,
                                                 document_data['signxml'],
                                                 company_data['env'])
    except Exception as ex:  # todo: be more specific about exceptions
        return {'error': 'A problem occurred when attempting to send the document to Hacienda.'}

    response_status = response_json.get('status')
    response_text = response_json.get('text')

    if 200 <= response_status <= 299:
        state_tributacion = 'procesando'
        return_message = response_text
    else:
        if response_text.find('ya fue recibido anteriormente') != -1:
            state_tributacion = 'procesando'
            return_message = 'Ya recibido anteriormente, se pasa a consultar'
        else:
            state_tributacion = 'procesando'
            return_message = response_text

    try:
        documents.update_document(company_user, key_mh, None, state_tributacion, date)
    except DatabaseError as dbe:
        return {'error': str(dbe)}

    return {'message': return_message}


def consult_documents():
    return


def consult_document(company_user, key_mh):
    document_data = documents.get_document(key_mh)
    # todo: move this type of validation to a function?
    if '_error' in document_data:
        return {'error': 'A problem occurred when attempting to get the document from the database.'}
    elif '_warning' in document_data:
        return {'error': "The specified document wasn't found in the database."}

    company_data = companies.get_company_data(company_user)
    if '_error' in company_data:
        return {'error': 'A problem occurred when attempting to get the company from the database'}
    elif '_warning' in company_data:
        return {'error': "The specified company wasn't found in the database."}

    date = api_facturae.get_time_hacienda(True)

    try:
        token_m_h = api_facturae.get_token_hacienda(company_user, company_data['user_mh'], company_data['pass_mh'],
                                                    company_data['env'])
    except Exception as ex:
        return {'error': 'A problem occured when attempting to get the token from Hacienda.'}

    try:
        response_json = api_facturae.consulta_documentos(key_mh, company_data['env'], token_m_h, date,
                                                         document_data['document_type'])
    except Exception as ex:  # todo: be more specific about exceptions
        return {'error': 'A problem occurred when attempting to query the document to Hacienda.'}

    response_status = response_json.get('ind-estado')
    response_text = response_json.get('respuesta-xml')

    try:
        documents.update_document(company_user, key_mh, response_text, response_status, date)
    except DatabaseError as dbe:
        return {'error': str(dbe)}
    result = dict()
    if response_status == 'aceptado' and document_data['document_type'] != "TE":
        try:
            emails.sent_email_fe(document_data)
        except Exception as ex:  # todo be more specific about exceptions
            result['warning'] = 'A problem occurred when attempting to send the email.'

    result['message'] = response_status
    result['xml-respuesta'] = response_text
    return result


def consult_document_notdatabase(company_user, key_mh, document_type):
    company_data = companies.get_company_data(company_user)
    if '_error' in company_data:
        return {'error': 'A problem occurred when attempting to get the company from the database'}
    elif '_warning' in company_data:
        return {'error': "The specified company wasn't found in the database."}

    date = api_facturae.get_time_hacienda(True)

    try:
        token_m_h = api_facturae.get_token_hacienda(company_user, company_data['user_mh'], company_data['pass_mh'],
                                                    company_data['env'])
    except Exception as ex:  # todo: be more specific about exceptions
        return {'error': 'A problem occurred when attempting to get the token from Hacienda.'}

    try:
        response_json = api_facturae.consulta_documentos(key_mh, company_data['env'], token_m_h, date,
                                                         document_type)
    except Exception as ex:  # todo: be more specific about exceptions
        return {'error': 'A problem occurred when attempting to fetch the document from Hacienda.'}

    response_status = response_json.get('ind-estado')
    response_text = response_json.get('respuesta-xml')

    if response_text:
        return build_response_data({'message' : response_status, 'data' : {'xml-respuesta' : response_text} })
    else:
        raise ServerError(status=InternalErrorCodes.INTERNAL_ERROR) # TODO : new code: 2 bad data hacienda


def processing_documents(company_user, key_mh, is_consult):
    if is_consult:
        result = consult_document(company_user, key_mh)
    else:
        result = validate_document(company_user, key_mh)
    return result


def document_report(company_user, document_type):
    result = documents.get_documentsreport(company_user, document_type)
    return result


def consult_vouchers(company_user, emisor, receptor, offset, limit):
    company_data = companies.get_company_data(company_user)
    if not company_data:
        raise InputError('company', company_user, status=InputErrorCodes.NO_RECORD_FOUND)

    try:
        token_m_h = api_facturae.get_token_hacienda(company_user, company_data['user_mh'], company_data['pass_mh'],
                                                 company_data['env'])
    except Exception as ex: #TODO : be more specific with exceptions
        raise # TODO : new InternalErrorCode 3 token. return {'error' : 'A problem occurred when attempting to get the token from Hacienda.'} # INTERNAL ERROR

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
    except Exception as ex:  # todo: be more specific with exceptions
        return {'error': "A problem occurred when attempting to get the company's vouchers."}

    response_status = response_json.get('status')
    response_text = response_json.get('text')

    if 200 <= response_status <= 206:
        return build_response_data({'data' : {'Comprobantes' : response_text}})

    else:
        raise ServerError(InternalErrorCodes.INTERNAL_ERROR) # TODO : Hacienda Unauthorized
        # return errors.build_internalerror_error('Hacienda considered the query as unauthorized.')


def consult_voucher_byid(company_user, clave):
    company_data = companies.get_company_data(company_user)
    if not company_data:
        raise InputError('company', company_user, status=InputErrorCodes.NO_RECORD_FOUND)

    try:
        token_m_h = api_facturae.get_token_hacienda(company_user, company_data['user_mh'], company_data['pass_mh'],
                                                company_data['env'])
    except Exception as ex: #TODO : be more specific with exceptions
        raise # TODO : hacienda token error return {'error' : 'A problem occurred when attempting to get the token from Hacienda.'} # INTERNAL ERROR

    try:
        response_json = api_facturae.get_voucher_byid(clave, token_m_h)
    except Exception as ex: #TODO : be more specific with exceptions
        raise # TODO : Internal get voucher error return {'error' : "A problem occurred when attempting to fetch the specified document."} # INTERNAL ERROR

    response_status = response_json.get('status')
    response_text = response_json.get('text')
    if response_status == 200:        
        return build_response_data({ 'data' : {'Comprobante' : response_text} })
    else:
        raise ServerError(InternalErrorCodes.INTERNAL_ERROR)
        # return errors.build_internalerror_error('Hacienda considered the query as unauthorized.')


def validate_email(email):
    """
    Validates an email by parsing it into an email.headerregistry.Address object.

    :param email: str - a string with the email to validate.
    :returns: bool - True if no errors were raised.
    :raises: ValueError - when 'email' is empty, 'email' is not a string, or email can't be parsed by Address, indicating the email is not valid.
    """
    if not email:
        raise ValidationError(status=ValidationErrorCodes.INVALID_EMAIL,
                              message='Empty Email')

    if not isinstance(email, str):
        raise ValidationError(status=ValidationErrorCodes.INVALID_EMAIL,
                              message='Email is not a string')

    try:
        Address(addr_spec=email)
    except (ValueError, IndexError):
        raise ValidationError(email, status=ValidationErrorCodes.INVALID_EMAIL)

    return True

def build_additional_pdf_fields(data):
    DATETIME_DISPLAY_FORMAT = '%d-%m-%Y'

    fields = {}
    order_num = data.get('numReferencia')
    if order_num:
        fields['order_num'] = order_num

    sale_condition = data['condicionVenta']
    if sale_condition == '02':
        issued_date = parse_datetime(data['fechafactura'])
        term_days = data['plazoCredito']
        due_date = data.get('numFecha')
        if isinstance(due_date, str) and due_date.strip():
            fields['due_date'] = parse_datetime(due_date).strftime(DATETIME_DISPLAY_FORMAT)
        else:
            fields['due_date'] = (issued_date + timedelta(days=int(term_days))).strftime(DATETIME_DISPLAY_FORMAT)
        fields['credit_term'] = term_days

    currency = data['codigoTipoMoneda']
    if currency['tipoMoneda'] != 'CRC':
        fields['currency_exchange'] = utils.stringRound(currency['tipoCambio'])

    details = data['detalles']
    for line in details:
        exemption_found = False
        for tax in line.get('impuesto', []):
            exemption = tax.get('exoneracion')
            if exemption:
                fields['exemption'] = {
                    'doc_type': fe_enums.ExemptionDocType[exemption['Tipodocumento']],
                    'doc_number': exemption['NumeroDocumento'],
                    'issuer': exemption['NombreInstitucion'],
                    'issued_date': exemption['FechaEmision'],
                    'percentage': exemption['porcentajeExoneracion'],
                    'total_amount': data['totalExonerado']
                    }
                exemption_found = True
                break
        if exemption_found:
            break

    return fields


def parse_datetime(value):
    EXPECTED_DATETIME_FORMAT = '%d-%m-%YT%H:%M:%S%z'
    parsed = None
    try:
        parsed = datetime.strptime(value, EXPECTED_DATETIME_FORMAT)
    except ValueError:
        try: 
            parsed = datetime.fromisoformat(value)
        except ValueError as ver:
            raise ValidationError(value, 'fechafactura',
                                  status=ValidationErrorCodes.INVALID_DATETIME_FORMAT) from ver

    return parsed
