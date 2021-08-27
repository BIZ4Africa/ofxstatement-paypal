import csv
import re
from datetime import datetime

from decimal import Decimal as D

from ofxstatement import statement
from ofxstatement.statement import generate_transaction_id, StatementLine
from ofxstatement.statement import generate_unique_transaction_id

from ofxstatement.parser import CsvStatementParser
from ofxstatement.plugin import Plugin


class PayPalPlugin(Plugin):
    """Paypal Plugin
    """

    def get_parser(self, filename):
        f = open(filename, 'r', encoding=self.settings.get("charset", "UTF-8"))
        parser = PayPalParser(f)
        return parser

class PayPalParser(CsvStatementParser):

    date_format = None
    mappings = {
        # 'check_no': 3,
        'date': 0,
        'refnum': 3,
        'memo': 2,
        'amount': 5,
        'id': 3
    }
    valid_header = [
        u"Date",
        u"Time",
        u"Time Zone",
        u"Name",
        u"Type",
        u"Status",
        u"Currency",
        u"Gross",
        u"Fee",
        u"Net",
        u"From Email Address",
        u"To Email Address",
        u"Transaction ID",
        u"Delivery address",
        u"Address Status",
        u"Item Title",
        u"Item ID",
        u"Shipping and Handling Amount",
        u"Insurance Amount",
        u"Sales Tax",
        u"Option 1 Name",
        u"Option 1 Value",
        u"Option 2 Name",
        u"Option 2 Value",
        u"Reference Txn ID",
        u"Invoice Number",
        u"Custom Number",
        u"Quantity",
        u"Receipt ID",
        u"Balance",
        u"Address Line 1",
        u"Address Line 2/District/Neighborhood",
        u"Town/City",
        u"State/Province/Region/County/Territory/Prefecture/Republic",
        u"Zip/Postal Code",
        u"Country",
        u"Contact Phone Number",
        u"Object",
        u"Remark",
        u"Country Code",
        u"Impact On Balance",
    ]

    unique_id_set = set()
    filetype = None

    def _setFileType(self):
        self.filetype = "csv"

    def parse(self):
        """Main entry point for parsers

        super() implementation will call to split_records and parse_record to
        process the file.
        """
        self._setFileType()
        stmt = super(PayPalParser, self).parse()
        total_amount = sum(sl.amount for sl in stmt.lines)
        stmt.end_balance = stmt.start_balance + total_amount
        # stmt.start_date= min(sl.date for sl in stmt.lines)
        statement.recalculate_balance(stmt)
        return stmt

    def split_records(self):
        """Return iterable object consisting of a line per transaction
        """
        
        reader = csv.reader(self.fin, delimiter=',')
        next(reader, None)
        return reader

    def fix_amount(self, value):
        dbt_re = r"(.*)(Dr)$"
        cdt_re = r"Cr$"
        dbt_subst = "-\\1"
        cdt_subst = ""
        result = re.sub(dbt_re, dbt_subst, value, 0)
        result = re.sub(cdt_re, cdt_subst, result, 0)

        #Consider "--" as a reversal entry
        reversal_re = r"^--"
        reversal_subst = ""
        return re.sub(reversal_re, reversal_subst, result, 0)


    def parse_record(self, line):
        """Parse given transaction line and return StatementLine object
        """


        if self.filetype == "csv":
            return self.parse_record_csv(line)
        else:
            return self.parse_record_pdf(line)


    def parse_record_pdf(self, line):

        return None


    def parse_record_csv(self, line):
        id_idx = self.valid_header.index("Transaction ID")
        date_idx = self.valid_header.index("Date")
        name_idx = self.valid_header.index("Name")
        from_idx = self.valid_header.index("Name")
        to_idx = self.valid_header.index("Name")
        amount_idx = self.valid_header.index("Gross")
        currency_idx = self.valid_header.index("Currency")
        trn_type_idx = self.valid_header.index("Impact On Balance")
        balance_idx = self.valid_header.index("Balance")

        if self.date_format is None:
            self.date_format = "%d/%m/%Y" if len(line[0].split("/")[2]) == 4 else "%Y/%m/%d"

        if not self.statement.start_date:
            self.statement.start_date = datetime.strptime(line[date_idx], self.date_format)
            self.statement.start_balance = D(line[balance_idx].replace(',','.'))

        if not len(line[name_idx]) and not len(line[from_idx]) and not len(line[to_idx]):
            #Temporary  trick to skip conversion transactions
            return None

        smt_line = StatementLine()
        smt_line.id = line[id_idx]
        smt_line.date = datetime.strptime(line[date_idx], self.date_format)
        smt_line.currency = line[currency_idx]
        smt_line.amount = D(line[amount_idx].replace(',','.'))
        if line[trn_type_idx][0:1].upper() == "C":
            smt_line.trntype = "CREDIT"
        elif line[trn_type_idx][0:1].upper() == "D":
            smt_line.trntype = "DEBIT"


        #Build memo line
        smt_line.memo = ""
        for column_name in [
            "Name",
            "Invoice Number",
            "Currency",
            "From Email Address",
            "To Email Address"
        ]:
            memo_idx = self.valid_header.index(column_name)
            if len(line[memo_idx]):
                if len(smt_line.memo):
                    smt_line.memo = smt_line.memo + " // "
                smt_line.memo = smt_line.memo + line[memo_idx]

        return smt_line




        #Valuable lines has 9 elements
        if len(line) <=9:
            if line[0] == "Opening Balance":
                res = line[1].split();
                self.statement.currency=res[0]
                self.statement.start_balance=D(res[1])
                return None
        elif len(line) < 8:
            return None


        if (self.statement.currency and  (len(line) < 4 or not (line[4] ==  self.statement.currency))):
            return None


        date = line[0]
        date_value = line[1]
        description = line[2]
        transaction_id = line[3]
        currency = line[4]
        amount = self.fix_amount(line[5])
        line[5] = amount
        if(date.find('-') != -1):
            self.date_format = "%d-%b-%y"
        else:
            self.date_format = "%d %b %Y"

        stmtline = super(PayPalParser, self).parse_record(line)
        stmtline.trntype = 'DEBIT' if stmtline.amount < 0 else 'CREDIT'
        stmtline.id = generate_unique_transaction_id(stmtline, self.unique_id_set)

        return stmtline
