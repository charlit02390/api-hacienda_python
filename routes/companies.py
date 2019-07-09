from flask import Blueprint, request
import json
from service import companies as service

app = Blueprint('companies', __name__)


@app.route("", methods=['GET'])
def route_list_companies():
    result = service.get_list_companies()
    return result


@app.route("/<id>", methods=['GET'])
def route_get_company_byid(id):
    result = service.get_list_companies(id)
    return result


@app.route("", methods=['POST'])
def route_create_company():
    body = json.loads(request.get_data())
    result = service.create_company(body)
    return result


@app.route("/info/hacienda", methods=['POST'])
def route_save_info_hacienda():
    body = request.form
    file = request.files['firma'].read()
    result = service.save_info_mh(body, file)
    return result


@app.route("", methods=['PUT'])
def route_update_company():
    return 1


@app.route("", methods=['DELETE'])
def route_delete_company():
    return 1

