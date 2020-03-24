import json
from extensions import mysql


def save_company_smtp(host, user, password, port, encrypt_type, id_company):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_createSmtpData', (host, user, password,
                                              port, encrypt_type, id_company))
        data = cursor.fetchall()
        if len(data) is 0:
            conn.commit()
            return True
        else:
            return {'error': str(data[0])}
    except Exception as e:
        return {'error': str(e)}
    finally:
        cursor.close()
        conn.close()


def get_company_smtp(id_company):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_getCompanySmtpInfo', (id_company,))
        row_headers = [x[0] for x in cursor.description]
        data = cursor.fetchall()
        if len(data) is not 0:
            conn.commit()
            json_data = []
            for row in data:
                json_data.append(dict(zip(row_headers, row)))
            return json_data
        else:
            return {'error': 'Error: Not get information of the user'}
    except Exception as e:
        return {'error': str(e)}
    finally:
        cursor.close()
        conn.close()


def delete_company_smtp(id_company):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_deleteCompanySmtp', (id_company,))
        data = cursor.rowcount
        if data != 0:
            conn.commit()
            return {'message': 'The company smtp data has been deleted'}
        else:
            return {'error': 'The company smtp data can not be deleted'}
    except Exception as e:
        return {'error': str(e)}
    finally:
        cursor.close()
        conn.close()


def modify_company_smtp(host, password, user, port, encrypt_type, id_company):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_ModifyCompanySmtp', (host, password, user, port, encrypt_type, id_company))
        data = cursor.rowcount
        if data != 0:
            conn.commit()
            return {'message': 'Company smtp data modify'}
        else:
            return {'error': 'The Company smtp can not be modify'}
    except Exception as e:
        return {'error': str(e)}
    finally:
        cursor.close()
        conn.close()


def verify_company_smtp(company_user):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_getCompanySmtpInfo', (company_user,))
        data = cursor.fetchall()
        if len(data) is not 0:
            return True
        else:
            return False
    except Exception as e:
        return {'error': str(e)}
    finally:
        cursor.close()
        conn.close()
