from functools import wraps
from flask import abort
from flask_login import current_user

def permission_required(permission):
	def decorator(f):
		@wraps(f)
		def decorator_function(*args, **kwargs):
			if not current_user.hak(permission):
				abort(403)
			return f(*args, **kwargs)
		return decorator_function
	return decorator
	