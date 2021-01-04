import os
import tempfile

import pdfkit
from flask import render_template

from . import fe_enums
from . import utils

CREDIT_CURRENCY_EXCHANGE_POLICY = """\
Si la factura no se cancela dentro del mes de su facturación, \
se debe pagar al tipo de cambio oficial al dia de su cancelación."""

def render_pdf(company_data, logo, pdf_data):
    css = ['templates/bootstrap.min.css']
   
    options = {
        '--encoding': 'utf-8'
    }

    company_id_type_str = fe_enums.tipoCedulaPDF.get(
        company_data.get('type_identification'),
        'Tipo de identificación no especificada'
    )
    header_data = {'company' : company_data, 'logo' : logo, 
                   'type_iden_company' : company_id_type_str
    }
    header_data.update(pdf_data['header'])

    footer_data = {
        'email': company_data['email']
    }
    footer_data.update(pdf_data['footer'])

    add_pdf_header(options, header_data)
    add_pdf_footer(options, footer_data)

    body_data = {
        'company': company_data,
        'lines': pdf_data['lines'],
        **pdf_data['body']
    }

    main_content = render_template("invoice.html",
                                   **body_data)
    try:
        pdf = pdfkit.from_string(main_content, False,
                                 css=css,
                                 options=options)
    finally:
        os.remove(options['--header-html'])
        os.remove(options['--footer-html'])
    return pdf


def add_pdf_header(options, data):
    add_temp_section(options, '--header-html', 'header.html', data)


def add_pdf_footer(options, notes):
    add_temp_section(options, '--footer-html','footer.html', notes)


def add_temp_section(options, section_name, template_name, data):
    with tempfile.NamedTemporaryFile(suffix='.html',
                                     delete=False) as section:
        options[section_name] = section.name
        rendered = render_template(template_name,
                                   **data).encode('utf-8')
        section.write(rendered)
