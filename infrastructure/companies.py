import json
from extensions import mysql


def create_company(company_user, name, tradename, type_identification, dni, state, county, district, neighbor, address,
                   phone_code, phone, email, activity_code):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_createCompany', (company_user, name, tradename, type_identification, dni, state, county,
                                             district, neighbor, address, phone_code, phone, email, activity_code))
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


def save_mh_data(company_user, user_mh, pass_mh, signature, pin_sig, env):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_saveMHInfo', (user_mh, pass_mh, signature, pin_sig, company_user, env))
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


def get_company_data(company_user):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_getCompanyInfo', (company_user,))
        row_headers = [x[0] for x in cursor.description]
        data = cursor.fetchall()
        if len( data ) is not 0:
            conn.commit()
            json_data = []
            for row in data:
                json_data.append(dict(zip(row_headers, row)))
            return json_data
        else:
            return {'error': 'Error: Not get information of your company'}
    except Exception as e:
        return {'error': str(e)}
    finally:
        cursor.close()
        conn.close()


def get_companies():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_getCompanies', ())
        row_headers = [x[0] for x in cursor.description]
        data = cursor.fetchall()
        if len( data ) is not 0:
            conn.commit()
            json_data = []
            for row in data:
                json_data.append(dict(zip(row_headers, row)))
            return json_data
        else:
            return {'error': 'Error: Not get information of your company'}
    except Exception as e:
        return {'error': str( e )}
    finally:
        cursor.close()
        conn.close()


def get_sign_data(company_user):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_getSignCompany', (company_user,))
        row_headers = [x[0] for x in cursor.description]
        data = cursor.fetchall()
        if len(data) is not 0:
            conn.commit()
            for row in data:
               signature = dict(zip(row_headers, row))
            return signature
        else:
            return {'error': 'Error: Not get information of your company'}
    except Exception as e:
        return {'error': str(e)}
    finally:
        cursor.close()
        conn.close()

