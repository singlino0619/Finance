import pandas as pd
import datetime
import numpy as np
import matplotlib.pyplot as plt
import single_df_curve.utility.utilities as utl

class discount_factor():
    def __init__(self, df, str_ccy):
        self._str_ccy = str_ccy
        self._df_ir = df[df['Currency']==str_ccy]
        self._base_date_obj = datetime.datetime.strptime(self._df_ir['Date'][0], '%Y/%m/%d')
        self._spot_date = self._base_date_obj + datetime.timedelta(days=int(self._df_ir['lag(day)'][0]))
        self._frequency_year = (self._df_ir.at[self._df_ir.query('Product == "SWAP"')['Frequency(month)'].index[0], 'Frequency(month)']) /12
        self._str_frequency = str(int(self._df_ir.at[self._df_ir.query('Product == "SWAP"')['Frequency(month)'].index[0], 'Frequency(month)'])) + 'M'

    def get_raw_rate(self, str_tenor):
        return self._df_ir.set_index('Tenor').at[str_tenor, 'Rate']

    def calc_DF_short_term(self, str_tenor):
        short_term_rate = self.get_raw_rate(str_tenor)
        dcc = utl.str_dcc_to_num(self._df_ir.set_index('Tenor').at[str_tenor, 'Dcc'])
        target_date_obj = self._base_date_obj + datetime.timedelta(days = int(utl.tenor_to_days(str_tenor)))
        dfc = (target_date_obj - self._base_date_obj).days / dcc
        DF = 1 / ( 1 + dfc * short_term_rate)
        return DF

    def get_str_frequency(self):
        return self._str_frequency

    def get_array_swap_tenor(self):
        index_one_year = self._df_ir.query('Tenor == "1Y"').index[0]
        array_swap_tenor = self._df_ir['Tenor'][index_one_year:].apply(lambda x: int(x[0:len(x)-1]))
        list_array_swap_tenor = list(array_swap_tenor)
        return list_array_swap_tenor

    def get_array_swap_rate(self):
        index_one_year = self._df_ir.query('Tenor == "1Y"').index[0]
        array_swap_rate = self._df_ir['Rate'][index_one_year:]
        list_array_swap_rate = list(array_swap_rate.map(lambda x: float(x)))
        return list_array_swap_rate

    def interpolation_swap_rate(self, kind):
        array_x = self.get_array_swap_tenor()
        array_y = self.get_array_swap_rate()
        func = utl.interpolation(array_x, array_y, kind)
        return func

    def create_tenor_for_bootstrap(self):
        initial_year = self.get_array_swap_tenor()[0]
        last_year = self.get_array_swap_tenor()[-1]
        ndarray_swap_tenor =  np.arange(initial_year, last_year + self._frequency_year, self._frequency_year)
        return ndarray_swap_tenor

    def create_swap_rate_for_bootstrap(self, kind):
        func_swap_rate_interpolated = self.interpolation_swap_rate(kind)
        ndarray_swap_tenor = self.create_tenor_for_bootstrap()
        ndarray_swap_rate =  func_swap_rate_interpolated(ndarray_swap_tenor)
        return ndarray_swap_rate

    def zip_swap_tenor_rate(self, kind):
        list_swap_tenor = list(self.create_tenor_for_bootstrap())
        list_swap_rate = list(self.create_swap_rate_for_bootstrap(kind))
        return list(zip(list_swap_tenor, list_swap_rate))

    def get_array_str_for_bootstrap(self):
        frequency = self._frequency_year * 12
        array_int_for_bootstrap = []
        while frequency  < 12:
            array_int_for_bootstrap.append(int(frequency))
            frequency = frequency + int((self._frequency_year * 12))
        array_str_for_bootstrap = list(map(lambda x: str(x) + 'M', array_int_for_bootstrap))
        return array_str_for_bootstrap

    def array_DF_short_term_for_bootstrap(self):
        array_str_for_bootstrap = self.get_array_str_for_bootstrap()
        array_DF_for_bootstrap = list(map(lambda x: self.calc_DF_short_term(x), array_str_for_bootstrap))
        array_int_for_bootstrap = list(map(lambda x: int(x[0])/12, array_str_for_bootstrap))
        array_for_bootstrap = list(zip(array_int_for_bootstrap, array_DF_for_bootstrap))
        return array_for_bootstrap

    def calc_DF_bootstrap(self, kind, unit_year):
        array_DF_short_term_for_bootstrap = self.array_DF_short_term_for_bootstrap()
        array_swap_rate = [j for i, j in self.zip_swap_tenor_rate(kind)]
        dcf = self._frequency_year
        array_DF_value = self.do_bootstrapping(dcf, array_swap_rate, array_DF_short_term_for_bootstrap)
        if (unit_year == True):
            array_tenor = [i for i, j in self.zip_swap_tenor_rate(kind)]
        else:
            array_tenor = map(lambda x : x * 365, [i for i, j in self.zip_swap_tenor_rate(kind)])
        array_DF = list(zip(array_tenor, array_DF_value))
        return array_DF

    def do_bootstrapping(self, dcf, array_swap_rate, array_DF_short_term):
        sum_DF = sum([j for i, j in array_DF_short_term])
        num_bootstrapping = len(array_swap_rate)
        array_DF_value = []
        for i in range(num_bootstrapping):
            DF = 1.0 / (1.0 + dcf * array_swap_rate[i])  * (1.0 - array_swap_rate[i]* dcf * sum_DF)
            array_DF_value.append(DF)
            sum_DF += DF
        return array_DF_value

    def array_DF_short_term(self):
        array_DF_tenor = []
        array_DF_value = []
        series_tenor = self._df_ir.query('Product == "LIBOR"')['Tenor']
        for i in range(len(series_tenor)):
            array_DF_tenor.append(float(utl.tenor_to_days(series_tenor[i])) + float(self._df_ir['lag(day)'][0]))
            array_DF_value.append(self.calc_DF_short_term(series_tenor[i]))
        array_DF_short_term = list(zip(array_DF_tenor, array_DF_value))
        return array_DF_short_term

    def array_DF(self, kind):
        array_DF_short = self.array_DF_short_term()
        array_DF_swap = self.calc_DF_bootstrap(kind, False)
        array_base_date = [(0.0, 1.0)]
        array_DF = array_base_date + array_DF_short + array_DF_swap
        return array_DF

    def get_DF(self, target_date, kind_swap_rate, kind_DF):
        array_DF = self.array_DF(kind_swap_rate)
        array_DF_x = [i for i, j in array_DF]
        array_DF_y = [j for i, j in array_DF]
        f = utl.interpolation(array_DF_x, array_DF_y, kind_DF)
        days = (datetime.datetime.strptime(target_date, '%Y/%m/%d') - self._spot_date).days
        return f(days)

    ##### for get_array_DF. need to be updated to get_array_DF make get_DF_function before into for loop.
    def get_DF_function(self, kind_swap_rate, kind_DF):
        array_DF = self.array_DF(kind_swap_rate)
        array_DF_x = [i for i, j in array_DF]
        array_DF_y = [j for i, j in array_DF]
        f = utl.interpolation(array_DF_x, array_DF_y, kind_DF)
        return f

    def get_array_DF(self, str_initial_date, str_end_date, kind_swap_rate, kind_DF):
        array_date = []
        array_DF = []
        initial_date_dt_obj = datetime.datetime.strptime(str_initial_date, '%Y/%m/%d')
        str_spot_date = self._spot_date.strftime('%Y/%m/%d')
        days_for_array = utl.calc_days(str_initial_date, str_end_date)
        days_from_base_date = utl.calc_days(str_spot_date, str_initial_date)
        DF_function = self.get_DF_function(kind_swap_rate, kind_DF)
        for i in range(days_for_array + 1):
            days= i + days_from_base_date
            date = (self._spot_date + datetime.timedelta(days=i + days_from_base_date)).strftime('%Y/%m/%d')
            array_date.append(date)
            DF = DF_function(days)
            array_DF.append(float(DF))
        array_DF = list(zip(array_date, array_DF))
        return array_DF

    def to_csv_array_DF(self, str_initial_date, str_end_date, kind_swap_rate, kind_DF):
        array_DF = self.get_array_DF(str_initial_date, str_end_date, kind_swap_rate, kind_DF)
        df_array_DF = pd.DataFrame(array_DF)
        str_initial_date = str_initial_date.replace('/', '-')
        str_end_date = str_end_date.replace('/', '-')
        df_array_DF.to_csv('DF' + '_' + self._str_ccy + '_' +  str_initial_date + '_' + str_end_date + ".csv")
