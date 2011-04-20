"""

Parser.py

INTRODUCTION

YNABpy - A Python module for the YNAB (You Need A Budget) application.

AUTHOR

Mark J. Nenadov (2011)
* Essex, Ontario
* Email: <marknenadov@gmail.com> 

LICENSING

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version

This program is distributed in the hope that it will be useful
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>. 

"""

import sys

from xml.dom import minidom

def xmlize(item):
    if sys.version_info[0] == 3:
        return item
    return unicode(item)


class YNAB3_AccountingWidget:
    """
    Base class for various YNAB3 things
    (ie. YNAB3_Payee, YNAB3_Transaction)

    """

    fields_of_interest = [xmlize('memo'), xmlize('inflow'), xmlize('outflow')]

    def __init__(self, transaction_dom, additional_fields_of_interest):
        """Constructor

        """

        self.dom = transaction_dom

        for field in additional_fields_of_interest:
            if field not in self.fields_of_interest:
                self.fields_of_interest.append(field)

        for child in transaction_dom.childNodes:
            self.load_properties(child)


    def get_property(self, name):
        """ get a property (return None if it doesn't exist)

        We do this because this class loads properties from the xml
        dynamically, so there's a chance some properties may be missing
        """
        if hasattr(self, name):
            return getattr(self, name)
        return None


    def get_inflow(self):
        """ get_inflow
        """
        return self.get_property('inflow')

    def get_outflow(self):
        """ get_outflow
        """
        return self.get_property('outflow')

    def get_balance(self):
        """ get_balance

        Get the balance for this transaction, accounting
        for both outflow and inflow
        """

        if self.get_outflow() != None and self.get_inflow() != None:
            return float(self.get_inflow()) - float(self.get_outflow()) 
        else:
            return None

    def get_memo(self):
        """ get_memo
        """

        return self.get_property('memo')


class YNAB3_Payee(YNAB3_AccountingWidget):
    """
    YNAB3Transaction class

    """

    name = ""

    def __init__(self, payee_dom):
        """Constructor

        """
        
        super(YNAB3_Payee, self).__init__(payee_dom, [xmlize('category')])


    def load_properties(self, child):
        """ __load_properties
        Private method to Load ynab payee properties from a node
        """
        if child.nodeType == child.ELEMENT_NODE:
            if child.hasChildNodes():
                if child.nodeName == "name":
                    for subchild in child.childNodes:
                        self.name = subchild.data
                elif child.nodeName == "autoFillData":
                    for subchild in child.childNodes:
                        if not hasattr(subchild, "data"):        
                            for subsubchild in subchild.childNodes:
                                if hasattr(subsubchild, "data"):
                                    setattr(self, subchild.tagName, subsubchild.data)

    def get_category(self):
        """ get_memo
        """

        return self.get_property('category')

    def get_name(self):
        """ get_name
        """

        return self.get_property('name')


class YNAB3_Transaction(YNAB3_AccountingWidget):
    """
    YNAB3Transaction class
    
    """

    fields_of_interest = [xmlize('payee'), xmlize('date'), xmlize('accepted'), \
                          xmlize('account'), xmlize('memo'), xmlize('inflow'), \
                          xmlize('outflow')]

    dom = None

    def __init__(self, transaction_dom):
        """Constructor

        """
        super(YNAB3_Transaction, self).__init__(transaction_dom, [xmlize('accepted'), \
              xmlize('date'), xmlize('account'), xmlize('payee')])

    def load_properties(self, child):
        """ __load_properties
        Private method to Load ynab transaction properties from a node
        """
        if child.nodeType == child.ELEMENT_NODE:
            if child.hasChildNodes():
                if child.tagName in self.fields_of_interest:
                    for subchild in child.childNodes:
                        if hasattr(subchild, "data"):
                                setattr(self, child.tagName, subchild.data)

    def get_payee(self):
        """ get_payee
        """
        return self.get_property('payee')

    def get_date(self):
        """ get_date
        """
        return self.get_property('date')

    def get_accepted(self):
        """ get_accepted
        """
        return self.get_property('accepted')

    def get_account(self):
        """ get_account
        """

        return self.get_property('account')


    def get_xml(self):
        """ return xml 
        """

        return self.dom.toxml()

class YNAB3_Lister:
    """
    YNAB3_Lister base class
    """

    contents = []

    def __init__(self):
        """Constructor
    
        """

        pass 
    
    def get_content(self):
        """ return array of listed objects
        """

        return self.contents

    def add(self, t):
        """ add an item
        """

        self.contents.append(t)

    def get_items_by_text_filter(self, field, filter_str):
        """ Get items that have a argument-supplied property value that 
        matches a substring
        """

        item_list = []

        for item in self.get_content():
            if item.get_property(field) != None:
                if (item.get_property(field).find(filter_str) != -1):
                    item_list.append(item)

        return item_list


class YNAB3_Payee_Lister(YNAB3_Lister):
    """
    YNAB3_Payee_Lister

    """

    def get_categories(self):
        """ Get a unique list of categories for this list of
        payees
        """

        category_list = []

        for payee in self.contents:
            if payee.get_category() != None:
                category_list.append(payee.get_category())

        # eliminate duplicates
        return list(set(category_list))

    def get_payees_by_memo(self, memo_substr):
        """ Get transactions that have a memo that matches
        a substring
        """

        return self.get_items_by_text_filter('memo', memo_substr)

    def get_payees_by_name(self, name_substr):
        """ Get transactions that have a name that matches
        a substring
        """

        return self.get_items_by_text_filter('name', name_substr)


    def get_payees_by_category(self, category_substr):
        """ Get transactions that have a category that matches
        a substring
        """

        return self.get_items_by_text_filter('category', category_substr)



class YNAB3_Transaction_Lister(YNAB3_Lister):
    """
    YNAB3_Transaction_List Class

    """

    def get_accounts(self):
        """ Get the list of accounts represented in this transaction
        lister without duplicates
        """

        account_list = []
        for transaction in self.contents:
            if transaction.get_account() != None:
                account_list.append(transaction.get_account())

        # eliminate duplicates
        return list(set(account_list))


    def get_payees(self):
        """ Get the list of payees represented in this transaction
        lister without duplicates
        """

        payee_list = []
        for transaction in self.contents:
            if transaction.get_payee() != None:
                payee_list.append(transaction.get_payee())

        # eliminate duplicates
        return list(set(payee_list))

    def __get_transactions_by_text_filter(self, field, filter_str):
        """ Get transactions that have a argument-supplied property that 
        matches a substring
        """

        transaction_list = []

        for transaction in self.get_content():
            if transaction.get_property(field) != None:
                if (transaction.get_property(field).find(filter_str) != -1):
                    transaction_list.append(transaction)

        return transaction_list


    def get_transactions_by_payee(self, payee_substr):
        """ Get transactions that have a payee that matches
        a substring
        """

        return self.get_items_by_text_filter('payee', payee_substr)


    def get_transactions_by_memo(self, memo_substr):
        """ Get transactions that have a memo that matches
        a substring
        """

        return self.get_items_by_text_filter('memo', memo_substr)

    def get_transactions_by_outflow_filter(self, outflow_filter):
        """
        get transactions that have an outflow that falls inside
        of a tuple in the format of (low number, high number)
        """

        transaction_list = []

        for transaction in self.get_content():
            if transaction.get_outflow() != None:
                if (float(transaction.get_outflow()) >= outflow_filter[0] and \
                        float(transaction.get_outflow()) <= outflow_filter[1]):
                    transaction_list.append(transaction)

        return transaction_list

    def get_transactions_by_inflow_filter(self, inflow_filter):
        """
        get transactions that have an inflow that falls inside
        of a tuple in the format of (low number, high number)
        """

        transaction_list = []

        for transaction in self.get_content():
            if transaction.get_inflow() != None:
                if (float(transaction.get_inflow()) >= inflow_filter[0] and \
                        float(transaction.get_inflow()) <= inflow_filter[1]):
                    transaction_list.append(transaction)

        return transaction_list



    def get_total_inflow(self):
        """ Get total inflow represented in this transaction lister
        """
        inflow = 0

        for transaction in self.get_content():
            inflow += float(transaction.get_inflow())

        return inflow

    def get_total_outflow(self):
        """ Get total outflow represented in this transaction lister
        """
        outflow = 0

        for transaction in self.get_content():
            outflow += float(transaction.get_outflow())

        return outflow

    def get_pct_accepted(self):
        """ Get percentage of transactions accepted in this transaction
        lister

        Note: Technically speaking, accepted + not_accepted may not
        add up to the total amount of transactions (if a transaction
        dom node doesn't have the 'accepted' field)
        """
        accepted = 0
        not_accepted = 0
        for transaction in self.get_content():
            if (transaction.get_accepted() == "true"):
                accepted += 1
            elif (transaction.get_accepted() == "false"):
                not_accepted += 1

        return round(accepted / (accepted + not_accepted), 2) * 100


class YNAB3_Parser:
    minidom = None

    """
    YNAB3Parser Class

    """

    def __init__(self, file_path):
        """Constructor

        """

        self.minidom = minidom.parse(file_path)

    def get_payee_lister(self):
        """ get_payee_lister
        """

        payee_lister = YNAB3_Payee_Lister()
        for payee_node in self.minidom.getElementsByTagName('payees'):
            for p in payee_node.getElementsByTagName('data.vos.PayeeVO'):
                payee_lister.add( YNAB3_Payee(p) )
        return payee_lister


    def get_transaction_lister(self):
        """ get_transaction_lister
        """

        transaction_lister = YNAB3_Transaction_Lister()
        for transactions_node in self.minidom.getElementsByTagName('transactions'):
            for transaction in transactions_node.getElementsByTagName('data.vos.TransactionVO'):
                transaction_lister.add( YNAB3_Transaction(transaction) )
        return transaction_lister

if __name__ == "__main__":

    print("This is a module meant for being imported. Please refer to examples in the project folder!")

   
    YNAB_DATA_FILE = "F:/Development/PortableGit/YNABpy/YNABpy/test_budget.ynab3"
    yparser = YNAB3_Parser(YNAB_DATA_FILE)

    payee_lister = yparser.get_payee_lister()
    for x in payee_lister.get_payees_by_name("Mark"):
       print( x.get_name() )
