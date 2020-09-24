from infrastructure import dbadapter as dbadp
from helpers.errors.enums import DBErrorCodes
from helpers.errors.exceptions import DatabaseError


def search_meds(pattern):
    procname = 'usp_buscar_medicamento'
    headers = ['codigocabys','principioms','codigoatc','principioatc','descripcion']
    try:
        return dbadp.fetchall_from_proc(procname, (pattern,), headers)
    except dbadp.DbAdapterError as dbae:
        raise DatabaseError(status=DBErrorCodes.DB_CABYS_SEARCH_MEDICATION) from dbae



def search_cabys(pattern):
    procname = 'usp_buscar_cabys'
    headers = ['codigo','descripcion','impuesto']
    try:
        return dbadp.fetchall_from_proc(procname, (pattern,), headers)
    except dbadp.DbAdapterError as dbae:
        raise DatabaseError(status=DBErrorCodes.DB_CABYS_SEARCH_CODE) from dbae



def find_sacs(cabyscode):
    procname = 'usp_obtenersacs_cabysxsac'
    headers = ['codigocabys','codigosac','descripcabys']
    try:
        return dbadp.fetchall_from_proc(procname, (cabyscode,), headers)
    except dbadp.DbAdapterError as dbae:
        raise DatabaseError(status=DBErrorCodes.DB_CABYS_SEARCH_SACS) from dbae
