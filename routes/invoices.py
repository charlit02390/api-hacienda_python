# -*- coding: utf-8 -*-
from flask import Blueprint, request
import json
from service import invoices as service


app = Blueprint('invoices', __name__)


@app.route("", methods=['GET'])
def route_list_invoice():

    return 'Hello Invoices!'


@app.route("", methods=['POST'])
def route_create_invoice():
    body = request.form
    result = service.create_invoice(body)
    return result
