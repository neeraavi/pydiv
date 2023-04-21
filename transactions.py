import calendar
import csv
import datetime
from typing import List

import fileprocessor
import itertools


class Transactions:
    def __init__(self, start_year, prefix, current_date, out_path_prefix):
        # self.outPathPrefix = out_path_prefix
        # self.numOfYears = None
        # self.prefix = prefix
        # self.totalInvested = 0
        # self.transactions = []
        # self.transactionMap = {}
        # self.investmentCalendar = []
        # self.investmentCalendarMap = {}
        # self.startYear = start_year
        # self.now = current_date

        self.outPathPrefix: str = out_path_prefix
        self.numOfYears: int = 0
        self.prefix: str = prefix
        self.totalInvested: float = 0
        self.transactions: List[List] = []
        self.transactionMap: dict = {}
        self.investmentCalendar: List[List] = []
        self.investmentCalendarMap: dict = {}
        self.startYear: int = start_year
        self.currentMonth: int = 0
        self.currentYear: int = 0
        self.now: datetime = current_date

        self.init_investment_calendar()
        self.fill_transactions()

    def init_investment_calendar(self):
        for y, m in itertools.product(range(self.startYear, self.now.year + 1), range(1, 13)):
            ym = "{y}-{m:02d}".format(y=y, m=m)
            self.investmentCalendarMap[ym] = 0

        self.numOfYears = self.now.year - self.startYear + 1
        self.investmentCalendar = [[0] * self.numOfYears for _ in range(12)]

    def transactions_processor(self, line):
        if line.startswith("#"):
            return None
        (name, yy, mm, dd, operation, nos, cost) = line.replace(" ", "").split("-")
        operation_sign = 1 if "Buy" in operation else -1
        nos = int(nos)
        cost = float(cost)
        cost_per_share = "{:.2f}".format(cost / nos) if nos > 0 else "0.00"
        # cost_per_share = round(cost / nos, 2) if nos > 0 else 0.0
        ym = f"{yy}-{mm}"
        transaction_item = [name, operation, f"{ym}-{dd}", nos, cost, cost_per_share, operation_sign]
        self.transactionMap.setdefault(name, [])
        self.transactionMap[name].append(transaction_item)
        # if name not in self.transactionMap:
        #    self.transactionMap[name] = []
        # self.transactionMap[name].append(item)

    def create_summary_table_from_list(self):
        # [name, operation, ym + ' - ' + dd, nos, cost, cps, op_sign]'
        #  0      1          2              3      4    5    6
        for ticker, t_list in self.transactionMap.items():
            inv = sum(row[4] * row[6] for row in t_list)
            nos = sum(row[3] * row[6] for row in t_list)
            if nos > 0:
                self.totalInvested = self.totalInvested + inv
                for row in t_list:
                    y, m, _ = row[2].split("-")
                    # ym = "{y}-{m:02d}".format(y=y, m=int(m))
                    ym = f"{y}-{int(m):02d}"
                    cost = row[4]
                    op_sign = row[6]
                    self.investmentCalendarMap[ym] += op_sign * cost
            self.transactions.append([ticker, nos, round(inv)])
            # cps = "{:.2f}".format(inv / nos) if nos != 0 else " "
            cps = f"{inv / nos:.2f}" if nos != 0 else " "
            t_list.append(["Total", len(t_list), "", nos, inv, cps, "xx"])
        for item in self.transactions:
            ticker, nos, invested = item
            if nos == 0:
                status = "*"
                alloc = "0.00%"
            else:
                status = " "
                # alloc = "{:.2f}%".format(invested / self.totalInvested * 100)
                alloc = f"{invested / self.totalInvested * 100:.2f}%"
            item[5:5] = (alloc, "0.00", 0, "0.00%", "0.00", 0)
            #                    yoc_a  ann_a ann_a%  yoc_b,  ann_b
            item.insert(1, status)
        self.cleanup_transaction_calendar()
        self.process_names()

    def cleanup_transaction_calendar(self):
        #        for y, m in itertools.product(range(self.startYear, self.now.year + 1), range(1, 13)):
        #            ym = "{y}-{m:02d}".format(y=y, m=m)
        #            self.investmentCalendarMap[ym] = round(self.investmentCalendarMap[ym])

        years = range(self.startYear, self.now.year + 1)
        months = range(1, 13)

        def get_ym_string(year, month):
            return f"{year}-{month:02d}"

        def round_investment_calendar():
            for y, m in itertools.product(years, months):
                ym = get_ym_string(y, m)
                self.investmentCalendarMap[ym] = round(self.investmentCalendarMap[ym])

        round_investment_calendar()

        for m in months:
            inner_list = self.investmentCalendar[m - 1]
            for y in range(self.now.year, self.startYear - 1, -1):
                # ym = "{y}-{m:02d}".format(y=y, m=m)
                ym = get_ym_string(y, m)
                inner_list[self.startYear - y - 1] = self.investmentCalendarMap[ym]
        total_row = [sum(i) for i in zip(*self.investmentCalendar)]
        self.investmentCalendar.append(total_row)

        def add_sigma_row():
            # sigma_row = [0] * len(total_row)
            num_years = self.now.year - self.startYear + 1
            total = sum(total_row)
            # sigma_row[0] = total
            # sigma_row[2] = "ϕ"
            # sigma_row[3] = round(total / self.numOfYears)
            sigma_row = [total, 0, "ϕ", round(total / self.numOfYears)] + [0] * (num_years - 4)
            self.investmentCalendar.append(sigma_row)
            # print(total_row)

        add_sigma_row()
        fname = f'{self.outPathPrefix}/investment_details.log'
        with open(fname, "w") as f:
            for r in self.investmentCalendar[:12]:
                print(', '.join(str(e) for e in r), file=f)

    def process_names(self):
        #        f = f"{self.prefix}/names.txt"
        #        with open(f) as file:
        #            for line in file:
        #                line = line.rstrip()
        #                (ticker, name, sector) = line.split("-")
        #                ticker = ticker.lower().strip()
        #                name = name.strip().replace("_", " ")
        #                sector = sector.strip()
        #                for t in self.transactions:
        #                    if ticker == t[0]:
        #                        t.extend([name, sector])

        ticker_map = {}
        with open(f"{self.prefix}/names.txt", newline='') as file:
            reader = csv.reader(file, delimiter='-')
            for row in reader:
                ticker, name, sector = [s.strip() for s in row]
                ticker_map[ticker.lower()] = (name.replace('_', ' '), sector)

        for t in self.transactions:
            ticker = t[0]
            if ticker in ticker_map:
                name, sector = ticker_map[ticker]
                t.extend([name, sector])
            else:
                t.extend(['ERR', 'ERR'])

    def fill_transactions(self):
        f = f"{self.prefix}/akt.txt"
        return fileprocessor.process_file(
            f, self.transactions_processor, self.create_summary_table_from_list
        )

    def get_transaction_results(self):
        summary_header = [
            "Ticker",
            ".",
            "#",
            "Inv",
            "Alloc",
            "Yoc_B",
            "Ann_B",
            "Contrib%",
            "Yoc_A",
            "Ann_A",
            "Name",
            "Sector",
        ]
        # self.totalInvested = round(self.totalInvested)
        return self.transactions, self.transactionMap, self.totalInvested, summary_header

    def get_investment_calendar(self):
        investment_calendar_header = list(range(self.now.year, self.startYear - 1, -1))
        # month_names = list(calendar.month_name)[1:13]
        # month_names.append("Total")
        # month_names.append("Σ")
        ##month_names = [calendar.month_name[i] for i in range(1, 13)] + ["Total", "Σ"]
        month_names = list(calendar.month_name)[1:13] + ["Total", "Σ"]
        self.investmentCalendar = [[" " if x == 0 else x for x in l] for l in self.investmentCalendar]
        return self.investmentCalendar, investment_calendar_header, month_names
