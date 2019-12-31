import subprocess

from . import api_facturae
from . import fe_enums

from infrastructure import companies


def generate_key(data):
    document_type = fe_enums.TipoDocumentoApi[data['tipo']]
    company_data = companies.get_company_data(data['nombre_usuario'])
    return api_facturae.get_clave_hacienda(company_data[0], document_type, data['consecutivo'], data['sucursal'], data['terminal'],
                                           data['situacion'])



