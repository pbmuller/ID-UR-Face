import os


def proper_slash():
	return '\\' if os.name == 'nt' else '/'