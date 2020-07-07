"""Module that provides reusable functions for communicating with the database in a generic way. Hopefully...
"""
import json
from extensions import mysql
from enum import Enum
from pymysql import cursors

class FetchType(Enum):
    """
    Enum that specifies how cursors will fetch data from the the query given.

    For convenience, each enum has a dictionary value for the warning error used in functions.
    
    :FetchType.ONE: Fetches only the first row.
    :FetchType.ALL: Fetches all rows available.
    :FetchType.ALL_UNBUFFERED: Prompts the creation of a generator. Should only be used with buffered as False.
    """
    ONE = {'_warning' : 'No data found.'}
    ALL = {'_warning' : 'No matches found.'}
    ALL_UNBUFFERED = {'_warning' : 'No data found.'}


def fetchall_from_proc(procname: str, args: tuple=(), headers: list=None):
    """
    Fetches all rows from the given database procedure name and returns them in a list.

    Optionally, accepts as parameters an arguments tuple and a headers list.
    Delegates to _fetch_from_proc

    :param procname: str - The name of the stored procedure to call.
    :param args: [optional] tuple - A tuple that contains the data so be sent as the called procedure's parameters.
    :param headers: [optiona] list - A list that contains strings to be used as \"headers\" for the dictionaries produced for each row.
    :returns: list[dict]|dict - A list composed of dictionaries for each row fetched from the stored procedure called; or a dictionary that contains warning or error data.
    """
    return _fetch_from_proc(FetchType.ALL, True, procname, args, headers)


def fetchone_from_proc(procname: str, args: tuple=(), headers: list=None):
    """
    Fetches the first row from the given database procedure name and returns it in a dictionary.

    Optionally, accepts as parameters an arguments tuple and a headers list.
    Delegates to _fetch_from_proc

    :param procname: str - The name of the stored procedure to call.
    :param args: [optional] tuple - A tuple that contains the data so be sent as the called procedure's parameters.
    :param headers: [optiona] list - A list that contains strings to be used as \"headers\" for the dictionaries produced for each row.
    :returns: dict - A dictionary that contains the data fetched from the stored procedure called; or a dictionary that contains warning or error data.
    """
    return _fetch_from_proc(FetchType.ONE, False, procname, args, headers)
    

def _fetch_from_proc(fetchtype: FetchType, buffered: bool, procname: str, args: tuple=(), headers: list=None):
    """
    Fetches data from the database from the given database procedure name.

    This function behaves differently depending on the fetchtype and buffered parameters given. Needs some more testing...

    :param fetchtype: FetchType - How the cursor will fetch the data. Refer to the FetchType class for more information.
    :param buffered: bool - Determines the type of cursor to use: True for buffered cursor, which pulls all the data into memory and provides some utility functions not available in a unbuffered cursor; False for unbuffered, which consumes less memory, but has other limitations.
    :param procname: str - The name of the stored procedure to call.
    :param args: [optional] tuple - A tuple that contains the data so be sent as the called procedure's parameters.
    :param headers: [optiona] list - A list that contains strings to be used as \"headers\" for the dictionaries produced for each row.
    :returns: dict|dict[list]|gen - A dictionary if an error or warning happens, or if FetchType.ONE was used; a list composed of dictionaries if FetchType.ALL was used; or, a generator object if FetchType.ALL_UNBUFFERED was used and buffered was set to False.
    """
    data = {'_warning' : fetchtype.value['_warning']}
    conn = None
    try:
        conn = mysql.connect()
        cursortype = None
        if buffered:
            cursortype = cursors.Cursor
        else:
            cursortype = cursors.SSCursor

        with conn.cursor(cursortype) as cursor:
            cursor.callproc(procname, args)
            row_headers = headers or [x[0] for x in cursor.description]
            if fetchtype is FetchType.ALL:
                _resultSet = cursor.fetchall()
                if len(_resultSet) is not 0:
                    conn.commit()
                    _data = []
                    for row in _resultSet:
                        _data.append(dict(zip(row_headers,row)))

                    data = _data

            elif fetchtype is FetchType.ONE:
                _resultSet = cursor.fetchone()
                if _resultSet is not None:
                    data = dict(zip(row_headers,_resultSet))

            elif fetchtype is FetchType.ALL_UNBUFFERED and not buffered:
                data = cursor.fetchall_unbuffered()

            # gotta raise an exception for when no proper fetching was done... but... too lazy rn

    except Exception as e:
        data = {'_error' : str(e)}

    finally:
        if conn is not None:
            conn.close()


    return data
