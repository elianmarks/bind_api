# -*- coding: utf-8 -*-
#Elliann Marks
#elian.markes@gmail.com
#

#Bibliotecas
import logging
from contextlib import closing
from config import LOG_FILE

class ModuleLog():

    def __init__(self):
        #Configuracoes de logging
        self.logFormat = "%(asctime)s - %(levelname)s - %(message)s"
        self.logArquivo = LOG_FILE
        self.logLevel = logging.INFO
        #Configuracoes de log
        self.log = logging.getLogger(__name__)
        self.log.setLevel(self.logLevel)
        with closing(logging.FileHandler(self.logArquivo)) as self.logHandler:
            self.logHandler.setLevel(self.logLevel)
            self.logFormato = logging.Formatter(self.logFormat)
            self.logHandler.setFormatter(self.logFormato)
            self.log.addHandler(self.logHandler)

#Module log
moduleLog = ModuleLog()

def logInfo(stringLog):
    moduleLog.log.info(stringLog)

def logWarn(stringLog):
    moduleLog.log.warn(stringLog)

def logError(stringLog):
    moduleLog.log.error(stringLog)
