import shutil
import filecmp
import paramiko
import os
import time
import jwt
import json

class fileHandler(object):

    def getRemotePath(Cluster):
        
        return './PeridigmJobs/apiModels/'
    
    def getRemoteModelPath(Cluster, username, ModelName):
        
        return './PeridigmJobs/apiModels/' + username + '/' + ModelName

    def getRemoteUmatPath(Cluster):
        
        if Cluster=='None':
            return '/Peridigm/src/materials/umats/'
        return './Peridigm/src/src/materials/umats/'

    def getRemoteUserPath(Cluster, username):
        
        return './PeridigmJobs/apiModels/' + username

    def getUserPath(Cluster, username, ModelName):
        
        return './PeridigmJobs/apiModels/' + username

    def getUserName(request):
        encodedToken = request.headers.get('Authorization')
        if encodedToken == None or encodedToken == '':
            return 'guest'

        decodedToken = jwt.decode(encodedToken.split(' ')[1], options={"verify_signature": False})

        return decodedToken['preferred_username']

    def getMaxNodes(username):
        
        f = open('./support/allowedMaxNodes.json')
        data = json.load(f)
        
        if data[username]:
            return data[username]['allowedNodes']
        
        else:
            return data['guest']['allowedNodes']

    def getMaxFeSize(username):
        
        f = open('./support/allowedMaxNodes.json')
        data = json.load(f)
        
        if data[username]:
            return data[username]['allowedFeSize']
        
        else:
            return data['guest']['allowedFeSize']


    def getUserMail(request):
        encodedToken = request.headers.get('Authorization')
        if encodedToken == None or encodedToken == '':
            return ''

        decodedToken = jwt.decode(encodedToken.split(' ')[1], options={"verify_signature": False})

        return decodedToken['email']

    def removeFolderIfOlder(path, days, recursive):
        
        now = time.time()
        names = []
        for foldername in os.listdir(path):
            
            folderPath =os.path.join(path, foldername)

            if os.path.getmtime(folderPath) < now - days * 86400:
                names.append(foldername)
                shutil.rmtree(folderPath)
            else:
                if recursive:
                    for subfoldername in os.listdir(folderPath):
                        if os.path.getmtime(os.path.join(folderPath, subfoldername)) < now - days * 86400:
                            names.append(os.path.join(foldername, subfoldername))
                            shutil.rmtree(os.path.join(folderPath, subfoldername))
        return names

    def removeFolderIfOlderSftp(sftp, path, days, recursive):
        
        now = time.time()
        for foldername in sftp.listdir(path):
            
            folderPath = os.path.join(path, foldername)

            if os.path.getmtime(folderPath) < now - days * 86400:
                fileHandler.removeAllFolderSftp(sftp, folderPath, True)
            else:
                if recursive:
                    for subfoldername in sftp.listdir(folderPath):
                        if os.path.getmtime(os.path.join(folderPath, subfoldername)) < now - days * 86400:
                            fileHandler.removeAllFolderSftp(sftp, os.path.join(folderPath, subfoldername), True)

    def removeAllFolderSftp(sftp, remotepath, recursive):

        for filename in sftp.listdir(remotepath):
            for subfilename in sftp.listdir(os.path.join(remotepath, filename)):
                if recursive:
                    for subSubfilename in sftp.listdir(os.path.join(remotepath, subfilename)):
                        sftp.remove(os.path.join(remotepath, subSubfilename))
                sftp.remove(os.path.join(remotepath, subfilename))
            sftp.remove(os.path.join(remotepath, filename))
        sftp.rmdir(remotepath)


    def copyModelToCluster(username, ModelName, Cluster):
        
        if Cluster=='None':
            localpath = './Output/' + os.path.join(username, ModelName)
            remotepath = './peridigmJobs/' + os.path.join(username, ModelName)
            if not os.path.exists(remotepath):
                os.makedirs(remotepath)
                # os.chown(remotepath, 'test')
            if not os.path.exists(localpath):
                return ModelName + ' has not been created yet'
            for root, dirs, files in os.walk(localpath):
                if len(files)==0:
                    return ModelName + ' has not been created yet'
                inputExist = False
                meshExist = False
                for name in files:
                    if name.split('.')[-1]=='yaml':
                        inputExist = True
                    if name.split('.')[-1]=='txt' or name.split('.')[-1]=='e' or name.split('.')[-1]=='g' :
                        meshExist = True

                if inputExist==False:
                    return 'Inputfile of ' + ModelName + ' has not been created yet'

                if meshExist==False:
                    return 'Meshfile of ' + ModelName + ' has not been created yet'

                for name in files:
                    shutil.copy(os.path.join(root,name), os.path.join(remotepath,name))
                    # os.chmod(os.path.join(remotepath,name), 0o0777)
                    # os.chown(os.path.join(remotepath,name), 'test')
            return 'Success'

        else:       
            
            localpath = './Output/' + os.path.join(username, ModelName)
            remotepath = fileHandler.getRemoteModelPath(Cluster, username, ModelName)
            userpath = fileHandler.getUserPath(Cluster, username, ModelName) 
            ssh, sftp = fileHandler.sftpToCluster(Cluster)

            try:
                sftp.chdir(userpath) 
            except FileNotFoundError:
                sftp.mkdir(userpath)
                sftp.chdir(userpath)

            try:
                sftp.chdir(ModelName)  # Test if remote_path exists
            except FileNotFoundError:
                sftp.mkdir(ModelName)  # Create remote_path
                sftp.chdir(ModelName)
            if not os.path.exists(localpath):
                return ModelName + ' has not been created yet'
            for root, dirs, files in os.walk(localpath):
                if len(files)==0:
                    return ModelName + ' has not been created yet'
                inputExist = False
                meshExist = False
                for name in files:
                    if name.split('.')[-1]=='yaml':
                        inputExist = True
                    if name.split('.')[-1]=='txt' or name.split('.')[-1]=='e':
                        meshExist = True

                if inputExist==False:
                    return 'Inputfile of ' + ModelName + ' has not been created yet'

                if meshExist==False:
                    return 'Meshfile of ' + ModelName + ' has not been created yet'

                for name in files:
                    sftp.put(os.path.join(root,name), name)

            sftp.close()
            ssh.close()
            
            return 'Success'

    def copyLibToCluster(username, ModelName, Cluster):
        
        localpath = './Output/' + os.path.join(username, ModelName)
        remotepath = fileHandler.getRemoteUmatPath(Cluster)
        try:
            ssh, sftp = fileHandler.sftpToCluster(Cluster)
        except:
            return "ssh connection to " + Cluster + " failed!"

        if not os.path.exists(localpath):
            return 'Shared libray can not been found'
        for root, dirs, files in os.walk(localpath):
            if len(files)==0:
                return 'Shared libray can not been found'
            for name in files:
                if name.split('.')[-1]=='so':
                    sftp.put(os.path.join(root,name), os.path.join(remotepath,name))
                    return 'Success'

        sftp.close()
        ssh.close()
        
        return 'Shared libray can not been found'

    def copyFileToFromPeridigmContainer(username, ModelName, Filename, ToOrFrom):
        
        localpath = './Output/' + os.path.join(username, ModelName)
        remotepath = './peridigmJobs/' + os.path.join(username, ModelName)
        if not os.path.exists(remotepath):
            os.makedirs(remotepath)
            # os.chown(remotepath, 'test')
        if not os.path.exists(localpath):
            return ModelName + ' has not been created yet'

        try:
            if ToOrFrom:
                shutil.copy(os.path.join(localpath,Filename), os.path.join(remotepath,Filename))
            else:
                shutil.copy(os.path.join(remotepath,Filename), os.path.join(localpath,Filename))
        except:
            return 'File not found'

        return 'Success'

    def copyResultsFromCluster(username, ModelName, Cluster, allData):
        resultpath = './Results/' + os.path.join(username, ModelName)
        if not os.path.exists(resultpath):
            os.makedirs(resultpath)

        if Cluster=='None':
            remotepath = './peridigmJobs/' + os.path.join(username, ModelName)
            for root, dirs, files in os.walk(remotepath):
                if len(files)==0:
                    return False

                for filename in files:
                    if(allData or '.e' in filename):
                        if(os.path.exists(os.path.join(resultpath, filename))):
                            if(filecmp.cmp(os.path.join(remotepath, filename),os.path.join(resultpath, filename))==False):
                                shutil.copy(os.path.join(remotepath, filename), os.path.join(resultpath,filename))
                        else:
                            shutil.copy(os.path.join(remotepath, filename), os.path.join(resultpath,filename))
                    # os.chmod(os.path.join(remotepath,name), 0o0777)
                    # os.chown(os.path.join(remotepath,name), 'test')
            return True

        else:
            remotepath = fileHandler.getRemoteModelPath(Cluster, username, ModelName)
            ssh, sftp = fileHandler.sftpToCluster(Cluster)
            try:
                for filename in sftp.listdir(remotepath):
                    if(allData or '.e' in filename):
                        if(os.path.exists(os.path.join(resultpath, filename))):
                            remoteInfo = sftp.stat(os.path.join(remotepath, filename))
                            remoteSize = remoteInfo.st_size
                            localSize = os.path.getsize(os.path.join(resultpath, filename))
                            print('compare ' + filename + ' remoteSize: ' + remoteSize + ', localsize: ' + localSize)
                            if(abs(remoteSize-localSize)>5):
                                sftp.get(os.path.join(remotepath, filename), os.path.join(resultpath, filename))
                        else:
                            sftp.get(os.path.join(remotepath, filename), os.path.join(resultpath, filename))
            except:
                return False
            sftp.close()
            ssh.close()
            return True

    def sftpToCluster(Cluster):

        ssh = paramiko.SSHClient() 
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        if Cluster=='FA-Cluster':
            username='f_peridi'
            server='129.247.54.37'
            keypath = './rsaFiles/id_rsa_cluster'
            try:
                ssh.connect(server, username=username, allow_agent=False, key_filename=keypath)
            except:
                return "ssh connection to " + server + " failed!"
        
        elif Cluster=='Cara':
            username='f_peridi'
            server='cara.dlr.de'
            keypath = './rsaFiles/id_rsa_cara'
            try:
                ssh.connect(server, username=username, allow_agent=False, key_filename=keypath)
            except:
                return "ssh connection to " + server + " failed!"
        
        elif Cluster=='None':
            username='root'
            server='perihub_peridigm'
            try:
                ssh.connect(server, username=username, allow_agent=False, password='root')
            except:
                return "ssh connection to " + server + " failed!"

        sftp = ssh.open_sftp()
        return ssh, sftp

    def sshToCluster(Cluster):
        
        if Cluster=='FA-Cluster':
            username='f_peridi'
            server='129.247.54.37'
            keypath = './rsaFiles/id_rsa_cluster'
        
        elif Cluster=='Cara':
            username='f_peridi'
            server='cara.dlr.de'
            keypath = './rsaFiles/id_rsa_cara'

        ssh = paramiko.SSHClient() 
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(server, username=username, allow_agent=False, key_filename=keypath)
        except:
            return "ssh connection to " + server + " failed!"
        return ssh
