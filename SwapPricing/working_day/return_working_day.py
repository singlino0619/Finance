import jpholiday
import datetime
#jpholiday.is_holiday(datetime.date(2030, 1, 1))
def calc_working_day(date, convention):
    week_name = ['月', '火', '水', '木', '金', '土', '日']
    date_obj_original = datetime.datetime.strptime(date,  '%Y/%m/%d')
    date_original = date_obj_original.strftime('%Y/%m/%d')
    if (convention=='following'):
        while (check_holiday(date) or check_Sat(date) or check_Sun(date)):
            date_obj = datetime.datetime.strptime(date,  '%Y/%m/%d')
            date_obj = date_obj + datetime.timedelta(days=1)
            date = date_obj.strftime('%Y/%m/%d')
        return date
    elif (convention=='modified following'):
        date_obj = datetime.datetime.strptime(date,  '%Y/%m/%d')
        while (check_holiday(date) or check_Sat(date) or check_Sun(date)):
            date_obj = date_obj + datetime.timedelta(days=1)
            date = date_obj.strftime('%Y/%m/%d')
        if (date_obj.month == date_obj_original.month):
            return date
        else:
            date_for_mf = date_original
            while (check_holiday(date_for_mf ) or check_Sat(date_for_mf ) or check_Sun(date_for_mf )):
                date_obj = datetime.datetime.strptime(date_original,  '%Y/%m/%d')
                date_obj = date_obj - datetime.timedelta(days=1)
                date_for_mf  = date_obj.strftime('%Y/%m/%d')
            return date_for_mf

def check_holiday(str_date):
    date_obj = datetime.datetime.strptime(str_date,  '%Y/%m/%d')
    year = date_obj.year
    month = date_obj.month
    day = date_obj.day
    date = datetime.date(year, month, day)
    is_holiday = jpholiday.is_holiday(date)
    return is_holiday

def calc_date_after_holiday(date):
    while (check_holiday(date)==True):
        date_obj = datetime.datetime.strptime(date,  '%Y/%m/%d')
        date_obj = date_obj + datetime.timedelta(days=1)
        date = date_obj.strftime('%Y/%m/%d')
    return date

def check_Sat(date):
    date_obj = datetime.datetime.strptime(date, '%Y/%m/%d')
    if (date_obj.weekday() == 5):
        return True
    else:
        return False

def check_Sun(date):
    date_obj = datetime.datetime.strptime(date, '%Y/%m/%d')
    if (date_obj.weekday() == 6):
        return True
    else:
        return False


def cash_flow_generator(start_day, tenor, convention):
    start_obj = datetime.datetime.strptime(start_day, '%Y/%m/%d')
    day = start_day[-2:]
    month = start_obj.month + int(tenor[0])
    year = start_obj.year
    if (month <= 12):
        pass
    elif (month > 12):
        month -= 12
        year += 1
    end_date = str(year) + '/' + str(month) + '/' + str(day)
    working_end_date = calc_working_day(end_date, convention)
    return working_end_date

def create_end_date(basis_date, tenor, convention, num_cash_flow, lag):
    end_date_list = ['' for i in range(num_cash_flow+1)]
    len_list = len(end_date_list)
    basis_date_obj = datetime.datetime.strptime(basis_date, '%Y/%m/%d')
    basis_year = basis_date_obj.year
    basis_month = basis_date_obj.month
    basis_day = basis_date_obj.day
    lag_date = basis_date_obj + datetime.timedelta(days=lag)
    end_date_list[0] = lag_date.strftime('%Y/%m/%d')
    for i in range(1,  len_list):
        cumulative_month = basis_month + int(tenor[-2]) * i
        year, month = divmod(cumulative_month, 12)
        if (month==0):
            end_date_month = 12
        else:
            end_date_month = month
        end_date_year = basis_year + year
        str_end_date = str(end_date_year) + '/' + str(end_date_month) + '/' + str(basis_day)
        end_date_obj = datetime.datetime.strptime(str_end_date, '%Y/%m/%d')
        end_date = end_date_obj.strftime('%Y/%m/%d')
        working_end_date = calc_working_day(end_date, convention)
        end_date_list[i] = working_end_date
    return end_date_list

def create_start_date(basis_date, tenor, convention, num_cash_flow, lag):
    end_date_list = create_end_date(basis_date, tenor, convention, num_cash_flow, lag)
    start_date_list = ['' for i in range(len(end_date_list))]
    start_date_list[0] = basis_date
    for i in range(1, len(end_date_list)):
        start_date_list[i] = end_date_list[i-1]
    return start_date_list
