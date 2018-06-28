import csv
import datetime
import numpy as np
from scipy.interpolate import interp1d
import sys

def extract_1d_list(nested_list, index):
    extracted_list = []
    for i in range(len(nested_list)):
        extracted_list.append(nested_list[i][index])
    return extracted_list

def interpolation_extract_list(original_list, index_xaxis, index_yaxis):
    xaxis = []
    yaxis = []
    for i in range(len(original_list)):
        xaxis.append(float(original_list[i][index_xaxis]))
        yaxis.append(float(original_list[i][index_yaxis]))
    f_interpolation = interp1d(xaxis, yaxis)
    return f_interpolation

def calc_days(tenor_name):
        if (tenor_name[-1] == 'Y'):
            tenor_days = float(tenor_name[0:-1]) * 365
        elif (tenor_name[-1] == 'M'):
            tenor_days = float(tenor_name[0:-1]) * 30
        elif (tenor_name[-1] == 'W'):
            tenor_days = float(tenor_name[0:-1]) * 7
        elif (tenor_name == ' O/N' or 'T/N'):
            tenor_days = 1
        return int(tenor_days)

def calc_month(tenor_name):
        if (tenor_name[-1] == 'Y'):
            tenor_month = float(tenor_name[0:-1]) * 12
        elif (tenor_name[-1] == 'M'):
            tenor_month = float(tenor_name[0:-1]) * 1
        elif (tenor_name[-1] == 'W'):
            tenor_month = float(tenor_name[0:-1])  / 4
        elif (tenor_name == ' O/N' or 'T/N'):
            tenor_month = 1/30
        return int(tenor_month)

def calc_trade_days(start_day, end_day):
    datetime_obj_start = datetime.datetime.strptime(start_day, '%Y/%m/%d')
    datetime_obj_end = datetime.datetime.strptime(end_day, '%Y/%m/%d')
    return (datetime_obj_end - datetime_obj_start).days

class discount_factor:
    def __init__(self, ir_list_name, ccy, base_date):
        ## コンストラクタの順番に注意．　先に_ir_listを定義し， _load_ir_listの中で_base_dateを定義した関数(今回は_add_cash_flow())
        ## を呼び出すと， _base_dateがまだ定義されていないのでエラーがでる．
        # base_date -> trade_date??
        # spot dateを２営業日後としている.
        self._column_base_date = 0
        self._column_tenor = 1
        self._column_market = 2
        self._column_ccy = 3
        self._column_rate = 4
        self._column_roll = 5
        self._column_convention = 6
        self._base_date = datetime.datetime.strptime(base_date, '%Y/%m/%d').strftime('%Y/%m/%d')
        self._spot_date = self._calc_end_date(self._base_date, '2.0D')
        self._ir_list = self._set_ir_list(ir_list_name, ccy)
        self._roll_month = float(self._ir_list[-1][self._column_roll ][0])
        self._str_roll_month = str(self._roll_month) + 'M'
        self._convention = int(self._ir_list[0][self._column_convention][-3:])
        self._str_convention = self._ir_list[0][self._column_convention]
        self._string_swap = self._ir_list[-1][self._column_market]
        self._string_mm = self._ir_list[0][self._column_market]
        self._ccy = self._ir_list[0][self._column_ccy]
        self._column_start_date = 7
        self._column_end_date = 8
#        self._ir_list_DF_mm = self._calc_DF_money_market()
        if (self._base_date != datetime.datetime.strptime(self._ir_list[0][self._column_base_date], '%Y/%m/%d').strftime('%Y/%m/%d')):
            print('Enter Correct Base_Date in "A" column of input file.')
            sys.exit()
        else:
            pass

    def _csv_read_ir_list(self, ir_list_name):
        with open(ir_list_name, 'r') as csvfile:
            reader_obj = csv.reader(csvfile)
            # rewritten header_obj by using next method(???)
            header_obj = next(reader_obj)
            ir_list = []
            for row in reader_obj:
                ir_list.append(row)
            return ir_list

    def _set_ir_list(self, ir_list_name, ccy):
        ir_list = self._select_ccy_ir_list(ir_list_name, ccy)
        # change int type to float type (ex. 1Y -> 1.0Y)
        temp_num = [[] for i in range(len(ir_list))] # comprehension expression for making null list.
        for i in range(len(ir_list)):
            if (ir_list[i][self._column_tenor ][0].isdigit()):
                num_tenor = ir_list[i][self._column_tenor ][0: len(ir_list[i][self._column_tenor ])-1]
                unit_tenor = ir_list[i][self._column_tenor ][-1]
                temp_num[i] = "{:.1f}".format(int(num_tenor))
                ir_list[i][self._column_tenor ] = temp_num[i] + unit_tenor
        ir_list_with_cf = self._add_cash_flow(ir_list)
        return ir_list_with_cf

    def _select_ccy_ir_list(self, ir_list_name, ccy):
        ir_list = self._csv_read_ir_list(ir_list_name)
        indices_selected_ccy = self._select_ccy(ir_list, ccy)
        first_index_selected_ccy = indices_selected_ccy[0]
        last_index_selected_ccy = indices_selected_ccy[-1] + 1
        selected_ccy_ir_list = []
        for i in range(first_index_selected_ccy, last_index_selected_ccy):
            selected_ccy_ir_list.append(ir_list[i])
        return selected_ccy_ir_list

    def _select_ccy(self, ir_list, ccy):
        extract_ccy_list = extract_1d_list(ir_list, self._column_ccy)
        indices_ccy = [i for i, ccy_name in enumerate(extract_ccy_list) if (ccy_name == ccy) ]
        return indices_ccy

    def _add_cash_flow(self, ir_list):
        obj_trade_date = datetime.datetime.strptime(self._base_date, '%Y/%m/%d')
        over_night_date = (obj_trade_date + datetime.timedelta(days=1)).strftime('%Y/%m/%d')
        spot_date = (obj_trade_date + datetime.timedelta(days=2)).strftime('%Y/%m/%d')
        for i in range(len(ir_list)):
            if (ir_list[i][self._column_tenor] == 'O/N'):
                ir_list[i].append(self._base_date)
                ir_list[i].append(over_night_date)
            elif (ir_list[i][self._column_tenor] == 'T/N'):
                ir_list[i].append(over_night_date)
                ir_list[i].append(spot_date)
            else:
                ir_list[i].append(spot_date)
                ir_list[i].append(self._calc_end_date(spot_date, ir_list[i][self._column_tenor]))
        return ir_list

    def _calc_end_date(self, start_day, str_maturity):
        datetime_obj_start = datetime.datetime.strptime(start_day, '%Y/%m/%d')
        unit = str_maturity[-1]
        # extract a part of integer from the float plus unit type.
        # ex. '10.0Y'[0: len(10.0Y)- 3] -> '10'
        int_num = int(str_maturity[0:len(str_maturity)-3])
        if (unit == 'D'):
            trade_days = int_num
        elif (unit == 'W'):
            trade_days = int_num * 7
        elif (unit == 'M'):
            trade_days = int_num * 30
        elif (unit == 'Y'):
            trade_days = int_num * 365
        end_day = datetime_obj_start + datetime.timedelta(days=trade_days)
        return end_day.strftime('%Y/%m/%d')

    def _calc_day_count_fraction(self, start_date, end_date):
        datetime_obj_start = datetime.datetime.strptime(start_date, '%Y/%m/%d')
        datetime_obj_end = datetime.datetime.strptime(end_date, '%Y/%m/%d')
        daycount = float((datetime_obj_end - datetime_obj_start).days / self._convention)
        return daycount

    def get_convention(self):
        return self._convention

    def get_ir_list(self):
        return self._ir_list

    def get_base_date(self):
        return self._base_date

    def get_ccy(self):
        return self._ccy

    def get_roll_month(self):
        return self._roll_month

    def get_ir_list_with_DF_money_market(self):
        ir_list_DF_mm = self._calc_DF_money_market()
        return ir_list_DF_mm

    def get_ir_list_with_DF_swap_rate(self):
        ir_list_DF_sr = self._calc_DF_swap_rate()
        return ir_list_DF_sr

    def get_ir_list_interpolated_swap_rate(self):
        ir_list_interpolated_swap_rate = self._interpolated_ir_list_for_bootstrap()
        return ir_list_interpolated_swap_rate

    def get_ir_list_interpolated_DF_money_market(self):
        f_interpolation_DF_mm = self.interpolate_DF_money_market()
        return f_interpolation_DF_mm

    def _calc_DF_money_market(self):
        col_tenor = self._column_tenor
        col_sd = self._column_start_date
        col_ed = self._column_end_date
        col_rate = self._column_rate
        len_MM = 0
        for i in range(len(self._ir_list)):
            if (self._ir_list[i][self._column_market] == 'Money Market'):
                len_MM += 1
        ir_list_DF_money_market = [['','','','','','','','',''] for i in range(len(self._ir_list))]
        temp_discount_factor = np.zeros(len_MM)
        extract_date_list = extract_1d_list(self._ir_list, col_tenor)
        len_ir_list = len(self._ir_list)
        len_one_list_with_DF = len(ir_list_DF_money_market[0])
        index_DF  = len_one_list_with_DF - 1
        for i in range(len_MM):
            TN_flag = self._ir_list[i][col_tenor] in 'T/N'

        if (TN_flag == True):
            # 0/N
            index_ON = extract_date_list.index('O/N')
            temp_discount_factor[index_ON] = 1.0 / (1.0 + self._calc_day_count_fraction(self._ir_list[index_ON][col_sd], \
                                                                                        self._ir_list[index_ON][col_ed]) * float(self._ir_list[index_ON][col_rate]))
            # T/N
            index_TN = extract_date_list.index('T/N')
            temp_discount_factor[index_TN] = temp_discount_factor[index_ON] / \
                                                                            (1.0 + self._calc_day_count_fraction(self._ir_list[index_TN][col_sd], self._ir_list[index_TN][col_ed]) \
                                                                             * float(self._ir_list[index_TN][col_rate]))
            # libor
            for i in range(2, len_MM):
                temp_discount_factor[i] = temp_discount_factor[index_TN] \
                                                            / (1.0 + self._calc_day_count_fraction(self._ir_list[i][col_sd], self._ir_list[i][col_ed]) * float(self._ir_list[i][col_rate]))

            for i in range(len_MM):
                for j in range(len_one_list_with_DF - 1):
                    ir_list_DF_money_market[i][j] =self._ir_list[i][j+1]
                ir_list_DF_money_market[i][index_DF] = temp_discount_factor[i]

            for i in range(len_MM, len_ir_list):
                for j in range(len_one_list_with_DF - 1):
                    ir_list_DF_money_market[i][j] = self._ir_list[i][j+1]
                ir_list_DF_money_market[i][index_DF] = 0.0

        elif (TN_flag == False):
            # 0/N
            index_ON = extract_date_list.index('O/N')
            temp_discount_factor[index_ON] = 1.0 / (1.0 + self._calc_day_count_fraction(self._ir_list[index_ON ][col_sd], self._ir_list[index_ON ][col_ed]) \
                                                                             * float(self._ir_list[index_ON][col_rate ]))
            # libor
            for i in range(1, len_MM):
                temp_discount_factor[i] = temp_discount_factor[index_ON] * temp_discount_factor[index_ON]  \
                                                            / (1.0 + self._calc_day_count_fraction(self._ir_list[i][col_sd], self._ir_list[i][col_ed]) * float(self._ir_list[i][col_rate ]))

            for i in range(len_MM):
                for j in range(len_one_list_with_DF - 1):
                    ir_list_DF_money_market[i][j] =self._ir_list[i][j+1]
                ir_list_DF_money_market[i][index_DF] = temp_discount_factor[i]

            for i in range(len_MM, len_ir_list):
                for j in range(len_one_list_with_DF - 1):
                    ir_list_DF_money_market[i][j] = self._ir_list[i][j+1]
                ir_list_DF_money_market[i][index_DF] = 0.0

        return ir_list_DF_money_market

    def interpolate_DF_money_market(self):
        ir_list_DF_money_market = self._calc_DF_money_market()
        extract_date_list = extract_1d_list(ir_list_DF_money_market, 0)
        extract_DF_list = extract_1d_list(ir_list_DF_money_market, 8)
        index_1m = extract_date_list.index('1.0M')
        index_1y = extract_date_list.index('1.0Y')
        extract_date_list_mm_tenor = extract_date_list[index_1m : index_1y + 1]
        extract_date_list_mm_tenor[-1] = '12.0M'
        for i in range(len(extract_date_list_mm_tenor)):
            extract_date_list_mm_tenor[i] = float(extract_date_list_mm_tenor[i][0:-3])
        extract_DF_list_mm_tenor = extract_DF_list[index_1m : index_1y + 1]
        f_interpolated_DF_money_market = interp1d(extract_date_list_mm_tenor, extract_DF_list_mm_tenor)
        return f_interpolated_DF_money_market

    def interpolated_ir_list_DF_money_market(self):
        ir_list_DF_mm = self._calc_DF_money_market()
        extract_date_list = extract_1d_list(ir_list_DF_mm, 0)
        len_one_list_with_DF = len(ir_list_DF_mm[0])
        len_ir_list = len(ir_list_DF_mm)
        index_1m = extract_date_list.index('1.0M')
        index_1y = extract_date_list.index('1.0Y')
        len_1m = index_1m +1
        len_1y = index_1y + 1
        len_interpolated_ir_list_DF_mm = (len_1m - 1) + 12 + (len_ir_list - len_1y)
        interpolated_ir_list_DF_mm = [['', '', '', '', '', '', '', '', ''] for i in range(len_interpolated_ir_list_DF_mm)]
        f_interpolated_DF_money_market = self.interpolate_DF_money_market()
        # 1.0Mの前までコピー
        for i in range(0, len_1m - 1):
            for j in range(len_one_list_with_DF):
                interpolated_ir_list_DF_mm[i][j] = ir_list_DF_mm[i][j]
        # 1.0M 12.0MまでDFを補完
        for i in range(len_1m - 1, len_1m - 1 + 12 - 1):
            interpolated_ir_list_DF_mm[i][0] = "{}M".format(float((i - (len_1m - 1) + 1)))
        for i in range(len_1m - 1, len_1m - 1 + 12 - 1):
            interpolated_ir_list_DF_mm[i][1] = ir_list_DF_mm[i][1]
            interpolated_ir_list_DF_mm[i][2] = ir_list_DF_mm[i][2]
            interpolated_ir_list_DF_mm[i][3] = ''
            interpolated_ir_list_DF_mm[i][4] = ir_list_DF_mm[i][4]
            interpolated_ir_list_DF_mm[i][5] = ir_list_DF_mm[i][5]
            interpolated_ir_list_DF_mm[i][6] = self._spot_date
            interpolated_ir_list_DF_mm[i][7] = self._calc_end_date(self._spot_date, interpolated_ir_list_DF_mm[i][0])
            interpolated_ir_list_DF_mm[i][8] = float(f_interpolated_DF_money_market(float(interpolated_ir_list_DF_mm[i][0][0:-1])))
        for i in range( len_1m - 1 + 12 - 1 , len_interpolated_ir_list_DF_mm):
            for j in range(len_one_list_with_DF):
                interpolated_ir_list_DF_mm[i][j] = ir_list_DF_mm[i - index_1y -1][j]
        return interpolated_ir_list_DF_mm

    def _interpolate_swap_rate(self):
        extract_date_list = extract_1d_list(self._ir_list, self._column_tenor)
        extract_rate_list = extract_1d_list(self._ir_list, self._column_rate)
        index_1y = extract_date_list.index('1.0Y')
        extract_date_list_swap_tenor = extract_date_list[index_1y:]
        for i in range(len(extract_date_list_swap_tenor)):
            extract_date_list_swap_tenor[i] = calc_month(extract_date_list_swap_tenor[i])
        extract_swap_rate_list = extract_rate_list[index_1y:]
        f_interpolated_swap_rate = interp1d(extract_date_list_swap_tenor , extract_swap_rate_list)
        return f_interpolated_swap_rate

    def _interpolated_ir_list_for_bootstrap(self):
        ir_list_for_bootstrap = self.interpolated_ir_list_DF_money_market()
        extract_date_list = extract_1d_list(ir_list_for_bootstrap, 0)
        #
        index_1y = extract_date_list.index('1.0Y')
        len_index_1y = index_1y + 1
        f_interpolated_swap_rate = self._interpolate_swap_rate()
        max_maturity_in_unit_month = calc_month(ir_list_for_bootstrap[-1][0])
        seq_len_for_bootstrap = int( ((max_maturity_in_unit_month) - 12.0)  / self._roll_month) + 1
        seq_for_bootstrap = [['', '', '', '', '', '', '', '', ''] for i in range(seq_len_for_bootstrap + index_1y)]
        # base_tenor はスワップレートのテナーでもっとも短いテナーという気持ち
        base_tenor = int(float(ir_list_for_bootstrap[index_1y][0][0:-1]) * 12.0)  # change unit: year to month
        for i in range(index_1y , seq_len_for_bootstrap + index_1y):
            seq_for_bootstrap[i][0] = "{}M".format(base_tenor + (i - index_1y)  * self._roll_month)
        for i in range(index_1y):
            seq_for_bootstrap[i] = ir_list_for_bootstrap[i]
        for i in range(index_1y, seq_len_for_bootstrap + index_1y):
            seq_for_bootstrap[i][1] = self._string_swap
            seq_for_bootstrap[i][2] = self._ccy
            seq_for_bootstrap[i][3] = float(f_interpolated_swap_rate(float(seq_for_bootstrap[i][0][0:-1])))
            seq_for_bootstrap[i][4] = self._str_roll_month
            seq_for_bootstrap[i][5] = self._str_convention
            seq_for_bootstrap[i][6] = self._spot_date
            seq_for_bootstrap[i][7] = self._calc_end_date(self._spot_date, seq_for_bootstrap[i][0])
        # add discount factor for 12.0M calculated by calc_DF_money_market.
        seq_for_bootstrap[index_1y][8] = ir_list_for_bootstrap[index_1y][8]
        return seq_for_bootstrap
#TODO complete interpolated_ir_list_for_bootstrap

    def _calc_annuity(self, ir_list, target_tenor):
        extract_date_list = extract_1d_list(ir_list, 0)
        index_target_tenor = extract_date_list.index(target_tenor)
        index_roll_tenor = extract_date_list.index(self._str_roll_month)
        annuity = 0
        day_count_fraction = self._calc_day_count_fraction(ir_list[index_roll_tenor][6],  ir_list[index_roll_tenor][7])
        for i in range(index_roll_tenor, index_target_tenor):
            annuity += ir_list[i][8] * day_count_fraction
        return annuity

    def _calc_DF_swap_rate(self):
        col_sd = self._column_start_date
        col_ed = self._column_end_date
        interpolated_ir_list = self._interpolated_ir_list_for_bootstrap()
        extract_date_list = extract_1d_list(interpolated_ir_list, 0)
        index_1y = extract_date_list.index('12.0M')
        index_roll_tenor = extract_date_list.index(self._str_roll_month)
        index_start_tenor = index_1y + 1
        index_end_tenor = len(interpolated_ir_list)
        ### need to change day_count_fraction
        day_count_fraction = self._calc_day_count_fraction(self._ir_list[index_roll_tenor][col_sd],  self._ir_list[index_roll_tenor][col_ed])
        DF_swap_rate = np.zeros(len(interpolated_ir_list))
        for i in range(index_start_tenor, index_end_tenor):
            annuity = self._calc_annuity(interpolated_ir_list, interpolated_ir_list[i][0])
            swap_rate = interpolated_ir_list[i][3]
            DF_swap_rate[i] = 1.0 / (1.0 + day_count_fraction * swap_rate) * (1.0 - swap_rate * float(annuity) )
            interpolated_ir_list[i][8] = DF_swap_rate[i]
        return interpolated_ir_list

    def _interpolate_DF(self):
        # make list including days between start_day and end_day in fourth column.
        # DF_list = [0:tenor_name, 1:market_name, 2:ccy, 3:rate, 4:roll_month, 5:convetion, 6:start_date, 7:end_date, 8:DF]
        DF_list = self._calc_DF_swap_rate()
        len_DF_list = len(DF_list)
        # interpolated_DF_list [0: tenor_name, 1:days, 2:DF]
        interpolated_DF_list = [["", 0.0, 0.0] for i in range(len_DF_list)]
        for i in range(len_DF_list):
            interpolated_DF_list[i][0] = DF_list[i][0]
            interpolated_DF_list[i][2] = DF_list[i][8]
        # calc days from %Y/%m/%d
        for i in range(len_DF_list):
            if (interpolated_DF_list[i][0] == 'O/N'):
                interpolated_DF_list[i][1] = calc_trade_days(DF_list[i][6], DF_list[i][7])
                # TODO going to revise 1 and 2 day-count. have to consider Sat., Sun. and Holidays.
            elif (interpolated_DF_list[i][0] == 'T/N'):
                interpolated_DF_list[i][1] = calc_trade_days(DF_list[i][6], DF_list[i][7]) + 1
            else:
                interpolated_DF_list[i][1] = calc_trade_days(DF_list[i][6], DF_list[i][7]) + 2
        # interpolate DF
        index_trade_days = 1
        index_DF = 2
        f_interpolation_DF = interpolation_extract_list(interpolated_DF_list, index_trade_days, index_DF)
        return f_interpolation_DF

    def _calc_end_date_input_days(self, days_from_base_date):
        obj_start_date = datetime.datetime.strptime(self._base_date, '%Y/%m/%d')
        end_date = (obj_start_date + datetime.timedelta(days=days_from_base_date)).strftime('%Y/%m/%d')
        return end_date

    def get_DF(self, date):
        DF_list = self._calc_DF_swap_rate()
        max_maturity_days = calc_trade_days(DF_list[-1][6], DF_list[-1][7]) + 2
        interpolated_DF_list = [[i, '', 0.0] for i in range(max_maturity_days + 1)]
        f_interpolation_DF = self._interpolate_DF()
        for i in range(1, max_maturity_days + 1):
            interpolated_DF_list[i][1] = self._calc_end_date_input_days(interpolated_DF_list[i][0])
            interpolated_DF_list[i][2] = float(f_interpolation_DF(interpolated_DF_list[i][0]))
        # today's DF betauchi
        interpolated_DF_list[0][0] = 0
        interpolated_DF_list[0][1] = self._calc_end_date_input_days(interpolated_DF_list[0][0])
        interpolated_DF_list[0][2] = 1.0
        extract_end_date_list = extract_1d_list(interpolated_DF_list, 1)
        index_target_date = extract_end_date_list.index(date)
        return interpolated_DF_list[index_target_date][2]

    def get_DF_list(self):
        DF_list = self._calc_DF_swap_rate()
        max_maturity_days = calc_trade_days(DF_list[-1][6], DF_list[-1][7]) + 2
        interpolated_DF_list = [[i, '', 0.0] for i in range(max_maturity_days + 1)]
        f_interpolation_DF = self._interpolate_DF()
        for i in range(1, max_maturity_days + 1):
            interpolated_DF_list[i][1] = self._calc_end_date_input_days(interpolated_DF_list[i][0])
            interpolated_DF_list[i][2] = float(f_interpolation_DF(interpolated_DF_list[i][0]))
        # today's DF betauchi
        interpolated_DF_list[0][0] = 0
        interpolated_DF_list[0][1] = self._calc_end_date_input_days(interpolated_DF_list[0][0])
        interpolated_DF_list[0][2] = 1.0
        return interpolated_DF_list
