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

    main_content = render_template("invoice.html", lines=lines, total_document=total_document
                                   , total_taxes=total_impuestos, total_discounts=total_descuento
                                   , total_sales=total_sales, receiver=receptor, payment_method=payment_methods
                                   , sale_condition=sale_conditions, currency=moneda, currencySymbol=simboloMoneda
                                   , activity_code=activity_code, total_document_words=total_document_words)
    options = {
        '--encoding': 'utf-8'
    }
    add_pdf_header(options, company_data[0], key_mh, document_type, consecutive, date, logo)
    try:
        pdf = pdfkit.from_string(main_content, False, options=options)
    finally:
        os.remove(options['--header-html'])
    return pdf


def add_pdf_header(options, company_data, key_mh, document_type, consecutive, date,  logo):
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as header:
        options['--header-html'] = header.name
        type_iden_company = fe_enums.tipoCedulaPDF[company_data['type_identification']]
        header.write(
            render_template("header.html", company=company_data, key_mh=key_mh, type_iden_company=type_iden_company,
                            type=document_type, consecutive=consecutive, date=date, logo=logo).encode('utf-8')
        )
    return
