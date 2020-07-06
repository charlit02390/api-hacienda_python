
import json
from extensions import mysql


def search_meds(pattern):
    procname = 'usp_buscar_medicamento'
    headers = ['codigocabys','principioms','codigoatc','principioatc','descripcion']
    return fetchall_from_proc(procname, (pattern,), headers)


def search_cabys(pattern):
    procname = 'usp_buscar_cabys'
    headers = ['codigo','descripcion','impuesto']
    return fetchall_from_proc(procname, (pattern,), headers)


def find_sacs(cabyscode):
    procname = 'usp_obtenersacs_cabysxsac'
    headers = ['codigocabys','codigosac','descripcabys']
    return fetchall_from_proc(procname, (cabyscode,), headers)


def fetchall_from_proc(procname, args = (), headers = None):
     data = {'_warning' : 'No matches found.'}
     conn = None
     try:
         conn = mysql.connect()
         with conn.cursor() as cursor:
            cursor.callproc(procname, args)
            row_headers = headers or [x[0] for x in cursor.description]
            _resultSet = cursor.fetchall()
            if len(_resultSet) is not 0:
                conn.commit()
                json_data = []
                for row in _resultSet:
                    json_data.append(dict(zip(row_headers,row)))
                
                data = json_data
     except Exception as e:
        data = {'_error' : str(e)}
    
     finally:
        if conn is not None:
            conn.close()


     return data
