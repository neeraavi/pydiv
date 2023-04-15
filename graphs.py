import json
import calendar
import csv
import numpy as np
import datetime as datetime
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator


class Grapher:
    def __init__(self):
        self.parse_config()

    def parse_config(self):
        with open("config.json", "r") as config:
            data = json.load(config)
        self.pathPrefix = data["path_prefix"]
        self.outPathPrefix = data["out_path_prefix"]
        self.mainFont = data["main_font"]
        self.mainFontSize = data["main_font_size"]

    def graph_sectors(self):
        fname = f'{self.outPathPrefix}/sector_details.log'
        with open(fname) as f:
            sector_data = list(list(rec) for rec in csv.reader(f, delimiter=','))
        # names = [i[0] for i in sector_data]
        # values = [float(i[1]) for i in sector_data]
        names, values = zip(*[(i[0], float(i[1])) for i in sector_data])
        # div_b = sum(blist)
        # div_a = sum(alist)
        # print(names, values)

        fig, ax = plt.subplots(1, 1, figsize=(10, 6), tight_layout=True)
        ax.bar(names, values)
        plt.xticks(rotation=15, ha='right')
        ax.set_ylabel('Alloc')
        ax.set_title('Sector')
        ax.grid(True, which='both', alpha=0.5)
        ax.set_axisbelow(True)
        fname = f'{self.outPathPrefix}/sector_details.png'
        fig.set_size_inches(11, 3.5)
        plt.savefig(fname, bbox_inches="tight", dpi=96)
        # plt.show()
        print('done [1]')

    def graph_divs(self):
        fname = f'{self.outPathPrefix}/dividend_details.log'
        divs = np.loadtxt(fname, delimiter=",", dtype=int)
        # print(divs)

        fname = f'{self.outPathPrefix}/investment_details.log'
        invs = np.loadtxt(fname, delimiter=",", dtype=int)

        start_year = 2015
        today = datetime.datetime.now()

        div = inv = 0
        c_div = []
        c_inv = []

        fig, (ax1, ax2) = plt.subplots(2, figsize=(10, 6), tight_layout=True)
        for y in range(start_year, today.year + 1):
            for m in range(12):
                div += divs[m][today.year - y]
                c_div.append(div)
                inv += invs[m][today.year - y]
                c_inv.append(inv)
        # print(c_div, '.................')
        # ypoints = np.array(c_div)
        data_length = len(c_div)
        ax3 = ax2.twinx()
        # ax3 = ax_bot
        x = np.arange(0, data_length, 1).tolist()
        ax2.plot(x, c_div, color='g', alpha=0.4)
        ax2.yaxis.tick_right()
        # ax2.yaxis.set_label_position("right")
        ax2.tick_params(axis='y', labelcolor='g')

        # ax3.yaxis.set_label_position("right")
        # ax3.yaxis.tick_left()
        ax3.yaxis.tick_left()
        ax3.tick_params(axis='y', labelcolor='b')
        ax3.plot(x, c_inv, color='b', alpha=0.2)
        ax2.set_ylim(bottom=0)
        ax2.set_xlim(left=0)
        extended = data_length + 12
        major_ticks = np.arange(0, extended, 12)
        minor_ticks = np.arange(0, extended, 1)
        ax2.set_xticks(major_ticks)
        ax2.set_xticks(minor_ticks, minor=True)
        ax2.grid(which='major', color='g', linestyle='-', linewidth=1, alpha=0.5)
        ax2.minorticks_on()
        ax2.xaxis.set_minor_locator(MultipleLocator(3 / 1))
        # ax2.xaxis.set_minor_formatter(lambda x, pos: 'JFMAMJJASOND'[int(round(x * 12)) % 12])
        ax2.xaxis.set_minor_formatter(lambda x, pos: 'DSJM'[int(round(x)) % 4])
        ax2.xaxis.set_major_formatter(lambda x, pos: round(x / 12 + start_year))
        ax2.tick_params(axis='x', which='minor', labelsize=5)
        ax2.grid(True, which='both', alpha=0.2)
        last = data_length - 1
        for i, v in enumerate(c_div):
            if i % 12 == 0 or i == last:
                ax2.text(i, v + 25, "%d" % v, ha="center", fontsize=6)

        # ------------------
        divs = divs.transpose()
        # print(divs)

        s = [sum(x) for x in divs]
        s.reverse()
        xax = [(y - start_year) * 12 for y in list(range(start_year, today.year + 1))]
        # print(xax, s)
        rects = ax2.bar(xax, s)
        ax2.bar_label(rects, fmt="%d", fontsize=6, rotation=0, label_type='edge', padding=5, color='red')

        years = [i for i in range(today.year, start_year - 1, -1)]
        months = [calendar.month_abbr[i + 1] for i in range(12)]
        # print(years, months)

        means = {}
        for idx, y in enumerate(years):
            means[y] = divs[idx]
        # print(means)

        x = np.arange(len(months))  # the label locations
        width = 0.1  # the width of the bars
        multiplier = 0

        # fig, ax = plt.subplots(figsize=(10, 6),tight_layout=True)
        for attribute, measurement in means.items():
            offset = width * multiplier
            rects = ax1.bar(x + offset, measurement, width, label=attribute)
            # ax.bar_label(rects, padding=3)
            ax1.bar_label(rects, fmt="%d", fontsize=6, rotation=90, label_type='center', padding=3, color='white')
            multiplier += 1

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax1.set_ylabel('Div_B')
        ax1.set_title('Div progress')
        ax1.set_xticks(x + width, months)
        ax1.legend(loc='upper left', ncols=3)
        ax1.set_ylim(0, 2500)

        fname = f'{self.outPathPrefix}/div_details.png'
        fig.set_size_inches(11, 8.5)
        plt.savefig(fname, bbox_inches="tight", dpi=96)
        # plt.show()
        print('done [2]')


def draw_graphs():
    g = Grapher()
    g.graph_sectors()
    g.graph_divs()


if __name__ == "__main__":
    draw_graphs()
