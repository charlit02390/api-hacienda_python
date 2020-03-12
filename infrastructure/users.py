import json
from extensions import mysql


# todo: guardar las compañias
def save_user(email, password, name, idrol, idcompanies):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_createUser', (email, password, name, idrol))
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


# TODO: armar JSON
def get_user_data(user_email):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_getUserInfo', (user_email,))
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


# TODO: Modificar codigo
def get_user():
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

#todo: modificar sp problema?
def modify_user(email, password, name, idrol, idcompanies):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_ModifyUser', (email, password, name, idrol))
        data = cursor.rowcount
        if data != 0:
            conn.commit()
            return {'message': 'The user has been modify'}
        else:
            return {'error': 'The user can not be modify'}
    except Exception as e:
        return {'error': str(e)}
    finally:
        cursor.close()
        conn.close()


def delete_user_data(user_id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_deleteUser', (user_id,))
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
