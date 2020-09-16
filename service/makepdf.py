import os
import tempfile
import pdfkit
from . import fe_enums
from . import utils

from flask import render_template, make_response


def render_pdf(company_data, document_type, key_mh, consecutive, date, sale_conditions, activity_code, receptor,
                total_servicio_gravado, total_servicio_exento, totalServExonerado, total_mercaderia_gravado,
                total_mercaderia_exento, totalMercExonerada, totalOtrosCargos, base_total, total_impuestos,
                total_descuento, lines, otrosCargos, invoice_comments, referencia, payment_methods, plazo_credito,
                moneda, total_taxed, total_exone, total_untaxed, total_sales, total_return_iva, total_document, logo):

    css = ['templates/bootstrap.min.css']
    total_impuestos = utils.stringRound(total_impuestos)
    total_descuento = utils.stringRound(total_descuento)
    total_sales = utils.stringRound(total_sales)
    total_document = utils.stringRound(total_document)
    for line in lines:
        line['precioUnitario'] = utils.stringRound(line['precioUnitario'])
        line['impuestoNeto'] = utils.stringRound(line['impuestoNeto'])
        line['subtotal'] = utils.stringRound(line['subtotal'])
        line['cantidad'] = utils.stringRound(line['cantidad'])

    simboloMoneda = fe_enums.currencies[moneda['tipoMoneda']]

    total_document_words = utils.numToWord(total_document)

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
                                   , date=date
                                   , type_iden_receptor=re_idType_desc
                                   , company=company_data)
    options = {
        '--encoding': 'utf-8'
    }
    add_pdf_header(options, company_data, document_type, consecutive, date, logo, key_mh)
    try:
        pdf = pdfkit.from_string(main_content, False, css=css, options=options)
    finally:
        os.remove(options['--header-html'])
    return pdf


def add_pdf_header(options, company_data, document_type, consecutive, date,  logo, key_mh):
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as header:
        options['--header-html'] = header.name
        type_iden_company = fe_enums.tipoCedulaPDF.get(company_data.get('type_identification'), 'Tipo de identificación no especificada')
        header.write(
            render_template("header.html", company=company_data, type_iden_company=type_iden_company,
                            type=document_type, consecutive=consecutive, date=date, logo=logo, key_mh=key_mh).encode('utf-8')
        )
    return
