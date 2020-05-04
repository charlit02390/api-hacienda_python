import json
import base64
from extensions import mysql


def create_company(company_user, name, tradename, type_identification, dni, state, county, district, neighbor, address,
                   phone_code, phone, email, activity_code, is_active):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_createCompany', (company_user, name, tradename, type_identification, dni, state, county,
                                             district, neighbor, address, phone_code, phone, email, activity_code
                                             , is_active))
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


def save_mh_data(company_user, user_mh, pass_mh, signature, logo, pin_sig, env, expiration_date):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_saveMHInfo', (user_mh, pass_mh, signature, logo,
                                          pin_sig, company_user, env, expiration_date))
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


def modify_company(company_user, name, tradename, type_identification, dni, state, county, district, neighbor, address,
                   phone_code, phone, email, activity_code, is_active):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_ModifyCompany', (company_user, name, tradename, type_identification, dni, state, county,
                                             district, neighbor, address, phone_code, phone, email, activity_code
                                             , is_active))
        data = cursor.rowcount
        if data != 0:
            conn.commit()
            return True
        else:
            return {'error': 'The company data can not be modify'}
    except Exception as e:
        return {'error': str(e)}
    finally:
        cursor.close()
        conn.close()


def modify_mh_data(company_user, user_mh, pass_mh, signature, logo, pin_sig, env,expiration_date):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_modifyMHInfo', (user_mh, pass_mh, signature, logo,
                                            pin_sig, company_user, env, expiration_date))
        data = cursor.rowcount
        if data != 0:
            conn.commit()
            return True
        else:
            return {'error': 'The company data can not be modify'}
    except Exception as e:
        return {'error': str(e)}
    finally:
        cursor.close()
        conn.close()


def verify_company(company_user):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_getCompanyInfo', (company_user,))
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


def get_company_data(company_user):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_getCompanyInfo', (company_user,))
        row_headers = [x[0] for x in cursor.description]
        data = cursor.fetchall()

        if len(data) is not 0:
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
        if len(data) is not 0:
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


def get_logo_data(company_user):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_getLogoCompany', (company_user,))
        row_headers = [x[0] for x in cursor.description]
        data = cursor.fetchall()
        if len(data) is not 0:
            conn.commit()
            for row in data:
                logo = dict(zip(row_headers, row))
            return logo
        else:
            return {'error': 'Error: Not get information of your company'}
    except Exception as e:
        return {'error': str(e)}
    finally:
        cursor.close()
        conn.close()

def delete_company_data(company_user):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_deleteCompany', (company_user,))
        data = cursor.rowcount
        if data != 0:
            conn.commit()
            return {'message': 'The company has been deleted'}
        else:
            return {'error': 'The company can not be deleted'}
    except Exception as e:
        return {'error': str(e)}
    finally:
        cursor.close()
        conn.close()
