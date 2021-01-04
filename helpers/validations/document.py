import requests
from email.headerregistry import Address
from email.errors import HeaderParseError

from helpers.errors.exceptions import InputError, ValidationError, HaciendaError, ServerError
from helpers.errors.enums import InputErrorCodes, ValidationErrorCodes, InternalErrorCodes
from helpers.debugging import time_my_func
from helpers.entities.numerics import DecimalMoney

CABYS_VALID_LENGTH = 13
BASEIMPONIBLE_REQ_TAX_CODE = '07'
IVAFACTOR_REQ_TAX_CODE = '08'
HACIENDA_ENDPOINT = 'https://api.hacienda.go.cr/fe/cabys'
SERVICE_UNITS = ('Sp','Spe','St')

@time_my_func
def validate_data(data: dict):    
    doc_type = data['tipo']

    recipient = data.get('receptor')
    validate_recipient(recipient)

    details = data['detalles']
    validate_details(doc_type, details)

    validate_totals(data)


@time_my_func
def validate_recipient(recipient: dict):
    email = recipient['correo']
    additional_emails = recipient.get('correosAdicionales', [])
    if not isinstance(additional_emails, list):
        raise InputError('Receptor>correosAdicionales',
                         'Se recibio como tipo: {}. Se esperaba un arreglo.'
                         .format(str(type(additional_emails))),
                         status=InputErrorCodes.INCORRECT_TYPE)

    for e in (email, *additional_emails):
        validate_email(e)


@time_my_func
def validate_details(doc_type: str, details: list):
    with requests.Session() as sess:
        for line in details:
            check_tax(doc_type, line)

            line_number = line['numero']
            cabys = line['codigo']
            check_cabys(cabys, line_number, request_session=sess)


# TODO: finish this...?
def validate_totals(data: dict):
    lines_serv_taxed = DecimalMoney(0)
    lines_serv_exempt = DecimalMoney(0)
    lines_serv_cut = DecimalMoney(0)
    lines_merc_taxed = DecimalMoney(0)
    lines_merc_exempt = DecimalMoney(0)
    lines_merc_cut = DecimalMoney(0)
    lines_discounts = DecimalMoney(0)
    lines_taxes = DecimalMoney(0)

    details = data['detalles']
    local_line_number = 1
    for line in details:
        line_number = line['numero']
        if local_line_number != line_number:
            raise ValidationError(status=ValidationErrorCodes.INVALID_DETAIL_LINE,
                                  message=('La linea #{} posee un número'
                                           ' de linea inesperado. Se esperaba {}')
                                  .format(line_number, local_line_number))
        local_line_number += 1

        discounts = line.get('descuento', [])
        for disco in discounts:
            lines_discounts += DecimalMoney(disco['monto'])

        lines_taxes += DecimalMoney(line['impuestoNeto'])

        taxes = line.get('impuesto', [])
        for tax in taxes:
            taxcuts = tax.get('exoneracion', [])
            if isinstance(taxcuts, dict):
                taxcuts = [taxcuts]

            for cut in taxcuts:
                pass


def validate_email(email: str):
    """
    Validates an email by parsing it into an email.headerregistry.Address object.
    
    :param email: str - a string with the email to validate.
    :returns: bool - True if no errors were raised.
    :raises: ValueError - when 'email' is empty,
        'email' is not a string,
        or email can't be parsed by Address,
        indicating the email is not valid.
    """
    if not email:
        raise ValidationError(status=ValidationErrorCodes.INVALID_EMAIL,
                              message='Empty Email')

    if not isinstance(email, str):
        raise ValidationError(status=ValidationErrorCodes.INVALID_EMAIL,
                              message='Email is not a string')

    try:
        Address(addr_spec=email)
    except (ValueError, IndexError, HeaderParseError):
        raise ValidationError(email,
                              status=ValidationErrorCodes.INVALID_EMAIL)

    return True


@time_my_func
def check_tax(doc_type: str, line: dict):
    taxes = line.get('impuesto')
    if not taxes:
        return True

    for tax in taxes:
        tax_code = tax['codigo']
        if tax_code == BASEIMPONIBLE_REQ_TAX_CODE \
                and doc_type != 'FEE':
            if not line.get('baseImponible','').strip():
                raise ValidationError(
                    status=ValidationErrorCodes.INVALID_DETAIL_LINE,
                    message=('A la linea #{} le falta un valor requerido'
                             ' para {}. Razón: esta linea incluye un impuesto'
                             ' con código {}')
                             .format(line['numero'], 'baseImponible',
                                     BASEIMPONIBLE_REQ_TAX_CODE)
                    )

        elif tax_code == IVAFACTOR_REQ_TAX_CODE:
            if not tax.get('factorIVA', '').strip():
                raise ValidationError(
                    status=ValidationErrorCodes.INVALID_DETAIL_LINE,
                    message=('A la linea #{}, en los detalles de impuesto,'
                             ' falta un valor requerido para {}. Razón: los'
                             ' impuestos con código {} requieren un monto en'
                             ' el campo {}.')
                             .format(line['numero'], 'factorIVA',
                                     IVAFACTOR_REQ_TAX_CODE)
                    )

    return True


@time_my_func
def check_cabys(code: str, line_number: str,
                request_session: requests.sessions.Session=None):
    code_len = len(code.strip())
    if code_len != CABYS_VALID_LENGTH:
        raise ValidationError(
            status=ValidationErrorCodes.INVALID_CABYS,
            message=('La linea #{} posee un código CABYS con una'
                ' longitud inválida de {} caracteres. La longitud debe'
                ' ser exactamente de {} caracteres.')
                .format(line_number, code_len,
                        CABYS_VALID_LENGTH))

    params = {'codigo': code}
    timeout = 4
    try:
        if request_session is not None:
            response = request_session.get(HACIENDA_ENDPOINT,
                                           params=params,
                                           timeout=timeout)
        else:
            response = requests.get(HACIENDA_ENDPOINT,
                                    params=params,
                                    timeout=timeout)
    except requests.exceptions.RequestException: # TODO: branch into more specific exceptions
        raise ServerError(message=('Se presentó un problema'
                                   ' al enviar la verificación de CABYS'
                                   ' a Hacienda.'))

    if response.status_code == 200:
        json = response.json()
        if len(json) == 0: #hacienda returns a json array
            raise ValidationError(status=ValidationErrorCodes.CABYS_NOT_FOUND,
                                  message=('La linea #{} posee un código'
                                  ' CABYS que no se encuentra en Hacienda.')
                                  .format(line_number))
    else:
        # TODO: logging
        raise ServerError(status=InternalErrorCodes.HACIENDA_ERROR,
                          message=('La consulta del código CABYS, para la'
                                   ' linea #{}, a Hacienda presentó un problema.')
                                   .format(line_number))


    return True
