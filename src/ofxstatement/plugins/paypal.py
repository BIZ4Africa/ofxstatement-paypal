import csv
import re
from datetime import datetime

from decimal import Decimal as D

from ofxstatement import statement
from ofxstatement.statement import generate_transaction_id, StatementLine, Currency
from ofxstatement.statement import generate_unique_transaction_id

from ofxstatement.parser import CsvStatementParser
from ofxstatement.plugin import Plugin


class PayPalPlugin(Plugin):
    """Paypal Plugin
    """

    def get_parser(self, filename):
        f = open(filename, 'r', encoding=self.settings.get("charset", "UTF-8"))
        parser = PayPalParser(f)
        #TODO: Sort file per date + time
        return parser

class PayPalParser(CsvStatementParser):

    date_format = None
    valid_header = [
        u"Date",
        u"Time",
        u"Time Zone",
        u"Description",
        u"Currency",
        u"Gross",
        u"Fee",
        u"Net",
        u"Balance",
        u"Transaction ID",
        u"From Email Address",
        u"Name",
        u"Bank Name",
        u"Bank Account",
        u"Deliver And Handling Fees",
        u"Sales Tax",
        u"Invoice Number",
        u"Reference Txn ID",
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
        stmt.end_date= max(sl.date for sl in stmt.lines)
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
        from_idx = self.valid_header.index("From Email Address")
        amount_idx = self.valid_header.index("Gross")
        currency_idx = self.valid_header.index("Currency")
        balance_idx = self.valid_header.index("Balance")

        if self.date_format is None:
            self.date_format = "%m/%d/%Y" if len(line[0].split("/")[2]) == 4 else "%Y/%m/%d"

        if not self.statement.start_date:
            self.statement.start_date = datetime.strptime(line[date_idx], self.date_format)
            self.statement.start_balance = D(line[balance_idx].replace(',','.')) - D(line[amount_idx].replace(',','.'))

        # if not len(line[name_idx]) and not len(line[from_idx]) and not len(line[to_idx]):
        #     #Temporary  trick to skip conversion transactions
        #     return None

        smt_line = StatementLine()
        smt_line.id = line[id_idx]
        smt_line.date = datetime.strptime(line[date_idx], self.date_format)
        smt_line.currency = Currency(line[currency_idx])
        smt_line.amount = D(line[amount_idx].replace(',','.').replace(u'\xa0',''))
        smt_line.trntype = "DEBIT" if smt_line.amount < 0 else "CREDIT"

        #Build memo line
        smt_line.memo = ""
        for column_name in [
            "Name",
            "Invoice Number",
            "Gross",
            "Currency",
            "From Email Address",
        ]:
            memo_idx = self.valid_header.index(column_name)
            if len(line[memo_idx]):
                if len(smt_line.memo):
                    smt_line.memo = smt_line.memo + " // "
                smt_line.memo = smt_line.memo + line[memo_idx]

        return smt_line