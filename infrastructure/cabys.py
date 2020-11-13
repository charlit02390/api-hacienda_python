"""
Module for manipulating data for the tables related to the CABYS:
cabys
cabysxsacs
medicamento
"""
from infrastructure import dbadapter as dbadp
from helpers.errors.enums import DBErrorCodes
from helpers.errors.exceptions import DatabaseError


def search_meds(pattern: str) -> list:
    """
    Searches 'medicamento' table for the specified "pattern" and
    returns the matched rows.

    :param pattern: str - a string with a pattern to match rows.
    :returns: list - a list with matched rows for "pattern".
    """
    procname = 'usp_buscar_medicamento'
    headers = ['codigocabys', 'principioms', 'codigoatc',
               'principioatc', 'descripcion']
    try:
        return dbadp.fetchall_from_proc(procname, (pattern,), headers)
    except dbadp.DbAdapterError as dbae:
        raise DatabaseError(
            status=DBErrorCodes.DB_CABYS_SEARCH_MEDICATION
            ) from dbae



def search_cabys(pattern: str) -> list:
    """
    Searches 'cabys' table for the specified "pattern" and returns
    the matching rows.

    :param pattern: str - a string with a pattern to match rows.
    :returns: list - a list with matched rows for "pattern".
    """
    procname = 'usp_buscar_cabys'
    headers = ['codigo','descripcion','impuesto']
    try:
        return dbadp.fetchall_from_proc(procname, (pattern,), headers)
    except dbadp.DbAdapterError as dbae:
        raise DatabaseError(
            status=DBErrorCodes.DB_CABYS_SEARCH_CODE) from dbae



def find_sacs(cabyscode: str) -> list:
    """
    Obtains the SACS information from the given "cabyscode" in
    cabysxsacs table.

    :param cabyscode: str - a string containing the code to fetch
        it's SACS information.
    :returns: list - a list with the SACS for the "cabyscode"
        specified.
    """
    procname = 'usp_obtenersacs_cabysxsac'
    headers = ['codigocabys','codigosac','descripcabys']
    try:
        return dbadp.fetchall_from_proc(procname, (cabyscode,),
                                        headers)
    except dbadp.DbAdapterError as dbae:
        raise DatabaseError(
            status=DBErrorCodes.DB_CABYS_SEARCH_SACS) from dbae


def select(code: str):
    procname = 'usp_selectByCode_cabys'
    headers = ['codigo','descripcion','impuesto']
    try:
        return dbadp.fetchone_from_proc(procname, (code,), headers)
    except dbadp.DbAdapterError as dbae:
        raise DatabaseError(
            status=DBErrorCodes.DB_CABYS_SELECT_CABYS_BY_CODE
        ) from dbae
