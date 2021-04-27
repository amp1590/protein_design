import sys
import datetime


def get_time1(ar1, ar2):
    time=datetime.datetime.now()
    output="Hi %s and %s, the current time is %s" % (ar1,ar2,time)
    print(output)
    return output