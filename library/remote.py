import paramiko
import time
import os
import csv
import os
import stat
#from stat import S_ISDIR

#from library.msgbus import msgbus

class remoteSSH():

    def __init__(self,host,user,passwd):

        self._host = host
        self._user = user
        self._passwd = passwd

        self._sftp = None

        self._tree = {}

    def __del__(self):
        if self._sftp is not None:
            self._sftp.close()

    def connect(self):
        self._sshClient = paramiko.SSHClient()
        self._sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self._sshClient.connect(self._host, username=self._user, password=self._passwd,timeout=10)
         #   self._sshClient.start_client()
            self._sftp = self._sshClient.open_sftp()
            print('connect')
        except Exception as e:
            print ("Connection Failed")
            return False

        return True

    def chdir(self,directory):
        try:
            self._sftp.chdir(directory)
            print('changed to directory')
        except Exception as e:
            print('directory not found')
            return False

        return True

    def getData(self):
        print(self._sftp.listdir_attr())
        for item in self._sftp.listdir_attr():
            print('Attribute',item)
            print('Name',item.filename)

    def getDir(self):
            print('ls',self._sftp.listdir)
            for i in self._sftp.listdir():
                lstatout = str(self._sftp.lstat(i)).split()[0]

                if 'd' not in lstatout:
                    print('is a file',i)

    def getlatestFile(self,filter):
        fileDate = 0
        fileName = None
        for fileattr in self._sftp.listdir_attr():
            if fileattr.filename.startswith(filter) and fileattr.filename.endswith('txt') and fileattr.st_mtime > fileDate:
                fileDate = fileattr.st_mtime
                fileName = fileattr.filename

        return fileName,fileDate

    def executeCmd(self,cmd):
      #  print(cmd)
        (stdin,stdout,stderr)=self._sshClient.exec_command(cmd)
      # print('stderr',stderr.readlines())
       # for line in stdout.readlines():
        #    print(line)
        #print('STDOUT',stdout.read().split())
        #print('STDERR',stderr.read().split())
        return stdout.readlines()

    def fileType(self,file):
        _return = None
        _cmd = '/usr/bin/file --mime-type %s'% (file)
        try:
            stdout = self.executeCmd(_cmd)
            _temp = stdout[0]
            _return = _temp.split()[1]
        except:
            print('Error command file on %s output: %s'%(file,stdout))
     #   print(_str.split()[1])
     #   print(stdout)
        return _return

    def getMD5(self,file):
        _return = None
        _cmd = '/usr/bin/md5sum %s' % (file)
        try:
            stdout = self.executeCmd(_cmd)
            _temp = stdout[0]
            _return = _temp.split()[0]
        except:
            print('Error command file MD5 on %s output: %s'%(file,stdout))
        #   print(_str.split()[1])
        #   print(stdout)
        return _return

    def sftp_walk(self,remotepath,dict):
   #     print(remotepath)
        # Kindof a stripped down  version of os.walk, implemented for
        # sftp.  Tried running it flat without the yields, but it really
        # chokes on big directories.
        path=remotepath
        files=[]
        folders=[]
      #  print('start')


       # info = self._sftp.stat(remotepath)
        #print(info,info.st_size)

        for f in self._sftp.listdir_attr(remotepath):
            if stat.S_ISDIR(f.st_mode):
                folders.append(f.filename)
            elif stat.S_ISREG(f.st_mode):
                files.append(f.filename)
            else:
                print('special file: %s'% f.filename)


             #   if stat.S_ISREG(f.st_mode):
              #      files.append(f.filename)
       # print('Folder',folders)
      #  print('XX',path,folders,files)
        for file in files:
            info = self._sftp.stat(remotepath+'/'+file)
            _t = {}
            _t['SIZE'] = info.st_size
            _t['UID'] = info.st_uid
            _t['GID'] = info.st_gid
            _t['MODE'] = info.st_mode
            _t['ATIME'] = info.st_atime
            _t['MTIME'] = info.st_mtime
            _t['TYPE'] = self.fileType(remotepath+'/'+file)
            _t['MD5'] = self.getMD5(remotepath+'/'+file)
        #    dict[file]['SIZE']= info.st_size
            dict[file] = _t

      #  dict['FILES']=files

      #  try:
      #  yield path,folders,files
        for folder in folders:
            try:
         #       new_path=os.path.join(remotepath,folder)
                new_path = remotepath +'/'+ folder



                print('newpath',new_path)
                _temp = {}
                x = self.sftp_walk(new_path,_temp)
             #   print('TEST',x)
                dict[folder]=x
         #       yield x
            except:
                dict[folder]='Access Denide'
                print('Access Denide')

        return dict

    def getFilesFromDate(self,date,filter):
        filelist = []
        print ('fromGetDate',date,filter)
        for fileattr in self._sftp.listdir_attr():
            if fileattr.filename.startswith(filter) and fileattr.filename.endswith('txt') and fileattr.st_mtime > date:
                filelist.append(fileattr.filename)
        print(filelist)
        return filelist

    def getFile(self,localdir,filename):
        print('TEst',localdir+'/'+filename,self._path+'/'+filename)
        self._sftp.get(self._path+'/'+filename,localdir+'/'+filename)

        return localdir+'/'+filename

class remoteold(object):

    def __init__(self,cfg_server,tempdir,log):
        print('config',cfg_server)
        self._cfg_server = cfg_server
        self._tempdir = tempdir
        self._log = log

        self._processList = {}
        self._dataStore = {}
   #     self._remoteSSH = remoteSSH(config)



    def lookupfile(self):
       # data = self._dataStore
      #  print('before',self._dataStore)
        dictKeys = list(self._dataStore)
       # print('keys',list(self._dataStore))
        for key in dictKeys:
            value = self._dataStore[key]
        #    print('lookup',key,value)
            processID = self._dataStore[key]['PROCESS-ID']
            if processID.chdir(self._cfg_server[key]['PATH']):
                fileName,fileDate = processID.getlatestFile(self._cfg_server[key]['FILE_FILTER'])
         #       print('filelist, date', fileName,fileDate)

                if fileName is not None:
                    self._dataStore[key]['FILEDATE'] = fileDate
                    self._dataStore[key]['FILENAME'] = fileName
          #          print('self._dataStore',self._dataStore)
                else:
           #         print('delelet',key)
                    del self._dataStore[key]

            else:
            #    print('delete2',key)
                del self._dataStore[key]

        return True

    def latestFile(self):
        timeStampTemp = 0
        latest = None
        for key, value in self._dataStore.items():
            timeStamp = value.get('FILEDATE')
            if timeStampTemp < timeStamp:
                timeStampTemp = timeStamp
                latest = key
        self._log.debug('File with the latest timestamp %s', latest)
        return latest

    def getFile(self,id):
        print(id)
        processID=self._dataStore[id]['PROCESS-ID']
        filename = processID.getFile(self._tempdir,self._dataStore[id]['FILENAME'])

    #    return self._dataStore[id]['FILENAME']
        self._log.debug('get filename %s',filename)
        return filename


    def collecetFile(self):
        filename = None
        if self.connect():
            print('connected')
            if self.lookupfile():
                id = self.latestFile()
                print('ID',id)
                filename = self.getFile(id)
        else:
            print('No Server found')

        return filename