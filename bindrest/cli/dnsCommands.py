# -*- coding: utf-8 -*-
#Elliann Marks
#elian.markes@gmail.com
#

#Bibliotecas
import dns.update
import dns.query
import dns.resolver
import re
import os
from moduleLog import logInfo
from moduleLog import logWarn
from moduleLog import logError
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.executor.playbook_executor import PlaybookExecutor

#Variaveis default
zoneDefault = "tjmt.jus.br" #"example.com"
ttlDefault = 300
dnsInterno = "10.0.16.239" #"1.1.1.1"
dnsExterno = "172.16.1.242" #"2.2.2.2"
dnsGoogle = "8.8.8.8"
domain = ".tjmt.jus.br" #".example.com.br"
reversoInternoIP = "10.0.16.176" #"3.3.3.3"
reversoInterno = "http-nlb-14" #"CNAME_REV_INT"
reversoExterno = "http-nlb-13" #"CNAME_REV_EXT"
directoryInfo = "/usr/local/nginx/conf/includes" #"/path/nginxConfs"
typeRegistry = "CNAME"
regexInfo = "server [0-9]+.[0-9]+.[0-9]+.[0-9]+:[0-9]+;|server [0-9]+.[0-9]+.[0-9]+.[0-9]+;"

#Variaveis ansible
loader = DataLoader()
inventory = InventoryManager(loader=loader, sources='/etc/ansible/production/hosts')
variableManager = VariableManager(loader=loader, inventory=inventory)
playbookPath = '/etc/ansible/playbooks/reversoAPI.yml'
playbookPathDNS = '/etc/ansible/playbooks/rndcDNS.yml'
passwords = {}
viewInternalDNS = "internal"
viewReversoapiDNS = "reversoapi"

#Options para execucao do ansible
Options = namedtuple('Options', ['listtags', 'listtasks', 'listhosts', 'syntax', 'connection','module_path', 'forks',\
'remote_user', 'private_key_file', 'ssh_common_args', 'ssh_extra_args', 'sftp_extra_args', 'scp_extra_args', 'become',\
'become_method', 'become_user', 'verbosity', 'check','diff'])
options = Options(listtags=False, listtasks=False, listhosts=False, syntax=False, connection='ssh', module_path=None,\
forks=10, remote_user='ansible', private_key_file='/etc/keys/chave_ansible.pem', ssh_common_args=None, ssh_extra_args=None,\
sftp_extra_args=None, scp_extra_args=None, become=True, become_method='sudo', become_user='root', verbosity=None, check=False, diff=False)

def ansiblePlaybook(environment, nameDomain, confReversoHost, nameUser, remove_backend=None, reload_reverse=None, with_ssl=False):
    try:
        if confReversoHost != None:
            variableManager.extra_vars = { 'backends' : confReversoHost, 'backend_name' : nameDomain, 'reverse_environment' : environment, 'remove_backend' : remove_backend, 'reload_reverse' : reload_reverse, 'with_ssl' : with_ssl }
        else:
            variableManager.extra_vars = { 'backend_name' : nameDomain, 'reverse_environment' : environment, 'remove_backend' : remove_backend, 'reload_reverse' : reload_reverse, 'with_ssl' : with_ssl }
        executorAnsible = PlaybookExecutor(playbooks=[playbookPath], inventory=inventory, variable_manager=variableManager, loader=loader, options=options, passwords=passwords)
        executorAnsible.run()
        return True

    except Exception as er:
        logError(str(er))
        return False

def ansiblePlaybookDNS(viewDNS, serverDNS):
    try:
        variableManager.extra_vars = { 'serverDNS': serverDNS, 'viewDNS' : viewDNS }
        executorAnsible = PlaybookExecutor(playbooks=[playbookPathDNS], inventory=inventory, variable_manager=variableManager, loader=loader, options=options, passwords=passwords)
        executorAnsible.run()
        return True

    except Exception as er:
        logError(str(er))
        return False

def pullCacheConfs():
    os.system('/bin/git --work-tree=/usr/local/nginx/conf/includes/externo --git-dir=/usr/local/nginx/conf/includes/externo/.git pull -u origin master')
    os.system('/bin/git --work-tree=/usr/local/nginx/conf/includes/interno --git-dir=/usr/local/nginx/conf/includes/interno/.git pull -u origin master')

def reverseReload(nameUser):
    try:
        if (ansiblePlaybook(None, None, None, nameUser, None, True, None)):
            logInfo("reversereload | User-%s" % (nameUser))
            pullCacheConfs()
            return ["reversereload | User-%s" % (nameUser), True]
        else:
            logError("reversereload | User-%s" % (nameUser))
            return ["reversereload | User-%s" % (nameUser), False]

    except Exception as er:
        logError(str(er))
        return [str(er), False]

def create(environmentTemp, nameDomainTemp, nameUser, confReversoHost):
    try:
        environment = environmentTemp.lower()
        nameDomain = nameDomainTemp.lower()
        createDNS = dns.update.Update(zoneDefault)
        if environment == "interno":
            if not verify(nameDomain, "interno"):
                createDNS.add(nameDomain, ttlDefault, typeRegistry, reversoInterno)
                responseCreate = dns.query.tcp(createDNS, dnsInterno)
                if "NOERROR" in responseCreate.to_text():
                    if ansiblePlaybookDNS(viewInternalDNS, "dns_interno"):
                        if (ansiblePlaybook(environment, nameDomain, confReversoHost, nameUser, False)):
                            logInfo("dnscreate - DNS/reverse %s create | User-%s" % (nameDomain, nameUser))
                            pullCacheConfs()
                            return ["dnscreate - DNS/reverse %s create | User-%s" % (nameDomain, nameUser), True]
                        else:
                            logError("dnscreate - DNS %s create and FAIL conf reverse | User-%s" % (nameDomain, nameUser))
                            return ["dnscreate - DNS %s create and FAIL conf reverse | User-%s" % (nameDomain, nameUser), False]
                    else:
                        logError("dnscreate - DNS %s create and FAIL rndc interno | User-%s" % (nameDomain, nameUser))
                        return ["dnscreate - DNS %s create and FAIL rndc interno | User-%s" % (nameDomain, nameUser), False]
                elif "NXRRSET" in responseCreate.to_text():
                    logError("dnscreate - DNS interno %s fail in create | User-%s" % (nameDomain, nameUser))
                    return ["dnscreate - DNS interno %s fail in create | User-%s" % (nameDomain, nameUser), False]
                else:
                    logError(str(responseCreate.to_text()))
                    return [str(responseCreate.to_text()), False]
            else:
                logError("dnscreate - DNS interno %s exist | User-%s" %(nameDomain, nameUser))
                return ["dnscreate - DNS interno %s exist | User-%s" %(nameDomain, nameUser), False]

        elif environment == "externo":
            logError("13")
            if not verify(nameDomain, "externo"):
                createDNS.add(nameDomain, ttlDefault, typeRegistry, reversoExterno)
                responseCreate = dns.query.tcp(createDNS, dnsExterno)
                if "NOERROR" in responseCreate.to_text():
                    if ansiblePlaybookDNS(viewReversoapiDNS, "dns_externo"):
                        createDNS.add(nameDomain, ttlDefault, typeRegistry, reversoInterno)
                        responseCreate = dns.query.tcp(createDNS, dnsInterno)
                        if "NOERROR" in responseCreate.to_text():
                            if ansiblePlaybookDNS(viewInternalDNS, "dns_interno"):
                                if (ansiblePlaybook(environment, nameDomain, confReversoHost, nameUser, False)):
                                    logInfo("dnscreate - DNS/reverse %s create | User-%s" % (nameDomain, nameUser))
                                    pullCacheConfs()
                                    return ["dnscreate - DNS/reverse %s create | User-%s" % (nameDomain, nameUser), True]
                                else:
                                    logError("dnscreate - DNS %s create and FAIL conf reverse | User-%s" % (nameDomain, nameUser))
                                    return ["dnscreate - DNS %s create and FAIL conf reverse | User-%s" % (nameDomain, nameUser), False]
                            else:
                                logError("dnscreate - DNS %s create and FAIL rndc interno | User-%s" % (nameDomain, nameUser))
                                return ["dnscreate - DNS %s create and FAIL rndc interno | User-%s" % (nameDomain, nameUser),False]
                        elif "NXRRSET" in responseCreate.to_text():
                            logError("dnscreate - DNS interno %s fail in create | User-%s" % (nameDomain, nameUser))
                            return ["dnscreate - DNS interno %s fail in create | User-%s" % (nameDomain, nameUser), False]
                        else:
                            logError(str(responseCreate.to_text()))
                            return [str(responseCreate.to_text()), False]
                    else:
                        logError("dnscreate - DNS %s create and FAIL rndc externo | User-%s" % (nameDomain, nameUser))
                        return ["dnscreate - DNS %s create and FAIL rndc externo | User-%s" % (nameDomain, nameUser), False]
                elif "NXRRSET" in responseCreate.to_text():
                    logError("dnscreate - DNS externo %s fail in create | User-%s" %(nameDomain, nameUser))
                    return ["dnscreate - DNS externo %s fail in create | User-%s" %(nameDomain, nameUser), False]
                else:
                    logError(str(responseCreate.to_text()))
                    return [str(responseCreate.to_text()), False]
            else:
                logError("dnscreate - DNS externo %s exist | User-%s" %(nameDomain, nameUser))
                return ["dnscreate - DNS externo %s exist | User-%s" %(nameDomain, nameUser), False]
    
    except Exception as er:
        logError(str(er))
        return [str(er), False]

def delete(nameDomainTemp, nameUser):
    try:
        verifyDelete = False
        nameDomain = nameDomainTemp.lower()
        deleteDNS = dns.update.Update(zoneDefault)
        deleteDNS.delete(nameDomain)
        if verify(nameDomain, "interno"):
            try:
                responseDelete = dns.query.tcp(deleteDNS, dnsInterno)
            except:
                pass
            if "NOERROR" in responseDelete.to_text():
                if ansiblePlaybookDNS(viewInternalDNS, "dns_interno"):
                    if (ansiblePlaybook("interno", nameDomain, None, nameUser, True, None, None)):
                        logInfo("dnsdelete - DNS %s delete interno - User-%s" %(nameDomain, nameUser))
                        verifyDelete = True
                    else:
                        logError("dnsdelete - DNS %s deleted and FAIL in delete conf reverse | User-%s" %(nameDomain, nameUser))
                else:
                    logError("dnsdelete - DNS %s delete and FAIL rndc interno | User-%s" % (nameDomain, nameUser))
            else:
                logError("dnsdelete - DNS interno %s fail in delete | User-%s" %(nameDomain, nameUser))
        else:
            logError("dnsdelete - DNS interno %s not exist | User-%s" %(nameDomain, nameUser))

        if verify(nameDomain, "externo"):
            try:
                responseDelete = dns.query.tcp(deleteDNS, dnsExterno)
            except:
                pass
            if "NOERROR" in responseDelete.to_text():
                if ansiblePlaybookDNS(viewReversoapiDNS, "dns_externo"):
                    if (ansiblePlaybook("externo", nameDomain, None, nameUser, True, None, None)):
                        logInfo("dnsdelete - DNS %s delete externo - User-%s" %(nameDomain, nameUser))
                        verifyDelete = True
                    else:
                        logError("dnsdelete - DNS %s deleted and FAIL in delete conf reverse | User-%s" %(nameDomain, nameUser))
                else:
                    logError("dnsdelete - DNS %s delete and FAIL rndc externo | User-%s" % (nameDomain, nameUser))
            else:
                logError("dnsdelete - DNS externo %s fail in delete | User-%s" %(nameDomain, nameUser))
        else:
            logError("dnsdelete - DNS externo %s not exist | User-%s" %(nameDomain, nameUser))

        if verifyDelete:
            pullCacheConfs()
            return ["dnsdelete - DNS %s delete - User-%s" % (nameDomain, nameUser), True]
        else:
            return ["dnsdelete - DNS %s fail in delete | User-%s" % (nameDomain, nameUser), False]

    except Exception as er:
        logError(str(er))
        return [str(er), False]

def info(nameDomainTemp, nameUser):
    try:
        nameDomain = nameDomainTemp.lower()
        infoDNS = dns.resolver.Resolver()
        infoDNS.nameservers = [dnsInterno]
        responseInfo = infoDNS.query(nameDomain + domain)
        resolveDNS = str(responseInfo.rrset.to_text()).split(" ")[4]
        logInfo("dnsinfo - DNS %s info | User-%s" %(nameDomain, nameUser))
        publicado = "internal"
        if resolveDNS == reversoInternoIP:
            pathFile = directoryInfo + "/" + "interno" + "/" + "interno_includes"
            joinFilePath = os.path.join(pathFile, nameDomain + ".conf")
            logError(joinFilePath)
            if not os.path.isfile(joinFilePath):
                pathFile = directoryInfo + "/" + "externo/" + "externo_includes"
                joinFilePath = os.path.join(pathFile, nameDomain + ".conf")
                logError(joinFilePath)
                publicado = "public"
                if not os.path.isfile(joinFilePath):
                    logError("Configuration file not found")
                    return ["Configuration file not found", False, None]
            fileOpen = open(joinFilePath, "rt")
            fileText = fileOpen.read()
            fileOpen.close()
            resultList = re.findall(regexInfo, fileText)
            if len(resultList) >= 1:
                result = list()
                for resultTemp in resultList:
                    result.append(resultTemp.replace(";", "").replace("server ", ""))
                return [result, True, publicado]
            else:
                logError("dnsinfo - DNS %s not exist | User-%s" %(nameDomain, nameUser))
                return ["dnsinfo - DNS %s not exist | User-%s" %(nameDomain, nameUser), False, None]
        else:
            publicado = "direct"
            return [[resolveDNS], True, publicado]

    except Exception as er:
        logError(str(er))
        return [str(er), False, None]

def verify(nameDomainTemp, typeDNSTemp):
    try:
        typeDNS = typeDNSTemp.lower()
        nameDomain = nameDomainTemp.lower()
        if typeDNS == "interno":
            verifyDNS = dns.resolver.Resolver()
            verifyDNS.nameservers = [dnsInterno]
            verifyDNS.query(nameDomain + domain)
            return True
        elif typeDNS == "externo":
            verifyDNS = dns.resolver.Resolver()
            verifyDNS.nameservers = [dnsGoogle]
            verifyDNS.query(nameDomain + domain)
            return True

    except Exception:
        if typeDNS == "interno":
            pathFile = directoryInfo + "/" + "interno" + "/" + "interno_includes"
            joinFilePath = os.path.join(pathFile, nameDomain + ".conf")
            if not os.path.isfile(joinFilePath):
                return False
            else:
                return True
        if typeDNS == "externo":
            pathFile = directoryInfo + "/" + "externo/" + "externo_includes"
            joinFilePath = os.path.join(pathFile, nameDomain + ".conf")
            if not os.path.isfile(joinFilePath):
                return False
            else:
                return True
        else:
            return True
