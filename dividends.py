import fileprocessor


class Dividends:
    def __init__(self, start_year, prefix, transactions_list, total_investment):
        self.prefix = prefix
        self.startYear = start_year
        self.transactions_list = transactions_list
        self.total_investment = total_investment
        self.tax_factor = (1 - .27)  # Bruttodividenden – 26,375 % = Nettodividenden)

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
        # print(item)

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
        self.update_summary_table_with_dividend_info()
        self.update_dividend_table_with_div_increase_marker()
        self.update_summary_table_with_div_increase_marker()

    def update_summary_table_with_dividend_info(self):
        #    0      1    2    3    4    5        6      7        8
        # [ticker, freq, ym, nos, dps, before, after, where, div_increase]
        self.total_annual_div_a = 0
        for ticker, t_list in self.dividendsMap.items():
            before_total = sum(row[5] for row in t_list)
            after_total = sum(row[6] for row in t_list)
            dps = t_list[-1][4]
            f = t_list[0][1]
            last_div_before = t_list[-1][5]
            last_div_nos = t_list[-1][3]
            t_list.append(['Total', '', '', '', '', before_total, after_total, ''])
            last_effective_dps = last_div_before / last_div_nos
            for t_item in self.transactions_list:
                # ['Ticker', '.', '#', 'Invested', 'Alloc', 'Yoc_A', 'Annual_A', 'Yoc_B', 'Name', 'Sector', '↕', 'b2']
                #     0       1    2       3          4        5        6          7         8       9       10
                if t_item[0] == ticker:
                    nos = t_item[2]
                    next_before = last_effective_dps * nos
                    next_after = next_before * self.tax_factor
                    t_list.append(['Next', '~1', '~2', nos, dps, next_before, next_after, '~7'])
                    if nos > 0:
                        inv = t_item[3]
                        if inv != 0:
                            yoc_b = next_before / inv * 100 * self.freq_multiplier(f)
                            next_annual_a = next_after * self.freq_multiplier(f)
                            self.total_annual_div_a += next_annual_a
                            print(f'{ticker} ,{next_annual_a}')
                            yoc_a = next_annual_a / inv * 100
                            t_item[5] = "{:.2f} %".format(yoc_a)
                            # t_item[6] = "{:.0f}".format(next_annual_a)
                            t_item[6] = int(next_annual_a)
                            t_item[8] = "{:.2f} %".format(yoc_b)
                        # t_item.insert(6, yoc_a)

        print(
            f'total_annual_div_a:{self.total_annual_div_a} {self.total_annual_div_a + 2000} {(self.total_annual_div_a + 2000) / 12}')

    def update_dividend_table_with_div_increase_marker(self):
        for ticker, t_list in self.dividendsMap.items():
            [row.append('') for row in t_list]
            for index, row in enumerate(t_list):
                if index > 0 and index < len(t_list) - 2:
                    prev_div = t_list[index - 1][4]
                    current_div = row[4]
                    if prev_div != current_div:
                        if prev_div != 0:
                            div_change = (current_div - prev_div) / prev_div * 100
                            # print(row[0], current_div, prev_div, div_change)
                            sign = '='
                            if prev_div > current_div:
                                sign = '↓'
                            else:
                                sign = '↑'
                            row[8] = '{:2.2f}% '.format(div_change) + sign

    def update_summary_table_with_div_increase_marker(self):
        for ticker, t_list in self.dividendsMap.items():
            no_of_divs = len(t_list) - 2
            if no_of_divs < 2:
                continue
            freq = t_list[-3][1]
            cycle_length = self.freq_multiplier(freq)
            how_many_to_check = cycle_length if no_of_divs >= cycle_length else no_of_divs
            result = '='
            for x in range(how_many_to_check):
                index = -3 - x
                if '↑' in t_list[index][-1]:
                    result = '↑'
                    break
                if '↓' in t_list[index][-1]:
                    result = '↓'
                    break
            for t_item in self.transactions_list:
                # ['Ticker', '.', '#', 'Invested', 'Alloc', 'Yoc_A', 'Annual_A', 'Yoc_B', 'Name', 'Sector', '↕', 'b2']
                #     0       1    2       3          4        5        6          7         8       9       10
                if t_item[0] == ticker:
                    t_item[11] = result
            # print(
            #    f'{ticker} f={freq} len(divs): {len(t_list)} check last {how_many_to_check}   result:{result}')

    def freq_multiplier(self, f):
        if f == 'A': return 1
        if f == 'B': return 2
        if f == 'Q': return 4
        if f == 'M': return 12
        print('Unknown freq:', f)
        return 0

    def get_dividend_results(self):
        dividend_header = ['Ticker', 'F', 'YYYY-MM', '#', 'DPS', 'Before', 'After', 'Where', 'DivInc']
        return self.dividendsMap, dividend_header, self.total_annual_div_a
