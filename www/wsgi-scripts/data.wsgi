#!/usr/bin/python
import json
import sys
import os
sys.path.append('/opt/YNABpy')
from YNABpy import Parser

def application(environ, start_response):
	YNAB_DATA_FILE = "/opt/YNABpy/test.ynab3"
	yparser = Parser.YNAB3_Parser(YNAB_DATA_FILE)
	payees = yparser.get_payee_lister()
	categories = yparser.get_category_lister()
	resp = json.dumps({'payees':[payee.get_name() for payee in payees.get_content()],
					   'categories':[category.get_name() for category in categories.get_content()]})
	status = '200 OK'
	headers = [\
		('Content-type', 'application/json'),
		('Content-length', str(len(resp)))]
	start_response(status, headers)
	return [resp]
