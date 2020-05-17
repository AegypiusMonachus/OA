from .. import db


def execute(statement, page=None, per_page=None):
	result = db.session.execute(statement)
	total = result.rowcount
	if page and per_page:
		while (page - 1) * per_page > total:
			page -= 1
		statement += ' LIMIT %d OFFSET %d' % (per_page, (page - 1) * per_page)
		result.close()
		result = db.session.execute(statement)
		import math
		pages = math.ceil(total / per_page)
	else:
		page = pages = 1
	return [result.fetchall(), page, pages, total]


def paginate(query, criterion=set(), page=None, per_page=None):
	pagination = query.filter(*criterion).paginate(page, per_page, error_out=False)
	while not pagination.items and pagination.has_prev:
		pagination = pagination.prev()
	return pagination

def paginate_one(query, page=None, per_page=None):
	pagination = query.paginate(page, per_page, error_out=False)
	while not pagination.items and pagination.has_prev:
		pagination = pagination.prev()
	return pagination