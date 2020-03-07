import os
import tempfile

import pdfkit

from flask import render_template, make_response


def render_pdf(company_data, document_type, key_mh, consecutive, date, sale_conditions, activity_code, receptor,
                total_servicio_gravado, total_servicio_exento, totalServExonerado, total_mercaderia_gravado,
                total_mercaderia_exento, totalMercExonerada, totalOtrosCargos, base_total, total_impuestos,
                total_descuento, lines, otrosCargos, invoice_comments, referencia, payment_methods, plazo_credito,
                moneda, total_taxed, total_exone, total_untaxed, total_sales, total_return_iva, total_document):

    main_content = render_template("invoice.html", key_mh=key_mh)
    options = {
        '--encoding': 'utf-8'
    }
    add_pdf_header(options, company_data[0], document_type, consecutive, key_mh, receptor, date, payment_methods,
                   sale_conditions, moneda, activity_code)
    pdf = pdfkit.from_string(main_content, False, options=options)

    return pdf


def add_pdf_header(options, company_data, document_type, consecutive, key_mh, receptor, date, payment_method,
                   sale_condition, moneda, activity_code):
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as header:
        options['--header-html'] = header.name
        header.write(
            render_template("header.html", company=company_data, type=document_type, key_mh=key_mh,
                            consecutive=consecutive, receiver=receptor, date=date,
                            payment_method=payment_method, sale_condition=sale_condition, currency=moneda,
                            activity_code=activity_code).encode('utf-8')
        )
    return
