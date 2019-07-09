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
            return json.dumps({'message': 'company created successfully!'})
        else:
            return json.dumps({'error': str(data[0])})
    except Exception as e:
        return json.dumps({'error': str(e)})
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
            return json.dumps({'message': 'information saved successfully!'})
        else:
            return json.dumps({'error': str(data[0])})
    except Exception as e:
        return json.dumps( {'error': str(e)})
    finally:
        cursor.close()
        conn.close()


def get_mh_data(company_user):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_getMHInfo', (company_user,))
        data = cursor.fetchall()
        if len(data) is not 0:
            conn.commit()
            return data
        else:
            return json.dumps({'error': 'Error: Not get information of your company'})
    except Exception as e:
        return json.dumps( {'error': str(e)})
    finally:
        cursor.close()
        conn.close()




def get_companies(id_company=0):
    return json.dumps({'error': str(id_company)})
