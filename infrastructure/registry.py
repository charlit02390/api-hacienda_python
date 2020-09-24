"""Module for manipulating data for table registrocivil in the database
"""
from infrastructure import dbadapter as dbadp
from helpers.errors.enums import DBErrorCodes
from helpers.errors.exceptions import DatabaseError

def get_person(id: str):
	"""
	Gets the information of a person from the database using the given id.

	:param id: str - The unique identification number for the person to find.
	:returns: dict - A dictionary, either with obtained data, or warning/error info.
	"""
	procname = 'usp_obtenerpersona_registrocivil'
	try:
		return dbadp.fetchone_from_proc(procname, (id,))
	except dbadp.DbAdapterError as dbae:
		raise DatabaseError(status=DBErrorCodes.DB_REGISTRY_SELECT_ONE) from dbae
