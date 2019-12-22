#!/usr/bin/python
# -*- coding: UTF-8 -*-

import logging
import time
import sys
import os
from .speedtest import speedtest
from configloader import  load_config
from Munager.MuAPI.webapi_utils import WebApi
class Speedtest(object):

    def __init__(self):
        import threading
        self.event = threading.Event()
        self.has_stopped = False
        self.config = load_config()
        self.webapi = WebApi()

    def speedtest_thread(self):
        if self.event.wait(600):
            return

        logging.info("Speedtest starting...You can't stop right now!")
        CTid = 0
        speedtest_ct = speedtest.Speedtest()
        speedtest_ct.get_servers()
        servers_list = []
        for _, servers in sorted(speedtest_ct.servers.items()):
            for server in servers:
                if server['country'].find(
                        'China') != -1 and server['sponsor'].find('Telecom') != -1:
                    servers_list.append(server)
        speedtest_ct.get_best_server(servers_list)
        results_ct = speedtest_ct.results
        CTPing = str(results_ct.server['latency']) + ' ms'
        speedtest_ct.download()
        CTDLSpeed = str(
            round(
                (results_ct.download / 1000 / 1000),
                2)) + " Mbit/s"
        speedtest_ct.upload()
        CTUpSpeed = str(
            round(
                (results_ct.upload / 1000 / 1000),
                2)) + " Mbit/s"

        CUid = 0
        speedtest_cu = speedtest.Speedtest()
        speedtest_cu.get_servers()
        servers_list = []
        for _, servers in sorted(speedtest_cu.servers.items()):
            for server in servers:
                if server['country'].find(
                        'China') != -1 and server['sponsor'].find('Unicom') != -1:
                    servers_list.append(server)
        speedtest_cu.get_best_server(servers_list)
        results_cu = speedtest_cu.results
        CUPing = str(results_cu.server['latency']) + ' ms'
        speedtest_cu.download()
        CUDLSpeed = str(
            round(
                (results_cu.download / 1000 / 1000),
                2)) + " Mbit/s"
        speedtest_cu.upload()
        CUUpSpeed = str(
            round(
                (results_cu.upload / 1000 / 1000),
                2)) + " Mbit/s"

        CMid = 0
        speedtest_cm = speedtest.Speedtest()
        speedtest_cm.get_servers()
        servers_list = []
        for _, servers in sorted(speedtest_cm.servers.items()):
            for server in servers:
                if server['country'].find(
                        'China') != -1 and server['sponsor'].find('Mobile') != -1:
                    servers_list.append(server)
        speedtest_cm.get_best_server(servers_list)
        results_cm = speedtest_cm.results
        CMPing = str(results_cm.server['latency']) + ' ms'
        speedtest_cm.download()
        CMDLSpeed = str(
            round(
                (results_cm.download / 1000 / 1000),
                2)) + " Mbit/s"
        speedtest_cm.upload()
        CMUpSpeed = str(
            round(
                (results_cm.upload / 1000 / 1000),
                2)) + " Mbit/s"


        self.webapi.postApi('func/speedtest',
                             {'node_id': self.config.get("node_id",0)},
                             {'data': [{'telecomping': CTPing,
                                        'telecomeupload': CTUpSpeed,
                                        'telecomedownload': CTDLSpeed,
                                        'unicomping': CUPing,
                                        'unicomupload': CUUpSpeed,
                                        'unicomdownload': CUDLSpeed,
                                        'cmccping': CMPing,
                                        'cmccupload': CMUpSpeed,
                                        'cmccdownload': CMDLSpeed}]})

        logging.info("Speedtest finished")

    @staticmethod
    def thread_db(obj):
        config = load_config()
        if config.get("speedtest",0)== 0:
            return
        global db_instance
        db_instance = obj()
        try:
            while True:
                try:
                    db_instance.speedtest_thread()
                except Exception as e:
                    import traceback
                    trace = traceback.format_exc()
                    logging.error(trace)
                    #logging.warn('db thread except:%s' % e)
                if db_instance.event.wait(config.get("speedtest") * 3600):
                    break
                if db_instance.has_stopped:
                    break
        except KeyboardInterrupt as e:
            pass
        db_instance = None

    @staticmethod
    def thread_db_stop():
        global db_instance
        db_instance.has_stopped = True
        db_instance.event.set()
