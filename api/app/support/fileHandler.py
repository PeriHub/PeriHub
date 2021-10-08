import shutil
import filecmp
import paramiko
import os

class fileHandler(object):
    
    def getRemoteModelPath(Cluster, username, ModelName):
        
        if Cluster=='FA-Cluster':
            remotepath = './Peridigm/apiModels/' + os.path.join(username, ModelName)
        
        elif Cluster=='Cara':
            remotepath = './PeridigmJobs/apiModels/' + os.path.join(username, ModelName)
        return remotepath

    def getRemoteUserPath(Cluster, username):
        
        if Cluster=='FA-Cluster':
            remotepath = './Peridigm/apiModels/' + username
        
        elif Cluster=='Cara':
            remotepath = './PeridigmJobs/apiModels/' + username
        return remotepath

    def getUserPath(Cluster, username, ModelName):
        
        if Cluster=='FA-Cluster':
            userpath = './Peridigm/apiModels/' + username
        
        elif Cluster=='Cara':
            userpath = './PeridigmJobs/apiModels/' + username
        return userpath

    def copyResultsFromCluster(username, ModelName, Cluster, allData):
        resultpath = './Results/' + os.path.join(username, ModelName)
        if not os.path.exists(resultpath):
            os.makedirs(resultpath)

        if Cluster=='None':
            remotepath = './peridigmJobs/' + os.path.join(username, ModelName)
            for root, dirs, files in os.walk(remotepath):
                if len(files)==0:
                    return ModelName + ' has not been created yet'

                for filename in files:
                    if(allData or '.e' in filename):
                        if(os.path.exists(os.path.join(resultpath, filename))):
                            if(filecmp.cmp(os.path.join(remotepath, filename),os.path.join(resultpath, filename))==False):
                                shutil.copy(os.path.join(remotepath, filename), os.path.join(resultpath,filename))
                        else:
                            shutil.copy(os.path.join(remotepath, filename), os.path.join(resultpath,filename))
                    # os.chmod(os.path.join(remotepath,name), 0o0777)
                    # os.chown(os.path.join(remotepath,name), 'test')
            # return ModelName + ' has been copied'

        else:
            remotepath = fileHandler.getRemoteModelPath(Cluster, username, ModelName)
            ssh, sftp = fileHandler.sftpToCluster(Cluster, username)
            
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
            sftp.close()
            ssh.close()
            # return ModelName + ' has been copied'

    def sftpToCluster(Cluster, username):
        
        if Cluster=='FA-Cluster':
            username='hess_ja'
            server='129.247.54.37'
            keypath = 'id_rsa_cluster'
        
        elif Cluster=='Cara':
            username='hess_ja'
            server='cara.dlr.de'
            keypath = 'id_rsa_cara'

        ssh = paramiko.SSHClient() 
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server, username=username, allow_agent=False, key_filename=keypath)
        sftp = ssh.open_sftp()
        return ssh, sftp

    def sshToCluster(Cluster, username):
        
        if Cluster=='FA-Cluster':
            username='hess_ja'
            server='129.247.54.37'
            keypath = 'id_rsa_cluster'
        
        elif Cluster=='Cara':
            username='hess_ja'
            server='cara.dlr.de'
            keypath = 'id_rsa_cara'

        ssh = paramiko.SSHClient() 
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server, username=username, allow_agent=False, key_filename=keypath)
        return ssh
