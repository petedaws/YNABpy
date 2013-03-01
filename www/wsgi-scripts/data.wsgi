#!/usr/bin/python
import json
from YNABpy import Parser

def application(environ, start_response):
	YNAB_DATA_FILE = "test.ynab3"
	yparser = Parser.YNAB3_Parser(YNAB_DATA_FILE)
	payees = yparser.get_payee_lister()
	categories = yparser.get_category_lister()
	resp = json.dumps({'payees':payees.get_content(),
					   'categories':categories.get_content()})
	status = '200 OK'
	headers = [\
		('Content-type', 'application/json'),
		('Content-length', str(len(resp)))]
	start_response(status, headers)
	return [resp]