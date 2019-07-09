import json
from infrastructure import companies

def create_invoice(data):
    _company_user = data['id_compania']
    _receptor = data['receptor_nombre']
    _receptor_dni = data['receptor_cedula']
    _receptor_email = data['receptor_email']
    _lines = data['detalles']

