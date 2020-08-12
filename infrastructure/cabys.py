from infrastructure import dbadapter as dbadp


def search_meds(pattern):
    procname = 'usp_buscar_medicamento'
    headers = ['codigocabys','principioms','codigoatc','principioatc','descripcion']
    return dbadp.fetchall_from_proc(procname, (pattern,), headers)


def search_cabys(pattern):
    procname = 'usp_buscar_cabys'
    headers = ['codigo','descripcion','impuesto']
    return dbadp.fetchall_from_proc(procname, (pattern,), headers)


def find_sacs(cabyscode):
    procname = 'usp_obtenersacs_cabysxsac'
    headers = ['codigocabys','codigosac','descripcabys']
    return dbadp.fetchall_from_proc(procname, (cabyscode,), headers)
