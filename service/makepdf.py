import os
import tempfile
import pdfkit
from . import fe_enums
from . import utils

from flask import render_template


def render_pdf(company_data, document_type, key_mh, consecutive, date, sale_conditions, activity_code, receptor,
                total_servicio_gravado, total_servicio_exento, totalServExonerado, total_mercaderia_gravado,
                total_mercaderia_exento, totalMercExonerada, totalOtrosCargos, base_total, total_impuestos,
                total_descuento, lines, otrosCargos, invoice_comments, referencia, payment_methods, plazo_credito,
                moneda, total_taxed, total_exone, total_untaxed, total_sales, total_return_iva, total_document, logo,
                additionalFields):

    css = ['templates/bootstrap.min.css']
    total_impuestos = utils.stringRound(total_impuestos)
    total_descuento = utils.stringRound(total_descuento)
    total_sales = utils.stringRound(total_sales)
    total_document = utils.stringRound(total_document)
    total_return_iva = utils.stringRound(total_return_iva)
    for line in lines:
        line['precioUnitario'] = utils.stringRound(line['precioUnitario'])
        line['impuestoNeto'] = utils.stringRound(line['impuestoNeto'])
        line['subtotal'] = utils.stringRound(line['subtotal'])
        line['cantidad'] = utils.stringRound(line['cantidad'])
        line['totalLinea'] = utils.stringRound(line['totalLinea'])

    simboloMoneda = fe_enums.currencies[moneda['tipoMoneda']]

    total_document_words = utils.numToWord(total_document, moneda['tipoMoneda']).upper()

    # @todo: how to get a proper description for code 99 (Others)?
    payment_methods_desc = list(fe_enums.paymentMethods.get(pm.get('codigo'), 'Efectivo') for pm in payment_methods)
    payment_methods_csvs = ', '.join(payment_methods_desc);

    sale_condition_str = fe_enums.saleConditions.get(sale_conditions, 'No especificada')

    re_idType_desc = fe_enums.tipoCedulaPDF.get(receptor.get('tipoIdentificacion'), 'Tipo de identificación no especificada')

    main_content = render_template("invoice.html"
                                   , key_mh=key_mh, lines=lines, total_document=total_document
                                   , total_taxes=total_impuestos, total_discounts=total_descuento
                                   , total_sales=total_sales, receiver=receptor, payment_method=payment_methods_csvs
                                   , sale_condition=sale_condition_str, currency=moneda, currencySymbol=simboloMoneda
                                   , activity_code=activity_code, total_document_words=total_document_words
                                   , date=date , total_returned_iva=total_return_iva
                                   , type_iden_receptor=re_idType_desc
                                   , company=company_data
                                   , **additionalFields)
    options = {
        '--encoding': 'utf-8'
    }
    header_data = {'company' : company_data, 'type' : document_type, 'consecutive' : consecutive,
                   'date' : date, 'logo' : logo, 'key_mh' : key_mh,
                   'type_iden_company' : fe_enums.tipoCedulaPDF.get(company_data.get('type_identification'), 'Tipo de identificación no especificada'),
                   'ref_num' : additionalFields['ref_num']
                  }
    add_pdf_header(options, header_data)
    add_pdf_footer(options, {"notes" : invoice_comments or [], "email" : company_data['email']})
    try:
        pdf = pdfkit.from_string(main_content, False, css=css, options=options)
    finally:
        os.remove(options['--header-html'])
        os.remove(options['--footer-html'])
    return pdf


def add_pdf_header(options, data):
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as header:
        options['--header-html'] = header.name
        header.write(
            render_template("header.html", **data).encode('utf-8')
        )
    return


def add_pdf_footer(options, notes):
    add_temp_section(options, '--footer-html','footer.html', notes)


def add_temp_section(options, section_name, template_name, data):
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as section:
        options[section_name] = section.name
        rendered = render_template(template_name, **data).encode('utf-8')
        section.write(
            rendered
            )
