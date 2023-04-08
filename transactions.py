from datetime import datetime
import calendar
import fileprocessor


class Transactions:
    def __init__(self, start_year, prefix):
        self.prefix = prefix
        self.totalInvested = 0
        self.transactions = []
        self.transactionMap = {}
        self.investmentCalendar = []
        self.investmentCalendarMap = {}
        self.startYear = start_year
        self.currentMonth = None
        self.currentYear = None
        self.now = None
        self.init_investment_calendar()

    def init_investment_calendar(self):
        self.now = datetime.now()
        for y in range(self.startYear, self.now.year + 1):
            for m in range(1, 13):
                ym = '{y}-{m:02d}'.format(y=y, m=m)
                self.investmentCalendarMap[ym] = 0

        self.numOfYears = (self.now.year - self.startYear + 1)
        self.investmentCalendar = [[0] * self.numOfYears for i in range(12)]
        # for s in self.investmentCalendar:
        #    print(*s)
        # print(json.dumps(self.transactionsCalendarMap, indent=4))

    def transactions_processor(self, line):
        if line.startswith('#'):
            return None
        else:
            (name, yy, mm, dd, operation, nos, cost) = line.replace(' ', '').split('-')
            op_sign = 1 if "Buy" in operation else -1
            nos = int(nos)
            cost = float(cost)
            cps = "{:.2f}".format(cost / nos) if nos > 0 else '0.00'
            ym = yy + '-' + mm
            item = [name, operation, ym + '-' + dd, nos, cost, cps, op_sign]
            if name not in self.transactionMap:
                self.transactionMap[name] = []
            self.transactionMap[name].append(item)

    def create_transactions_table_from_list(self):
        # [name, operation, ym + ' - ' + dd, nos, cost, cps, op_sign]'
        #  0      1          2              3      4    5    6
        for ticker, t_list in self.transactionMap.items():
            inv = sum(row[4] * row[6] for row in t_list)
            nos = sum(row[3] * row[6] for row in t_list)
            if nos > 0:
                self.totalInvested = self.totalInvested + inv
                for row in t_list:
                    y, m, _ = row[2].split('-')
                    ym = '{y}-{m:02d}'.format(y=y, m=int(m))
                    cost = row[4]
                    op_sign = row[6]
                    self.investmentCalendarMap[ym] = self.investmentCalendarMap[ym] + op_sign * cost
            self.transactions.append([ticker, nos, round(inv)])
            cps = "{:.2f}".format(inv / nos) if nos != 0 else ' '
            t_list.append(['Total', len(t_list), '', nos, inv, cps, 'xx'])
        self.totalInvested = round(self.totalInvested)
        for item in self.transactions:
            ticker, nos, invested = item
            if nos == 0:
                status = '*'
                alloc = '0.00 %'
            else:
                status = ' '
                alloc = "{:.2f} %".format(invested / self.totalInvested * 100)
            item.insert(1, status)
            item.append(alloc)
        print(self.totalInvested)
        self.cleanup_transaction_calendar()
        self.process_names()

    def cleanup_transaction_calendar(self):
        for y in range(self.startYear, self.now.year + 1):
            for m in range(1, 13):
                ym = '{y}-{m:02d}'.format(y=y, m=m)
                self.investmentCalendarMap[ym] = round(self.investmentCalendarMap[ym])

        for m in range(1, 13):
            inner_list = self.investmentCalendar[m - 1]
            for y in range(self.now.year, self.startYear - 1, -1):
                ym = '{y}-{m:02d}'.format(y=y, m=m)
                inner_list[self.startYear - y - 1] = self.investmentCalendarMap[ym]
        total_row = [sum(i) for i in zip(*self.investmentCalendar)]
        self.investmentCalendar.append(total_row)
        sigma_row = [0 for x in total_row]
        sigma_row[0] = sum(total_row)
        sigma_row[2] = 'ϕ'
        sigma_row[3] = round(sigma_row[0] / self.numOfYears)
        print(sum(total_row))
        self.investmentCalendar.append(sigma_row)
        print(total_row)

    def process_names(self):
        f = self.prefix + '/names.txt'
        with open(f) as file:
            for line in file:
                line = line.rstrip()
                (ticker, name, sector) = line.split('-')
                ticker = ticker.lower().strip()
                name = name.strip().replace('_', ' ')
                sector = sector.strip()
                for t in self.transactions:
                    if ticker == t[0]:
                        t.extend([name, sector])

    def fill_transactions(self):
        f = self.prefix + '/akt.txt'
        return fileprocessor.process_file(f, self.transactions_processor, self.create_transactions_table_from_list)

    def get_transaction_results(self):
        summary_header = ['Ticker', '.', '#', 'Invested', 'Alloc', 'Name', 'Sector']
        return self.transactions, self.transactionMap, self.totalInvested, summary_header

    def get_investment_calendar(self):
        investment_calendar_header = [x for x in range(self.now.year, self.startYear - 1, -1)]
        # investment_calendar_header.insert(0, 'Month')
        month_names = list(calendar.month_name)[1:13]
        month_names.append('Total')
        # month_names.append('')
        month_names.append('Σ')
        # m = 0
        # for row in self.investmentCalendar:
        #    row.insert(0, month_names[m])
        #    m = m + 1
        self.investmentCalendar = [[' ' if x == 0 else x for x in l] for l in self.investmentCalendar]
        return self.investmentCalendar, investment_calendar_header, month_names
