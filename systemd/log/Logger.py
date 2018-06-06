#!/usr/bin/env python
import logging
import os
from pathlib import Path

import yaml


class Logger:
    isInit = False
    usedLoggerList = {}
    loggerConfigData = None

    @staticmethod
    def initLogger():
        Logger.loadLoggerConfigData()

        logDirectory = os.path.dirname(Logger.loggerConfigData["log"]["filename"])

        if not os.path.exists(logDirectory):
            os.makedirs(logDirectory)

    @staticmethod
    def loadLoggerConfigData():
        configPath = Path("systemd/config/")
        configFile = configPath / "logging-config.yml"

        with configFile.open() as loggerConfigStream:
            Logger.loggerConfigData = yaml.load(loggerConfigStream)

    @staticmethod
    def getLogger(className):
        if className in Logger.usedLoggerList:
            return Logger.usedLoggerList[className]

        if not Logger.isInit:
            Logger.initLogger()

        loggerConfigData = Logger.loggerConfigData
        logger = logging.getLogger(className)
        logger.setLevel(loggerConfigData["log"]["level"])
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(
            logging.Formatter(loggerConfigData["log"]["format"])
        )
        logger.addHandler(handler)

        Logger.usedLoggerList[className] = logger

        return logger
