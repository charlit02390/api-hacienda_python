"""Module for manipulating data for table registrocivil in the database
"""
from infrastructure import dbadapter as dbadp
from helpers.errors.enums import DBErrorCodes
from helpers.errors.exceptions import DatabaseError

def get_person(person_id: str):
	"""
	Gets the information of a person from the database using the
	given id.

	:param person_id: str - The unique identification number for the
		person to find.
	:returns: dict|None - A dictionary with obtained data, or
		None if the person was not found.
	"""
	procname = 'usp_obtenerpersona_registrocivil'
	try:
		return dbadp.fetchone_from_proc(procname, (person_id,))
	except dbadp.DbAdapterError as dbae:
		raise DatabaseError(status=DBErrorCodes.DB_REGISTRY_SELECT_ONE) from dbae
