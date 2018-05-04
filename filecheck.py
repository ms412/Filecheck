#!/usr/bin/env python3
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


__app__ = "FEC2influxDB Adapter"
__VERSION__ = "0.9"
__DATE__ = "20.09.2016"
__author__ = "Markus Schiesser"
__contact__ = "Markus.Schiesser@swisscom.com"
__copyright__ = "Copyright (C) 2016 Markus Schiesser"
__license__ = 'GPL v3'

import sys
import os
import datetime
import json
#import logging

from configobj import ConfigObj
#from library.tempfile import tempfile
from library.remote import remoteSSH
from library.loghandler import loghandler
#from library.msgbus import msgbus


class manager(object):

    def __init__(self,cfgfile):
        self._cfgfile = cfgfile

        '''
        Configuration variables
        '''
        self._cfg_general = None
        self._cfg_server = None
        self._cfg_db = None
        '''
        Object Handles
        '''
        self._db = None

    def readcfg(self):

        print('openfile',self._cfgfile)
        try:
            configObj = ConfigObj(self._cfgfile)
            print(configObj)
            #return True
        except:
            print('ERROR open file:',self._cfgfile)
            return False

        self._cfg_general = configObj.get('GENERAL')
        self._cfg_server = configObj.get('SERVER')
        self._cfg_db = configObj.get('DB')

        self._log = None

        print('Test',self._cfg_general)

        return True

    def start_loging(self):
        self._log = loghandler(self._cfg_general)

        self._log.debug('Start FEC2influxDB Version 0.9 Date 24.11.2016')

    def getFiles(self):
        _temp = {}
        ssh = remoteSSH('192.168.2.254','pi','nd%aG9im')
        ssh.connect()
     #   ssh.chdir('/')
     #   ssh.getData()
     #   ssh.getDir()
        print('tet')
     #   ssh.fileType('tst')
        x = ssh.sftp_walk('/proc',_temp)
        print('dn',x)
        return

    def run(self):
        """
        Entry point, initiates components and loops forever...
        """
        if not self.readcfg():
            print('Failed to open file')
            return False
        self.start_loging()
        self.getFiles()


        return True


if __name__ == "__main__":

    print ('main',len(sys.argv))
    if len(sys.argv) == 2:
        print('with commandline',sys.argv[1])
        cfgfile = sys.argv[1]
    else:
        print('read default file')
        cfgfile = 'C:/Users/oper/PycharmProjects/FEC2influxDB2/FEC2influxDB.cfg'
        cfgfile ='./FEC2influxDB.cfg'
      #  cfgfile = '/home/tgdscm41/FEC2influxDB/FEC2mqtt2.cfg'

    mgr_handle = manager(cfgfile)
    mgr_handle.run()