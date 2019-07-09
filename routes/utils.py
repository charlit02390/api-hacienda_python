# -*- coding: utf-8 -*-
from flask import Blueprint, request
import json
from service import utils_mh as service


app = Blueprint('utils', __name__)


@app.route("/sign", methods=['POST'])
def sign_file():
    body = request.form
    result = service.sign_xml(body)
    return result


@app.route("/token", methods=['POST'])
def get_token():
    body = request.form
    result = service.get_token_hacienda(body)
    return result
