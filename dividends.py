import calendar
import fileprocessor
import columnNames as consts


def freq_multiplier(f):
    if f == 'A': return 1
    if f == 'B': return 2
    if f == 'Q': return 4
    if f == 'M': return 12
    print('Unknown freq:', f)
    return 0


class Dividends:
    def __init__(self, start_year, prefix, transactions_list, total_investment, current_date):
        self.month_names = None
        self.dividend_calendar_header = None
        self.numOfYears = None
        self.total_annual_div_a = 0
        self.total_annual_div_b = 0
        self.prefix = prefix
        self.startYear = start_year
        self.transactions_list = transactions_list
        self.total_investment = total_investment
        self.tax_factor = (1 - .27)  # Bruttodividenden – 26,375 % = Nettodividenden)

        # self.dividends = []
        self.dividendsMap = {}
        self.dividendsCalendar = []
        self.dividendsCalendarMap = {}  #
        self.currentMonth = None
        self.currentYear = None
        self.now = current_date

        self.init_dividends_calendar()

    def init_dividends_calendar(self):
        self.dividend_calendar_header = [x for x in range(self.now.year, self.startYear - 1, -1)]
        self.month_names = list(calendar.month_name)[1:13]
        self.month_names.extend(['Total', 'Σ'])

        for y in range(self.startYear, self.now.year + 1):
            for m in range(1, 13):
                ym = '{y}-{m:02d}'.format(y=y, m=m)
                self.dividendsCalendarMap[ym] = 0
        self.numOfYears = (self.now.year - self.startYear + 1)
        self.dividendsCalendar = [[0] * self.numOfYears for i in range(12)]

    def dividends_processor(self, line):
        if line.startswith('#'):
            return
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
        item = [ticker, freq, ym, nos, dps, before, '~yoc_b~', after, '~yoc_a~', where]

        if ticker not in self.dividendsMap:
            self.dividendsMap[ticker] = []
        self.combine_with_same_ym_or_append(item)

    def combine_with_same_ym_or_append(self, new_entry):
        ticker = new_entry[consts.DIV_TICKER]
        ym = new_entry[consts.DIV_YM]
        div_before = new_entry[consts.DIV_BEFORE]
        self.dividendsCalendarMap[ym] += div_before

        for existing_row in self.dividendsMap[ticker]:
            if existing_row[consts.DIV_YM] == ym:
                existing_row[consts.DIV_NOS] += new_entry[consts.DIV_NOS]
                existing_row[consts.DIV_BEFORE] += div_before
                existing_row[consts.DIV_AFTER] += new_entry[consts.DIV_AFTER]
                existing_row[consts.DIV_WHERE] = '~c~'
                return
        self.dividendsMap[ticker].append(new_entry)

    def create_dividends_table_from_list(self):
        self.update_summary_table_with_dividend_info()
        self.update_dividend_table_with_div_increase_marker()
        self.update_summary_table_with_div_increase_marker()
        self.update_summary_table_with_div_contrib_from_each_ticker()
        self.update_dividends_calendar()

    def update_dividends_calendar(self):
        for y in range(self.startYear, self.now.year + 1):
            for m in range(1, 13):
                ym = '{y}-{m:02d}'.format(y=y, m=m)
                self.dividendsCalendarMap[ym] = round(self.dividendsCalendarMap[ym])

        for m in range(1, 13):
            inner_list = self.dividendsCalendar[m - 1]
            for y in range(self.now.year, self.startYear - 1, -1):
                ym = '{y}-{m:02d}'.format(y=y, m=m)
                inner_list[self.startYear - y - 1] = self.dividendsCalendarMap[ym]
        total_row = [sum(i) for i in zip(*self.dividendsCalendar)]
        self.dividendsCalendar.append(total_row)
        sigma_row = [0] * len(total_row)
        sigma_row[0] = sum(total_row)
        sigma_row[2] = 'ϕ'
        sigma_row[3] = round(sigma_row[0] / self.numOfYears)
        self.dividendsCalendar.append(sigma_row)
        print(total_row)

    def update_summary_table_with_dividend_info(self):
        # 0        1    2    3     4   5        6      7      8       9      10
        # [ticker, freq, ym, nos, dps, before, yoc_b, after, yoc_a, where,  div_increase]
        for ticker, d_rows in self.dividendsMap.items():
            before_total = sum(row[consts.DIV_BEFORE] for row in d_rows)
            after_total = sum(row[consts.DIV_AFTER] for row in d_rows)
            last_row = d_rows[-1]  # use last item to get div freq
            f = last_row[1]
            (last_div_nos, dps, last_div_before) = last_row[consts.DIV_NOS:consts.DIV_BEFORE + 1]
            d_rows.append(['Total', '', '', '', '', before_total, '', after_total, '', ''])

            num_of_div_payments_per_year = freq_multiplier(f)
            last_effective_dps = last_div_before / last_div_nos
            for t_item in self.transactions_list:
                if t_item[consts.SMRY_TICKER] == ticker:
                    nos = t_item[consts.SMRY_NOS]
                    invested = t_item[consts.SMRY_INVESTED]

                    next_before = last_effective_dps * nos
                    next_after = next_before * self.tax_factor
                    yoc_a = yoc_b = '0.00%'

                    if nos > 0:
                        factor = 100 * num_of_div_payments_per_year / invested
                        yoc_b = "{:.2f}%".format(next_before * factor)
                        yoc_a = "{:.2f}%".format(next_after * factor)
                        factor = nos * factor
                        for d in d_rows[:-1]:
                            cps = factor / d[consts.DIV_NOS]
                            d[consts.DIV_YOC_B] = "{:.2f}%".format(d[consts.DIV_BEFORE] * cps)
                            d[consts.DIV_YOC_A] = "{:.2f}%".format(d[consts.DIV_AFTER] * cps)

                    d_rows.insert(-1, ['Next', '', '', nos, dps, next_before, yoc_b, next_after, yoc_a, ''])
                    if nos > 0:
                        inv = t_item[consts.SMRY_INVESTED]
                        if inv != 0:
                            f = 100 / inv
                            next_annual_a = next_after * num_of_div_payments_per_year
                            yoc_a = next_annual_a * f
                            self.total_annual_div_a += next_annual_a
                            t_item[consts.SMRY_YOC_A] = "{:.2f}%".format(yoc_a)
                            t_item[consts.SMRY_ANN_DIV_A] = int(next_annual_a)

                            next_annual_b = next_before * num_of_div_payments_per_year
                            yoc_b = next_annual_b * f
                            self.total_annual_div_b += next_annual_b
                            t_item[consts.SMRY_YOC_B] = "{:.2f}%".format(yoc_b)
                            t_item[consts.SMRY_ANN_DIV_B] = int(next_annual_b)

    def update_dividend_table_with_div_increase_marker(self):
        for ticker, divs in self.dividendsMap.items():
            [row.append('') for row in divs]
            for index, row in enumerate(divs):
                if 0 < index < len(divs) - 2:
                    prev_div = divs[index - 1][consts.DIV_DPS]
                    current_div = row[consts.DIV_DPS]
                    if prev_div != current_div and prev_div != 0:
                        div_change = (current_div - prev_div) / prev_div * 100
                        sign = consts.SIGN_INCR if prev_div < current_div else consts.SIGN_DECR
                        row[consts.DIV_CHANGE] = '{:2.2f}% '.format(div_change) + sign

    def update_summary_table_with_div_increase_marker(self):
        for ticker, divs in self.dividendsMap.items():
            no_of_divs = len(divs) - 2
            if no_of_divs < 1:
                continue
            freq = divs[-3][consts.DIV_FREQ]
            cycle_length = freq_multiplier(freq)
            how_many_to_check = cycle_length if no_of_divs >= cycle_length else no_of_divs
            if no_of_divs < 2:
                how_many_to_check = 0
            result = consts.SIGN_SAME
            for x in range(how_many_to_check):
                index = -3 - x
                sign = divs[index][-1]
                if consts.SIGN_INCR in sign:
                    result = consts.SIGN_INCR
                    break
                if consts.SIGN_DECR in sign:
                    result = consts.SIGN_DECR
                    break
            if how_many_to_check < cycle_length:
                result = consts.SIGN_UNKNOWN
            for t_item in self.transactions_list:
                if t_item[consts.SMRY_TICKER] == ticker and t_item[consts.SMRY_STATUS] != '*':
                    t_item[consts.SMRY_STATUS] = result

    def update_summary_table_with_div_contrib_from_each_ticker(self):
        factor = 100 / self.total_annual_div_a
        for t_item in self.transactions_list:
            t_item[consts.SMRY_ANN_DIV_A_PC] = '{:2.2f}% '.format(t_item[consts.SMRY_ANN_DIV_A] * factor)

    def fill_dividends(self):
        f = self.prefix + '/div.txt'
        return fileprocessor.process_file(f, self.dividends_processor, self.create_dividends_table_from_list)

    def get_dividend_results(self):
        dividend_header = ['Ticker', 'F', 'YYYY-MM', '#', 'DPS', 'Div_B', 'YocB', 'Div_A', 'YocA', 'Where',
                           'DivInc']
        return self.dividendsMap, dividend_header, self.total_annual_div_a, self.total_annual_div_b

    def get_dividend_calendar_before_tax(self):
        self.dividendsCalendar = [[' ' if x == 0 else x for x in l] for l in self.dividendsCalendar]
        return self.dividendsCalendar, self.dividend_calendar_header, self.month_names
