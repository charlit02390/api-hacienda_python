from re import ASCII, findall
from datetime import datetime

import requests
from email.headerregistry import Address
from email.errors import HeaderParseError

from helpers.errors.exceptions import InputError, ValidationError, HaciendaError, ServerError
from helpers.errors.enums import InputErrorCodes, ValidationErrorCodes, InternalErrorCodes
from helpers.debugging import time_my_func
from helpers.entities.numerics import DecimalMoney
from service.fe_enums import SituacionComprobante

CABYS_VALID_LENGTH = 13
BASEIMPONIBLE_REQ_TAX_CODE = '07'
IVAFACTOR_REQ_TAX_CODE = '08'
HACIENDA_ENDPOINT = 'https://api.hacienda.go.cr/fe/cabys'
SERVICE_UNITS = ('Sp','Spe','St')
SEQUENCE_PARTS_SLICES = {
    'branch': slice(0, 3),
    'terminal': slice(3, 8),
    'doctype': slice(8, 10),
}
KEY_PARTS_SLICES = {
    'countrycode': slice(0, 3),
    'day': slice(3, 5),
    'month': slice(5, 7),
    'year': slice(7, 9),
    'identification': slice(9, 21),
    'sequence': slice(21, 41),
    'circumstance': slice(41, 42)
}
KEY_VALID_COUNTRY_CODE = '506'

@time_my_func
def validate_data(data: dict):
    validate_header(data)

    recipient = data.get('receptor')
    validate_recipient(recipient)

    doc_type = data['tipo']
    details = data['detalles']
    validate_details(doc_type, details)

    validate_totals(data)


@time_my_func
def validate_header(data: dict):
    sequence = data['consecutivo']
    branch = data['sucursal']
    terminal = data['terminal']
    doctype = data['tipoC'].zfill(2)
    validate_sequence(sequence, branch, terminal, doctype)

    key = data['clavelarga']
    identification = ''.join(findall('\d', data['nombre_usuario'], ASCII)).zfill(12)
    date = datetime.fromisoformat(data['fechafactura'])
    circumstance = data['situacion']
    validate_key(key, date, identification, sequence, circumstance)


def validate_key(key: str, date: datetime, identification: str,
                 sequence: str, circumstance: str):
    countrycode_slice = KEY_PARTS_SLICES['countrycode']
    key_countrycode = key[countrycode_slice]
    if key_countrycode != KEY_VALID_COUNTRY_CODE:
        raise ValidationError(
            message=('La clave posee un código de país inválido {}. '
                     'El código de país debe ser {}.'
                     ).format(key_countrycode, KEY_VALID_COUNTRY_CODE),
            status=ValidationErrorCodes.INVALID_KEY_COMPOSITION
        )

    day = str(date.day).zfill(2)
    month = str(date.month).zfill(2)
    year = str(date.year)[2 : 4]
    dateisof = date.isoformat()

    day_slice = KEY_PARTS_SLICES['day']
    key_day = key[day_slice]
    if key_day != day:
        raise ValidationError(
            message=('La clave posee un número de día ({}) que '
                     'no coincide con el de la fecha de comprobante '
                     'especificada (fecha: {}; dia: {}).'
                     ).format(key_day, dateisof, day),
            status=ValidationErrorCodes.INVALID_KEY_COMPOSITION
        )

    month_slice = KEY_PARTS_SLICES['month']
    key_month = key[month_slice]
    if key_month != month:
        raise ValidationError(
            message=('La clave posee un número de mes ({}) que '
                     'no coincide con el de la fecha de comprobante '
                     'especificada (fecha: {}; mes: {}).'
                     ).format(key_month, dateisof, month)
        )

    year_slice = KEY_PARTS_SLICES['year']
    key_year = key[year_slice]
    if key_year != year:
        raise ValidationError(
            message=('La clave posee un número de año ({}) que '
                     'no coincide con el de la fecha de comprobante '
                     'especificada (fecha: {}; año: {}).'
                     ).format(key_year, dateisof, year)
        )

    identification_slice = KEY_PARTS_SLICES['identification']
    key_identification = key[identification_slice]
    if key_identification != identification:
        raise ValidationError(
            message=('La clave posee un número de identificación ({}) que '
                     'no coincide con el del usuario especificado ({}).'
                     ).format(key_identification, identification),
            status=ValidationErrorCodes.INVALID_KEY_COMPOSITION
        )

    sequence_slice = KEY_PARTS_SLICES['sequence']
    key_sequence = key[sequence_slice]
    if key_sequence != sequence:
        raise ValidationError(
            message=('La clave posee un consecutivo ({}) que '
                     'no coincide con el del consecutivo especificado ({}).'
                     ).format(key_sequence, sequence),
            status=ValidationErrorCodes.INVALID_KEY_COMPOSITION
        )

    circumstance_slice = KEY_PARTS_SLICES['circumstance']
    key_circumstance = key[circumstance_slice]
    circumstance_code = SituacionComprobante[circumstance]
    if key_circumstance != circumstance_code:
        raise ValidationError(
            message=('La clave posee un código de circumstancia ({}) que '
                     'no coincide con el especificado ({} => {}).'
                     ).format(key_circumstance, circumstance, circumstance_code)
        )

    return True


def validate_sequence(sequence: str, branch: str,
                      terminal: str, doctype: str):
    branch_slice = SEQUENCE_PARTS_SLICES['branch']
    seq_branch = sequence[branch_slice]
    if branch != seq_branch:
        raise ValidationError(
            message=('La sucursal en el consecutivo ({}) no '
                     'coincide con la sucursal provista ({}).'
                     ).format(seq_branch, branch),
            status=ValidationErrorCodes.INVALID_SEQUENCE
        )

    terminal_slice = SEQUENCE_PARTS_SLICES['terminal']
    seq_terminal = sequence[terminal_slice]
    if terminal != seq_terminal:
        raise ValidationError(
            message=('La terminal en el consecutivo ({}) no '
                     'coincide con la terminal provista ({}).'
                     ).format(seq_terminal, terminal),
            status=ValidationErrorCodes.INVALID_SEQUENCE
        )

    doctype_slice = SEQUENCE_PARTS_SLICES['doctype']
    seq_doctype = sequence[doctype_slice]
    if doctype != seq_doctype:
        raise ValidationError(
            message=('El tipo de documento en el consecutivo ({}) no '
                     'coincide con el tipo de documento provisto ({}).'
                     ).format(seq_doctype, doctype),
            status=ValidationErrorCodes.INVALID_SEQUENCE
        )

    return True


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
