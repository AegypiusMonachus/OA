import datetime,time
from datetime import timedelta

'''本周时间'''
def getData(now=None):

    if now == None:
        now = datetime.date.today()
        nows = int(time.time())

    else:
        now = now
        nows = now
        now = datetime.date.fromtimestamp(now)
        print(now)

    zeroPointToday = int(time.mktime(now.timetuple()))
    endPointToday = zeroPointToday + 60 * 60 * 24
    # print(zeroPointToday)
    # print(endPointToday)

    '''昨日时间'''
    endPointYestoday = zeroPointToday
    # print('昨日%s' % endPointYestoday)
    zeroPointYestoday = endPointYestoday - 60 * 60 * 24
    # print('昨日%s' % zeroPointYestoday)


    now = now - datetime.timedelta()
    this_week_start = now - timedelta(days=now.weekday())
    this_week_start_num = int(time.mktime(this_week_start.timetuple()))
    # print('本周start_%s'%this_week_start_num)
    # now_time = datetime.datetime.fromtimestamp(int(time.mktime(now.timetuple())) - int(time.time() - time.timezone) % 86400 + (60 * 60 * 24))
    this_week_end = now + timedelta(days=7 - now.weekday())
    this_week_end_num = int(time.mktime(this_week_end.timetuple()))
    # print('本周end_%s'%this_week_end_num)

    '''上周时间'''
    last_week_start = now - timedelta(days=now.weekday() + 7)
    last_week_start_num = int(time.mktime(last_week_start.timetuple()))
    # print('上周start_%s'%last_week_start_num)
    last_week_end = now - timedelta(days=now.weekday() + 1)
    last_week_end_num = this_week_start_num
    # print('上周end_%s'%last_week_end_num)


    '''本月时间'''
    this_month_start = datetime.datetime(now.year, now.month, 1)
    this_month_start_num = int(time.mktime(this_month_start.timetuple()))
    # print('本月start_%s'%this_month_start_num)
    this_month_end = datetime.datetime(now.year, now.month + 1, 1) - timedelta(days=1)
    this_month_end = datetime.datetime.fromtimestamp(int(time.mktime(this_month_end.timetuple())) + (60 * 60 * 24))
    this_month_end_num = int(time.mktime(this_month_end.timetuple()))
    # print('本月end_%s'%this_month_end_num)


    '''上月时间'''
    last_month_end = this_month_start - timedelta(days=1)
    last_month_end = datetime.datetime.fromtimestamp(int(time.mktime(last_month_end.timetuple())) + (60 * 60 * 24 - 1))
    last_month_end_num = int(time.mktime(last_month_end.timetuple()))
    # print('上月start_%s'%last_month_end_num)
    last_month_start = datetime.datetime(last_month_end.year, last_month_end.month, 1)
    last_month_start_num = int(time.mktime(last_month_start.timetuple()))
    last_month_end_num = this_month_start_num
    # print('上月start_%s'%last_month_start_num)

    result = {}
    result['today'] = zeroPointToday
    result['yesterday_start'] = zeroPointYestoday
    result['yesterday_end'] = endPointYestoday
    result['thisweek_start'] = this_week_start_num
    result['thisweek_end'] = this_week_end_num
    result['lastweek_start'] = last_week_start_num
    result['lastweek_end'] = last_week_end_num
    result['thismonth_start'] = this_month_start_num
    result['thismonth_end'] = this_month_end_num
    result['lastmonth_start'] = last_month_start_num
    result['lastmonth_end'] = last_month_end_num
    return result

def changeData(datas):
    d = datetime.datetime.strptime(datas, "%Y-%m-%d")
    t = d.timetuple()
    timeStamp = int(time.mktime(t))
    return timeStamp


def changeData_str(datas):
    d = datetime.datetime.fromtimestamp(datas)
    return d
