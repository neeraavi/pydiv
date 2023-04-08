import fileprocessor


class Dividends:
    def __init__(self, start_year, prefix, transactions_list):
        self.prefix = prefix
        self.startYear = start_year
        self.transactions_list = transactions_list
        self.tax_factor = (1 - .27)  # Bruttodividenden – 26,375 % = Nettodividenden)

        # self.totalInvested = 0

        self.dividends = []
        self.dividendsMap = {}
        self.dividendsCalendar = []
        self.dividendsCalendarMap = {}

        self.currentMonth = None
        self.currentYear = None
        self.now = None
        self.init_dividends_calendar()

    def fill_dividends(self):
        f = self.prefix + '/div.txt'
        return fileprocessor.process_file(f, self.dividends_processor, self.create_dividends_table_from_list)

    def init_dividends_calendar(self):
        pass

    def dividends_processor(self, line):
        if line.startswith('#'):
            return None
        pieces = line.replace(' ', '').split('-', maxsplit=8)
        pieces += [''] * (9 - len(pieces))
        (ticker, freq, mm, yy, nos, dps, before, after, where) = pieces
        # 0        1   2    3     4   5     6      7      8
        # size can be 7(no after, where), 8 (no where) or 9
        nos = int(nos)
        before = float(before)
        dps = before / nos if dps == '' else float(dps)
        after = before * self.tax_factor if after == '' else float(after)
        ym = yy + '-' + mm
        item = [ticker, freq, ym, nos, dps, before, after, where]
        print(item)

        if ticker not in self.dividendsMap:
            self.dividendsMap[ticker] = []
        self.combine_with_same_ym_or_append(item)

    def combine_with_same_ym_or_append(self, item):
        # 0        1    2    3     4   5        6      7
        # [ticker, freq, ym, nos, dps, before, after, where]
        ticker = item[0]
        for t_list in self.dividendsMap[ticker]:
            if t_list[2] == item[2]:
                t_list[3] += item[3]
                t_list[5] += item[5]
                t_list[6] += item[6]
                t_list[7] = '~c~'
                return
        self.dividendsMap[ticker].append(item)

    def create_dividends_table_from_list(self):
        #    0      1    2    3    4    5        6      7
        # [ticker, freq, ym, nos, dps, before, after, where]
        for ticker, t_list in self.dividendsMap.items():
            before_total = sum(row[5] for row in t_list)
            after_total = sum(row[6] for row in t_list)
            dps = t_list[-1][4]
            t_list.append(['Total', '~1', '~2', '~3', '~4', before_total, after_total, '~7'])
            for t_item in self.transactions_list:
                if t_item[0] == ticker:
                    nos = t_item[2]
                    before_next = dps * nos
                    after_next = before_next * self.tax_factor
                    t_list.append(['Next', '~1', '~2', nos, dps, before_next, after_next, '~7'])

    def get_dividend_results(self):
        dividend_header = ['Ticker', 'F', 'YYYY-MM', '#', 'DPS', 'Before', 'After', 'Where']
        return self.dividendsMap, dividend_header
