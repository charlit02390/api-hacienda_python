import json
from extensions import mysql


def save_user(id_user, password, name, idrol):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_createUser', (id_user, password, name, idrol))
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


def save_user_company(id_user,idcompany):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_createUser_Company', (id_user,idcompany))
        data = cursor.fetchall()
        if len(data) is 0:
            conn.commit()
            return {'message': 'user and data created successfully '}
        else:
            return {'error': str(data[0])}
    except Exception as e:
        return {'error': str(e)}
    finally:
        cursor.close()
        conn.close()


def get_user_data(id_user):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_getUserInfo', (id_user,))
        row_headers = [x[0] for x in cursor.description]
        data = cursor.fetchall()

        if len(data) is not 0:
            conn.commit()
            json_data = []
            for row in data:
                json_data.append(dict(zip(row_headers, row)))
            companies = {'companies': get_user_company_data(id_user)}
            json_data[0].update(companies)
            return json_data
        else:
            return {'error': 'Error: Not get information of the user'}
    except Exception as e:
        return {'error': str(e)}
    finally:
        cursor.close()
        conn.close()


def get_user_company_data(id_user):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_getUserInfoCompanies', (id_user,))
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


def get_users():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_getUsers', ())
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


def modify_user(id_user, password, name, idrol):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_ModifyUser', (id_user, password, name, idrol))
        data = cursor.rowcount
        if data != 0:
            conn.commit()
            return {'message': 'User data modify'}
        else:
            return {'error': 'The user can not be modify'}
    except Exception as e:
        return {'error': str(e)}
    finally:
        cursor.close()
        conn.close()


def verify_email(id_user):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_getUserInfo', (id_user,))
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


def verify_user_company(id_user,idcompany):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_getUserCompany_info', (id_user,idcompany,))
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


def delete_user_data(id_user):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_deleteUser', (id_user,))
        data = cursor.rowcount
        if data != 0:
            conn.commit()
            return {'message': 'The user has been deleted'}
        else:
            return {'error': 'The user can not be deleted'}
    except Exception as e:
        return {'error': str(e)}
    finally:
        cursor.close()
        conn.close()


def delete_user_company(id_user,idcompany):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_deleteUserCompany', (id_user, idcompany,))
        data = cursor.rowcount
        if data != 0:
            conn.commit()
            return True
        else:
            return {'error': 'The user company can not be deleted'}
    except Exception as e:
        return {'error': str(e)}
    finally:
        cursor.close()
        conn.close()


def check_user(email, password):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_CheckUser', (email, password,))
        row_headers = [x[0] for x in cursor.description]
        data = cursor.fetchall()
        if len(data) is not 0:
            conn.commit()
            json_data = []
            for row in data:
                json_data.append(dict(zip(row_headers, row)))
            return json_data
    except Exception as e:
        return {'error': str(e)}
    finally:
        cursor.close()
        conn.close()

