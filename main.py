#!/usr/bin/env python
# encoding: utf-8
# ===============================================================================
#
#         FILE:  
#
#        USAGE:    
#
#  DESCRIPTION:  
#
#      OPTIONS:  ---
# REQUIREMENTS:  ---
#         BUGS:  ---
#        NOTES:  ---
#       AUTHOR:  YOUR NAME (), 
#      COMPANY:  
#      VERSION:  1.0
#      CREATED:  
#     REVISION:  ---
# ===============================================================================

import uiautomator2 as u2
import time
import requests
from datetime import datetime
import json
from sys import argv

buy_button = (830, 2025)
time_format = "%Y-%m-%d %H:%M:%S.%f"
try:
    buy_time = argv[1]
except IndexError:
    raise RuntimeError("start time not defined")


class Timer(object):
    def __init__(self, start_time, sleep_interval=0.5):
        self.buy_time = datetime.strptime(start_time.__str__(), time_format)
        self.buy_time_ms = int(time.mktime(self.buy_time.timetuple()) * 1000.0 + self.buy_time.microsecond / 1000)

        self.sleep_interval = sleep_interval

        self.diff_time = self.local_jd_time_diff()

        info("购买时间：{}".format(start_time))

    @staticmethod
    def jd_time():
        """
        从京东服务器获取时间毫秒
        :return:
        """
        url = 'https://a.jd.com//ajax/queryServerData.html'
        ret = requests.get(url).text
        js = json.loads(ret)
        return int(js["serverTime"])

    @staticmethod
    def local_time():
        """
        获取本地毫秒时间
        :return:
        """
        return int(round(time.time() * 1000))

    def local_jd_time_diff(self):
        """
        计算本地与京东服务器时间差
        :return:
        """
        local_time = self.local_time()
        jd_time = self.jd_time()
        diff = local_time - jd_time
        info("本地时间:%s, JD时间:%s，误差:%s" % (local_time, jd_time, diff))
        return diff

    def start(self):
        info('正在等待到达设定时间:{}，检测本地时间与京东服务器时间误差为【{}】毫秒'.format(
            self.buy_time.strftime(time_format),
            self.diff_time)
        )
        while True:
            # 本地时间减去与京东的时间差，能够将时间误差提升到0.1秒附近
            # 具体精度依赖获取京东服务器时间的网络时间损耗
            if self.local_time() - self.diff_time >= self.buy_time_ms:
                info('时间到达，开始执行……')
                break
            else:
                sleep_time = abs(self.diff_time) / 1000
                if int(time.time()) % 30 == 0:
                    self.diff_time = self.local_jd_time_diff()
                    info('正在等待到达设定时间:{}，检测本地时间与京东服务器时间误差为【{}】毫秒'.format(
                        self.buy_time.strftime(time_format),
                        self.diff_time)
                    )
                    info("当前sleep: %s" % sleep_time)
                time.sleep(sleep_time)


def info(words):
    now = datetime.now().strftime(time_format)
    print("[%s] %s" % (now, words))


def main():
    d = u2.connect()
    clock = Timer(buy_time)
    clock.start()
    while True:
        d.click(*buy_button)


if __name__ == "__main__":
    main()
