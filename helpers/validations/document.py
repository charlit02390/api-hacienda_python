from re import ASCII, findall
from datetime import datetime

import requests
from email.headerregistry import Address
from email.errors import HeaderParseError

from helpers.errors.exceptions import InputError, ValidationError, ServerError
from helpers.errors.enums import InputErrorCodes, ValidationErrorCodes, InternalErrorCodes
# from helpers.debugging import time_my_func
from helpers.entities.numerics import DecimalMoney as Money
from service.fe_enums import SituacionComprobante

OPTIONAL_RECIPIENT_DOC_TYPES = ('TE', 'FEE', 'NC', 'ND')
CABYS_VALID_LENGTH = 13
BASEIMPONIBLE_REQ_TAX_CODE = '07'
IVAFACTOR_REQ_TAX_CODE = '08'
HACIENDA_API = 'https://api.hacienda.go.cr'
HACIENDA_CABYS_ROUTE = HACIENDA_API + '/fe/cabys'
HACIENDA_TAXCUTS_ROUTE = HACIENDA_API + '/fe/ex'
SERVICE_UNITS = ('Sp', 'Spe', 'St', 'Al', 'Alc')
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
TAXRATE_EXEMPTION_CODE = '01'
TAXRATE_GENERAL_CODE = '08'
TAXRATE_HEALTH_SERVICE_CODE = '04'
PAYMENT_METHOD_CARD_CODE = '02'


def validate_data(data: dict):
    validate_header(data)

    doc_type = data['tipo']
    details = data['detalles']
    validate_details(doc_type, details)

    validate_totals(data)


def validate_header(data: dict):
    doc_type = data['tipo']
    recipient = data.get('receptor')
    validate_recipient(recipient, doc_type)

    sequence = data['consecutivo']
    branch = data['sucursal']
    terminal = data['terminal']
    doctype = data['tipoC'].zfill(2)
    validate_sequence(sequence, branch, terminal, doctype)

    key = data['clavelarga']
    identification = ''.join(findall(r'\d', data['nombre_usuario'], ASCII)).zfill(12)
    date = datetime.fromisoformat(data['fechafactura'])
    circumstance = data['situacion']
    validate_key(key, date, identification, sequence, circumstance)


def validate_key(key: str, date: datetime, identification: str,
                 sequence: str, circumstance: str):
    validate_key_country_code(key)
    validate_key_date(key, date)
    validate_key_identification(key, identification)
    validate_key_sequence(key, sequence)
    validate_key_circumstance(key, circumstance)

    return True


def validate_key_circumstance(key, circumstance):
    circumstance_slice = KEY_PARTS_SLICES['circumstance']
    key_circumstance = key[circumstance_slice]
    circumstance_code = SituacionComprobante[circumstance]
    if key_circumstance != circumstance_code:
        raise ValidationError(
            status=ValidationErrorCodes.INVALID_KEY_COMPOSITION,
            message=('La clave posee un código de circumstancia ({}) que '
                     'no coincide con el especificado ({} => {}).'
                     ).format(key_circumstance, circumstance, circumstance_code)
        )


def validate_key_sequence(key, sequence):
    sequence_slice = KEY_PARTS_SLICES['sequence']
    key_sequence = key[sequence_slice]
    if key_sequence != sequence:
        raise ValidationError(
            message=('La clave posee un consecutivo ({}) que '
                     'no coincide con el del consecutivo especificado ({}).'
                     ).format(key_sequence, sequence),
            status=ValidationErrorCodes.INVALID_KEY_COMPOSITION
        )


def validate_key_identification(key, identification):
    identification_slice = KEY_PARTS_SLICES['identification']
    key_identification = key[identification_slice]
    if key_identification != identification:
        raise ValidationError(
            message=('La clave posee un número de identificación ({}) que '
                     'no coincide con el del usuario especificado ({}).'
                     ).format(key_identification, identification),
            status=ValidationErrorCodes.INVALID_KEY_COMPOSITION
        )


def validate_key_date(key, date):
    dateisof = date.isoformat()
    day = str(date.day).zfill(2)
    validate_key_date_day(key, day, dateisof)
    month = str(date.month).zfill(2)
    validate_key_date_month(key, month, dateisof)
    year = str(date.year)[2: 4]
    validate_key_date_year(key, year, dateisof)


def validate_key_date_year(key, year, dateisof):
    year_slice = KEY_PARTS_SLICES['year']
    key_year = key[year_slice]
    if key_year != year:
        raise ValidationError(
            status=ValidationErrorCodes.INVALID_KEY_COMPOSITION,
            message=('La clave posee un número de año ({}) que '
                     'no coincide con el de la fecha de comprobante '
                     'especificada (fecha: {}; año: {}).'
                     ).format(key_year, dateisof, year)
        )


def validate_key_date_month(key, month, dateisof):
    month_slice = KEY_PARTS_SLICES['month']
    key_month = key[month_slice]
    if key_month != month:
        raise ValidationError(
            status=ValidationErrorCodes.INVALID_KEY_COMPOSITION,
            message=('La clave posee un número de mes ({}) que '
                     'no coincide con el de la fecha de comprobante '
                     'especificada (fecha: {}; mes: {}).'
                     ).format(key_month, dateisof, month)
        )


def validate_key_date_day(key, day, dateisof):
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


def validate_key_country_code(key):
    countrycode_slice = KEY_PARTS_SLICES['countrycode']
    key_countrycode = key[countrycode_slice]
    if key_countrycode != KEY_VALID_COUNTRY_CODE:
        raise ValidationError(
            message=('La clave posee un código de país inválido {}. '
                     'El código de país debe ser {}.'
                     ).format(key_countrycode, KEY_VALID_COUNTRY_CODE),
            status=ValidationErrorCodes.INVALID_KEY_COMPOSITION
        )


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


def validate_recipient(recipient: dict, doc_type: str):
    if recipient is None:
        if doc_type in OPTIONAL_RECIPIENT_DOC_TYPES:
            return True
        else:
            raise ValidationError(
                status=ValidationErrorCodes.INVALID_DOCUMENT,
                message=('El tipo de documento especificado({}) requiere de un '
                         'receptor y este no fue especificado.'
                         .format(doc_type))
            )

    email = recipient['correo']
    additional_emails = recipient.get('correosAdicionales', [])
    if not isinstance(additional_emails, list):
        raise InputError('Receptor>correosAdicionales',
                         'Se recibio como tipo: {}. Se esperaba un arreglo.'
                         .format(str(type(additional_emails))),
                         status=InputErrorCodes.INCORRECT_TYPE)

    for e in (email, *additional_emails):
        validate_email(e)

    return True


def validate_details(doc_type: str, details: list):
    with requests.Session() as sess:
        for line in details:
            validate_line(line, doc_type, sess)


def validate_totals(data: dict):
    calculated_totals = calculate_totals(data)
    for prop, total in calculated_totals.items():
        validate_total(data, prop, total)

    return True


def calculate_totals(data: dict):
    calc_serv_taxed = Money(0)
    calc_serv_exempt = Money(0)
    calc_serv_cut = Money(0)
    calc_merc_taxed = Money(0)
    calc_merc_exempt = Money(0)
    calc_merc_cut = Money(0)
    calc_discounts = Money(0)
    calc_taxes = Money(0)
    calc_returned = Money(0)
    calc_other_charges = Money(0)

    paid_with_card = is_paid_with_card(data['medioPago'])
    details = data['detalles']
    for line in details:
        line_is_service = is_service(line)
        line_is_exempt = is_exempt(line)
        amount_total = Money(line['montoTotal'])
        taxes = line.get('impuesto', ())

        if line_is_exempt:
            taxed = taxcut = Money(0)
            exempt = Money(amount_total)
        else:
            tax_ratio = calculate_tax_ratio(taxes)

            taxed = Money(amount_total * (1 - tax_ratio))
            exempt = Money(0)
            taxcut = Money(amount_total * tax_ratio)

        if line_is_service:
            calc_serv_taxed += taxed
            calc_serv_exempt += exempt
            calc_serv_cut += taxcut
        else:
            calc_merc_taxed += taxed
            calc_merc_exempt += exempt
            calc_merc_cut += taxcut

        calc_discounts += sum(
            Money(d['monto']) for d in line.get('descuento', ())
        )

        calc_taxes += Money(line['impuestoNeto'])

        calc_returned += sum(
            Money(t['monto'])
            for t in taxes
            if paid_with_card
            and line_is_service
            and t['codigoTarifa'] == TAXRATE_HEALTH_SERVICE_CODE
        )

    other_charges = data.get('otrosCargos', ())
    for charge in other_charges:
        calc_other_charges += Money(charge['montoCargo'])

    calc_total_taxed = calc_serv_taxed + calc_merc_taxed
    calc_total_exempt = calc_serv_exempt + calc_merc_exempt
    calc_total_cut = calc_serv_cut + calc_merc_cut
    calc_sales = calc_total_taxed + calc_total_exempt + calc_total_cut
    calc_net_sales = calc_sales - calc_discounts
    calc_total_document = calc_net_sales + calc_taxes + calc_other_charges - calc_returned

    calculated_totals = {
        'totalServGravados': calc_serv_taxed,
        'totalServExentos': calc_serv_exempt,
        'totalServExonerado': calc_serv_cut,
        'totalMercanciasGravados': calc_merc_taxed,
        'totalMercanciasExentos': calc_merc_exempt,
        'totalMercExonerada': calc_merc_cut,
        'totalGravados': calc_total_taxed,
        'totalExentos': calc_total_exempt,
        'totalExonerado': calc_total_cut,
        'totalDescuentos': calc_discounts,
        'totalVentas': calc_sales,
        'totalImpuestos': calc_taxes,
        'totalOtrosCargos': calc_other_charges,
        'totalIVADevuelto': calc_returned,
        'totalVentasNetas': calc_net_sales,
        'totalComprobantes': calc_total_document
    }
    return calculated_totals


def calculate_tax_ratio(taxes):
    taxcut_percentage = get_taxcut_percentage(taxes)
    iva_percentage = get_iva_percentage(taxes)
    if iva_percentage == 0:  # dunno
        raise ValidationError(ValidationErrorCodes.INVALID_DETAIL_LINE,
                              message=('Impuesto inválido: posee una tarifa 0 (exento)'
                                       ', pero, su código de tarifa no corresponde al '
                                       'de un impuesto exento o, el código de impuesto '
                                       'no aplica factor IVA.'))
    if taxcut_percentage > iva_percentage:
        return Money(1)
    else:
        return Money.div(taxcut_percentage, iva_percentage)


def is_paid_with_card(payment_methods: list):
    for pm in payment_methods:
        if pm['codigo'] == PAYMENT_METHOD_CARD_CODE:
            return True

    return False


def is_service(line: dict):
    return line['unidad'] in SERVICE_UNITS


def is_exempt(line: dict):
    if 'impuesto' not in line:
        return True
    else:
        for tax in line['impuesto']:
            if 'codigoTarifa' in tax and \
                    tax['codigoTarifa'] == TAXRATE_EXEMPTION_CODE:
                return True

    return False


def get_taxcut_percentage(taxes: list):
    for tax in taxes:
        if 'exoneracion' in tax:
            for cut in tax['exoneracion']:
                if 'porcentajeExoneracion' in cut:
                    return Money(cut['porcentajeExoneracion'])

    return Money(0)


def get_iva_percentage(taxes: list):
    for tax in sorted(taxes, key=lambda t: t.get('codigo', '99')):
        # uuuuuuuuuuuuuuuuhh... yeah, I don't know
        if 'factorIVA' in tax and tax['factorIVA'].strip():
            return Money.mul((Money(tax['factorIVA']) - 1), 100)
        elif 'tarifa' in tax:
            return Money(tax['tarifa'])

    return Money(0)


def raise_invalid_detail_line(line_number, invalid_prop_name,
                              invalid_prop_value, expected_prop_value,
                              remarks: tuple = None):
    template = ('Linea Detalle #{}: el valor indicado para la propiedad "{}" ({}) '
                'no coincide con el valor calculado {}.')
    if remarks is not None:
        template = ' '.join((template, 'Observaciones:', '\n'.join(remarks)))

    raise ValidationError(status=ValidationErrorCodes.INVALID_DETAIL_LINE,
                          message=template.format(line_number, invalid_prop_name,
                                                  invalid_prop_value, expected_prop_value))


def validate_line(line: dict, doc_type: str,
                  request_session: requests.sessions.Session = None):
    line_number = line['numero']

    cabys = line['codigo']
    check_cabys(cabys, line_number, request_session)

    amount_total_prop = 'montoTotal'
    amount_total = Money(line[amount_total_prop])
    unit_price = Money(line['precioUnitario'])
    amount = Money(line['cantidad'])
    calc_amount_total = Money(amount * unit_price)
    if amount_total != calc_amount_total:
        raise_invalid_detail_line(line_number, amount_total_prop, amount_total,
                                  calc_amount_total)

    subtotal_prop = 'subtotal'
    subtotal = Money(line[subtotal_prop])
    discounts = sum(Money(d['monto']) for d in line.get('descuento', ()))
    calc_subtotal = Money(amount_total - discounts)
    if calc_subtotal != subtotal:
        raise_invalid_detail_line(line_number, subtotal_prop, subtotal,
                                  calc_subtotal)

    calc_net_tax = Money(0)
    taxes = sorted(
        line.get('impuesto', []), key=lambda t: t['codigo'], reverse=True
    )
    tax_subtotal = subtotal  # this subtotal accumulates additional taxes for IVA calcs
    for tax in taxes:
        tax_code = tax['codigo']
        tax_base_prop = 'baseImponible'
        tax_base = line.get(tax_base_prop, '').strip()
        iva_factor_prop = 'factorIVA'
        iva_factor = tax.get(iva_factor_prop, '').strip()
        validate_line_tax_code_uses(tax_code, doc_type, tax_base_prop,
                                    tax_base, iva_factor_prop, iva_factor, line_number)

        tax_amount_prop = 'monto'
        tax_amount = Money(tax[tax_amount_prop])
        if tax_code == IVAFACTOR_REQ_TAX_CODE:
            iva_factor = Money(iva_factor) - 1
            calc_tax_amount = Money(tax_subtotal * iva_factor)
        else:
            tax_rate = Money(tax['tarifa'])
            calc_tax_amount = Money(tax_subtotal * tax_rate / 100)

        if calc_tax_amount != tax_amount:
            raise_invalid_detail_line(line_number, tax_amount_prop, tax_amount,
                                      calc_tax_amount)

        calc_net_tax += tax_amount

        tax_cuts = tax.get('exoneracion', [])
        for cut in tax_cuts:
            authorization = cut['NumeroDocumento']
            #  check_taxcut(authorization, line_number, request_session)

            cut_amount_prop = 'montoExoneracion'
            cut_percentage_prop = 'porcentajeExoneracion'
            cut_amount = Money(cut[cut_amount_prop])
            cut_percentage = cut[cut_percentage_prop]
            validate_line_tax_cut_amount(cut_amount_prop, cut_amount,
                                         cut_percentage, tax_subtotal, line_number)

            calc_net_tax -= cut_amount
            tax_subtotal -= cut_amount

        tax_subtotal += tax_amount

    net_tax_prop = 'impuestoNeto'
    net_tax = Money(line[net_tax_prop])
    if calc_net_tax != net_tax:
        raise_invalid_detail_line(line_number, net_tax_prop, net_tax,
                                  calc_net_tax)

    line_total_prop = 'totalLinea'
    line_total = Money(line[line_total_prop])
    calc_line_total = subtotal + net_tax
    if line_total != calc_line_total:
        raise_invalid_detail_line(line_number, line_total_prop, line_total,
                                  calc_line_total)

    return True


def validate_line_tax_cut_amount(cut_amount_prop, cut_amount,
                                 cut_percentage, line_subtotal, line_number):
    calc_cut_amount = Money(
        line_subtotal * (Money.div(Money(cut_percentage), Money(100)))
    )
    if calc_cut_amount != cut_amount:
        remarks = ('Porcentaje Exoneracion: {}.'.format(cut_percentage),)
        raise_invalid_detail_line(line_number, cut_amount_prop,
                                  cut_amount, calc_cut_amount, remarks)


def validate_line_tax_code_uses(tax_code, doc_type, tax_base_prop, tax_base,
                                iva_factor_prop, iva_factor, line_number):
    if tax_code == BASEIMPONIBLE_REQ_TAX_CODE \
            and doc_type != 'FEE' \
            and tax_base:
        raise ValidationError(
            status=ValidationErrorCodes.INVALID_DETAIL_LINE,
            message=('A la linea #{} le falta un valor requerido'
                     ' para {}. Razón: esta linea incluye un impuesto'
                     ' con código {}'
                     ).format(line_number, tax_base_prop,
                              BASEIMPONIBLE_REQ_TAX_CODE)
        )

    elif tax_code == IVAFACTOR_REQ_TAX_CODE \
            and not iva_factor:
        raise ValidationError(
            status=ValidationErrorCodes.INVALID_DETAIL_LINE,
            message=('A la linea #{}, en los detalles de impuesto,'
                     ' falta un valor requerido para {}. Razón: los'
                     ' impuestos con código {} requieren un monto en'
                     ' el campo {}.'
                     ).format(line_number, iva_factor_prop,
                              IVAFACTOR_REQ_TAX_CODE)
        )


def validate_total(data: dict, prop: str, calc_total: Money):
    total = Money(data[prop])
    if calc_total != total:
        raise ValidationError(status=ValidationErrorCodes.INVALID_TOTAL,
                              message=('El valor indicado para la propiedad "{}" ({}) '
                                       "no coincide con el valor calculado {}.")
                              .format(prop, total, calc_total))

    return True


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


def check_taxcut(authorization: str, line_number: int,
                 request_session: requests.sessions.Session):
    params = {'autorizacion': authorization}
    response = requests_get(endpoint=HACIENDA_TAXCUTS_ROUTE,
                            params=params, request_session=request_session)

    if response.status_code != 200:
        if response.status_code == 404:
            raise ValidationError(
                status=ValidationErrorCodes.TAXCUT_AUTH_NOT_FOUND,
                message=('La linea #{} posee una exoneración con un '
                         'número de documento "{}" no encontrado en Hacienda.'
                         ).format(line_number, authorization))
        else:
            raise ServerError(message=('Se presentó un problema al consultar '
                                       'el documento de autorización de la exoneración '
                                       'en Hacienda.'))

    return True


def check_cabys(code: str, line_number: str,
                request_session: requests.sessions.Session = None):
    code_len = len(code.strip())
    if code_len != CABYS_VALID_LENGTH:
        raise ValidationError(
            status=ValidationErrorCodes.INVALID_CABYS,
            message=('La linea #{} posee un código CABYS con una'
                     ' longitud inválida de {} caracteres. La longitud debe'
                     ' ser exactamente de {} caracteres.'
                     ).format(line_number, code_len,
                              CABYS_VALID_LENGTH))

    params = {'codigo': code}
    response = requests_get(HACIENDA_CABYS_ROUTE,
                            params=params, request_session=request_session)

    if response.status_code == 200:
        json = response.json()
        if len(json) == 0:  # hacienda returns a json array
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


def requests_get(endpoint: str, params: dict, timeout: int = 4,
                 request_session: requests.sessions.Session = None):
    try:
        if request_session is not None:
            response = request_session.get(endpoint,
                                           params=params,
                                           timeout=timeout)
        else:
            response = requests.get(endpoint,
                                    params=params,
                                    timeout=timeout)
    except requests.exceptions.RequestException:  # TODO: branch into more specific exceptions
        raise ServerError(message=('Se presentó un problema'
                                   ' al enviar la verificación de CABYS'
                                   ' a Hacienda.'))
    return response
