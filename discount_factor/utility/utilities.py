import datetime
from scipy import interpolate

def tenor_to_days(str_tenor):
    if(str_tenor=='O/N'):
        days = 1
    elif(str_tenor=='T/N'):
        days = 2
    elif(str_tenor[-1]=='W'):
        days = int(str_tenor[0:len(str_tenor)-1]) * 7
    elif(str_tenor[-1]=='M'):
        days = int(str_tenor[0:len(str_tenor)-1]) * 30
    elif(str_tenor[-1]=='Y'):
        days = int(str_tenor[0:len(str_tenor)-1]) * 365
    return days

def str_dcc_to_num(str_dcc):
    if(str_dcc=='ACT/360'):
        dcc_num = 360
    elif(str_dcc=='ACT/365F'):
        dcc_num = 365
    return dcc_num

def calc_days(str_start_date, str_end_date):
    start_date_obj = datetime.datetime.strptime(str_start_date, '%Y/%m/%d')
    end_date_obj = datetime.datetime.strptime(str_end_date, '%Y/%m/%d')
    days =(end_date_obj - start_date_obj).days
    return days

def interpolation(array_x, array_y, str_kind):
    f = interpolate.interp1d(array_x, array_y, kind=str_kind)
    return f
