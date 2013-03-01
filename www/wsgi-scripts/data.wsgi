#!/usr/bin/python
import json
import sys
import os
sys.path.append('/opt/YNABpy')
from YNABpy import Parser
from YNABpy.Category import YNAB3_SubCategory

def get_sub_categories(categories):
	sub_categories = []
	for category in categories:
		sub_categories.extend(category.get_children())
	return sub_categories

def application(environ, start_response):
	YNAB_DATA_FILE = "/opt/YNABpy/test.ynab3"
	yparser = Parser.YNAB3_Parser(YNAB_DATA_FILE)
	payees = yparser.get_payee_lister()
	categories = yparser.get_category_lister()
	sub_categories = get_sub_categories(categories)
	resp = json.dumps({'payees':list(set([payee.get_name() for payee in payees.get_content()])),
					   'categories':sub_categories})
	status = '200 OK'
	headers = [\
		('Content-type', 'application/json'),
		('Content-length', str(len(resp)))]
	start_response(status, headers)
	return [resp]
