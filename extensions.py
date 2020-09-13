from flaskext.mysql import MySQL
from pymysql.constants import CLIENT

mysql = MySQL(client_flag=CLIENT.FOUND_ROWS)
