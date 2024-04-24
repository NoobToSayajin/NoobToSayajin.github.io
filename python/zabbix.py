import logs, datetime,logging
from logging.handlers import TimedRotatingFileHandler
from pyzabbix import ZabbixAPI
from dotenv import load_dotenv
from os import getenv, environ

class Zabbix:
    load_dotenv("C:\\Scripts\\ENV_GIT_Main\\.env")
    # load_dotenv("C:\\Users\\MERIELJ\\Desktop\\Stage_2024\\ENV_GIT\\ENV_GIT_Main - Copie (2)\\.env")
    TODAY: str = datetime.date.today().strftime("%Y-%m-%d")
    CISCO_IOS_USER: str | None = getenv("CISCO_IOS_USER") if not environ.get("CISCO_IOS_USER") else environ.get("CISCO_IOS_USER")
    CISCO_IOS_PASS: str | None = getenv("CISCO_IOS_PASS") if not environ.get("CISCO_IOS_PASS") else environ.get("CISCO_IOS_PASS")
    CISCO_IOS_SECRET: str | None = getenv("CISCO_IOS_SECRET") if not environ.get("CISCO_IOS_SECRET") else environ.get("CISCO_IOS_SECRET")
    TELNET_USER: str | None = getenv("TELNET_USER") if not environ.get("TELNET_USER") else environ.get("TELNET_USER")
    TELNET_PASS: str | None = getenv("TELNET_PASS") if not environ.get("TELNET_PASS") else environ.get("TELNET_PASS")
    DELAY: str | None = getenv("DELAY")
    INTERVAL: str | None = getenv("INTERVAL")
    ITEM_AGE: str | None = getenv("ITEM_AGE")
    ITEM_SIZE: str | None = getenv("ITEM_SIZE")
    TRIGGER_PRIORITY: int | None = int(getenv("TRIGGER_PRIORITY"))
    LOG_DIR: str | None = getenv("LOG_DIR")
    LOG_LEVEL: str | None = getenv("LOG_LEVEL")
    STREAM_HANDLER: str | None = getenv("STREAM_HANDLER")
    LOG_FILE: str | None = LOG_DIR+"\\.log" if LOG_LEVEL else None

    logLevel: dict = {
        "DEBUG":logging.DEBUG,
        "INFO":logging.INFO,
        "WARNING":logging.WARNING,
        "ERROR":logging.ERROR,
        "CRITICAL":logging.CRITICAL
    }

    triggerPriority: dict = {
        0:"Non-classe",
        1:"Information",
        2:"Avertissement",
        3:"Moyen",
        4:"Haut",
        5:"Desastre"
    }

    logger_zabbix = logging.getLogger(__name__)
    logger_zabbix.setLevel(logLevel[LOG_LEVEL])

    formater_zabbix = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:ligne_%(lineno)d -> %(message)s')

    file_handler_zabbix = TimedRotatingFileHandler(
        filename=LOG_FILE, # type: ignore
        when='H',
        interval=24,
        backupCount=5,
        encoding='utf-8'
    )
    file_handler_zabbix.setFormatter(formater_zabbix)
    file_handler_zabbix.setLevel(logLevel[LOG_LEVEL])

    stream_handler_zabbix = logging.StreamHandler()
    stream_handler_zabbix.setFormatter(formater_zabbix)

    logger_zabbix.addHandler(file_handler_zabbix)
    logger_zabbix.addHandler(stream_handler_zabbix) if STREAM_HANDLER.lower() == 'true' else ...
    
    SWITCHID: dict={
        "Switchs":22,
        "Routers":23,
        "pyZabbixGitFileGroup": 24
    }
    os: dict = {
        29:"aruba_os",
        30:"avaya_ers"
    }

    tagList: dict = {
        'connexion_type': 'telnet',
        'device_type': 'avaya_ers'
    }

    def __init__(self, ip: str, token: str) -> None:
        self.ip: str = ip
        self.token: str = token
        self.api: ZabbixAPI
        self.diconnect: list = []
        self.passBis: list = []
        # Zabbix.logger_zabbix.debug(f"Creation: {self}")
    
    def __str__(self) -> str:
        return f"Serveur Zabbix: {self.ip:>15}"
    
    def __del__(self) -> None:
        # Zabbix.logger_zabbix.debug(f"Destruction: {self}")
        pass
    
    @property
    def Disconnect(self) -> list:
        return self.diconnect
    
    @Disconnect.setter
    def Disconnect(self, swLst: list) -> None:
        Zabbix.logger_zabbix.info(f"Disconnect List set")
        Zabbix.logger_zabbix.debug(f"{swLst}")
        self.diconnect = swLst

    @property
    def PassBis(self) -> list:
        return self.passBis
    
    @PassBis.setter
    def PassBis(self, bisLst: list) -> None:
        Zabbix.logger_zabbix.info(f"PassBis List set")
        Zabbix.logger_zabbix.debug(f"{bisLst}")
        self.passBis = bisLst

    @logs.Timer
    def connexion(self) -> None:
        self.api = ZabbixAPI(self.ip)
        Zabbix.logger_zabbix.info(f"Connexion: {self}")
        self.api.login(api_token=self.token)

    def GetGroup(self) -> dict:
        groupe: dict = {}

        group = self.api.host.get(selectGroups='extend')
        for grp in group:
            for g in grp["groups"]:
                if not g['groupid'] in groupe.keys() and not int(g['groupid']) in Zabbix.SWITCHID.values():
                    groupe[g['name']]=int(g['groupid'])
        return groupe

    def GetTag(self, seek: str= None, hostname: str = None) -> dict:
        tags: dict = {}
        hosts = self.api.host.get(selectTags='extend')
        if hostname:
            for host in hosts:
                if host['host'] == hostname:
                    tag: dict = {}
                    if 0 < len(host["tags"]):
                        for g in host["tags"]:
                            if g['tag'].lower()==seek.lower():
                                return g['value']
        else:
            for host in hosts:
                tag: dict = {}
                if 0 < len(host["tags"]):
                    for g in host["tags"]:
                        if not seek:
                            Zabbix.logger_zabbix.debug(f"Get all tag")
                            tag.update({g['tag']:g['value']})
                            tags.update({host['host']:tag})
                        else:
                            if g['tag'].lower()==seek:
                                return g['value']
        return tags
    

    """
      _____      _    _____         _ _       _     
     / ____|    | |  / ____|       (_) |     | |    
    | |  __  ___| |_| (_____      ___| |_ ___| |__  
    | | |_ |/ _ \ __|\___ \ \ /\ / / | __/ __| '_ \ 
    | |__| |  __/ |_ ____) \ V  V /| | || (__| | | |
     \_____|\___|\__|_____/ \_/\_/ |_|\__\___|_| |_|
                                                    
    """

    @logs.Timer
    def GetCisco(self, filelog: bool) -> tuple:
        """ssh, name, group, ip, username, device_type"""
        Zabbix.logger_zabbix.debug(f"Recherche de switch: Switchs, cisco_ios")
        hostlst: list =[]
        log: list =[]
        grp: str | None = None
        hostsgrp = self.api.host.get(selectTags='extend', tags=[{"tag": "connexion_type", "value": "ssh"}, {"tag": "device_type", "value": "cisco_ios"}])
        for host in hostsgrp:
            inactive: bool = bool(self.GetTag("isActivate", host['host'])) if 0<len(self.GetTag("lieux", host['host'])) else False
            if inactive:
                Zabbix.logger_zabbix.info(f"{host['host']} est inactif")
                continue
            grp: str = self.GetTag("lieux", host['host']) if 0<len(self.GetTag("lieux", host['host'])) else "None"
            newpwd: bool = bool(self.GetTag("isNewPass", host['host'])) if 0<len(self.GetTag("lieux", host['host'])) else False
            pwd: str = Zabbix.CISCO_IOS_PASS_BIS if newpwd else Zabbix.CISCO_IOS_PASS
            cpwd: str = "CISCO_IOS_PASS_BIS" if newpwd else "CISCO_IOS_PASS"
            interfaces = self.api.hostinterface.get(hostids=[host["hostid"]])
            for intf in interfaces:
                h =["ssh",host['host'], grp,intf["ip"], Zabbix.CISCO_IOS_USER, pwd, "cisco_ios", Zabbix.CISCO_IOS_SECRET]
                if filelog:
                    h2 =["ssh",host['host'], grp,intf["ip"], "CISCO_IOS_USER", cpwd, "cisco_ios", "CISCO_IOS_SECRET"]
                    log.append(h2)
                hostlst.append(h)
        Zabbix.logger_zabbix.info(f"switchs, {len(hostlst):>5} cisco_ios trouves")
        return hostlst, log

    @logs.Timer
    def GetTelnet(self, filelog: bool) -> tuple:
        """ssh, name, group, ip, username, device_type"""
        Zabbix.logger_zabbix.debug(f"Recherche de switch: telnet")
        hostlst: list = []
        hostName: list = []
        log: list = []
        CRED: tuple = ()
        grp: str | None = None
        hostsgrp = self.api.host.get(selectTags='extend', tags=[{"tag": "connexion_type", "value": "telnet"}])
        for host in hostsgrp:
            device = self.GetTag("device_type", host['host'])
            if 0<len(self.diconnect):
                if host['host'] in self.diconnect[0]:
                    Zabbix.logger_zabbix.info(f"{host['host']} est dans la liste deconnecte")
                    continue
            if self.GetTag("device_type") == "avaya_ers":
                if 0<len(self.passBis):
                    if host['host'] in self.passBis[0]:
                        CRED = Zabbix.AVAYA_USER, Zabbix.AVAYA_PASS_BIS, "avaya_ers", "AVAYA_USER", "AVAYA_PASS_BIS"
                    else:
                        CRED = Zabbix.AVAYA_USER, Zabbix.AVAYA_PASS, "avaya_ers", "AVAYA_USER", "AVAYA_PASS"
                else:
                    CRED = Zabbix.AVAYA_USER, Zabbix.AVAYA_PASS, "avaya_ers", "AVAYA_USER", "AVAYA_PASS"
            elif self.GetTag("device_type") == "aruba_os":
                if 0<len(self.passBis):
                    if host['host'] in self.passBis[0]:
                        CRED = Zabbix.ARUBA_ERS_USER, Zabbix.ARUBA_ERS_PASS_BIS, "aruba_os", "ARUBA_ERS_USER", "ARUBA_ERS_PASS_BIS" 
                    else:
                        CRED = Zabbix.ARUBA_ERS_USER, Zabbix.ARUBA_ERS_PASS, "aruba_os", "ARUBA_ERS_USER", "ARUBA_ERS_PASS" 
                else:
                    CRED = Zabbix.ARUBA_ERS_USER, Zabbix.ARUBA_ERS_PASS, "aruba_os", "ARUBA_ERS_USER", "ARUBA_ERS_PASS" 
            grp = self.GetTag("lieux", host['host']) if 0<len(self.GetTag("lieux", host['host'])) else "None"
            interfaces = self.api.hostinterface.get(hostids=[host["hostid"]])
            for intf in interfaces:
                if host['host'] not in hostlst:
                    h =["telnet",host['host'], grp,intf["ip"], CRED[0], CRED[1], CRED[2]]
                    if filelog:
                        h2 =["telnet",host['host'], grp,intf["ip"], CRED[3], CRED[4], CRED[2]]
                        log.append(h2)
                    hostlst.append(h)
            if 0<len(hostlst):
                hostName.append(h[1])
        Zabbix.logger_zabbix.info(f"switchs telnet, {len(hostlst):>5} connexion telnet trouves")
        return hostlst, log

    """

     ██████╗██╗      █████╗ ███████╗███████╗    ███╗   ███╗ █████╗ ██╗███╗   ██╗
    ██╔════╝██║     ██╔══██╗██╔════╝██╔════╝    ████╗ ████║██╔══██╗██║████╗  ██║
    ██║     ██║     ███████║███████╗███████╗    ██╔████╔██║███████║██║██╔██╗ ██║
    ██║     ██║     ██╔══██║╚════██║╚════██║    ██║╚██╔╝██║██╔══██║██║██║╚██╗██║
    ╚██████╗███████╗██║  ██║███████║███████║    ██║ ╚═╝ ██║██║  ██║██║██║ ╚████║
     ╚═════╝╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝    ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝
                                                                                

    """

    @logs.Timer
    def main(self, FileLog: bool = False) -> list:
        telnet: list = []; tnlog: list | None
        ciscolst: list= []; cslog: list | None
        telnet, tnlog= self.GetTelnet(FileLog)
        ciscolst, cslog= self.GetCisco(FileLog)
        if FileLog:
            from os import path, makedirs
            import json
            swlst = [{"GroupList":self.GetGroup()},{"CISCO_IOS":cslog},{"telnet":tnlog}]
            doss = Zabbix.LOG_DIR+"\\"+Zabbix.TODAY+"\\SwitchList" # type: ignore
            d = doss+"\\"+datetime.datetime.now().strftime("%Hh%M")+"."+"ZabbixFileLogs.json"
            makedirs(doss) if not path.exists(doss) else ...
            Zabbix.logger_zabbix.debug(f"Sauvegarde ZabbixFileLog.json {d}")
            with open(d, "w") as f:
                json.dump(swlst, f, indent=4)
                f.close()

        return ciscolst+telnet
        # return huaweilst

    """
     _____            _                  _                     
    |  __ \          | |                | |                    
    | |  | | ___  ___| | __ _ _ __   ___| |__   ___ _   _ _ __ 
    | |  | |/ _ \/ __| |/ _` | '_ \ / __| '_ \ / _ \ | | | '__|
    | |__| |  __/ (__| | (_| | | | | (__| | | |  __/ |_| | |   
    |_____/ \___|\___|_|\__,_|_| |_|\___|_| |_|\___|\__,_|_|   
                                                                

    """

    @logs.Timer
    def Declancheur(self, name: str, file: str):
        def GetItems(items, itemsLst: list) -> list:
            for item in items:
                it = {item['name']:{item['itemid']}}
                itemsLst.append(it)
            return itemsLst
        
        def TriggerID(desc: str):
            triggers = self.api.trigger.get(output='extend', groupids=[67])
            trgLst= []
            for trigger in triggers:
                te = trigger['event_name']
                trgLst.append(te)
                if trigger['event_name'] == desc:
                    return trigger['triggerid']
            
        def ItemExist(host, name: str, item: str) -> None:
            itemExist: dict = {
                "hostid":host['hostid'],
                "name":"FileExits_"+name,
                "key_":"vfs.file.exists["+item+"]",
                "type":0,
                "value_type":3,
                "interfaceid":host["interfaces"][0]["interfaceid"],
                "delay":f"{Zabbix.DELAY};{Zabbix.INTERVAL}",
                # "delay":'1d;h9',
            }
            self.api.item.create(
                hostid=itemExist['hostid'],
                name=itemExist['name'],
                key_=itemExist['key_'],
                type=itemExist['type'],
                value_type=itemExist['value_type'],
                interfaceid=itemExist['interfaceid'],
                delay=itemExist['delay'],
            )
            Zabbix.logger_zabbix.debug(f"Creation de l'item {itemExist['name']}")
            triggerExist: dict = {
                "event_name":"FileExits_"+name,
                "description":"FileExits_"+name,
                "comments":"FileExits_"+name,
                "expression":"last(/"+host['host']+"/"+itemExist['key_']+")=0", "recovery_mode":1,
                "recovery_expression":"last(/"+host['host']+"/"+itemExist['key_']+")=1",
                "priority":Zabbix.TRIGGER_PRIORITY,
                "comments":f"Le fichier {name} n'a pas été trouvé."
            }
            self.api.trigger.create(triggerExist)
            Zabbix.logger_zabbix.debug(f"\n\nCreation du trigger {triggerExist['event_name']}\n")
            
        def ItemSize(host, name: str, item:str, size: str, parentName):
            itemSize: dict = {
                "hostid":host['hostid'],
                "name":"FileSize_"+name,
                "key_":"vfs.file.size["+item+"]",
                "type":0,
                "value_type":3,
                "interfaceid":host["interfaces"][0]["interfaceid"],
                "delay":f"{Zabbix.DELAY};{Zabbix.INTERVAL}",
            }
            self.api.item.create(
                hostid=itemSize['hostid'],
                name=itemSize['name'],
                key_=itemSize['key_'],
                type=itemSize['type'],
                value_type=itemSize['value_type'],
                interfaceid=itemSize['interfaceid'],
                delay=itemSize['delay'],
            )
            Zabbix.logger_zabbix.debug(f"Creation de l'item {itemSize['name']}")
            triggerSize: dict = {
                "event_name":"FileSize_"+name,
                "description":"FileSize_"+name,
                "expression":"last(/"+host['host']+"/"+itemSize['key_']+")<="+size,
                "recovery_mode":1,"recovery_expression":"last(/"+host['host']+"/"+itemSize['key_']+")>"+size,
                "priority":Zabbix.TRIGGER_PRIORITY,
                "comments":f"La taille du fichier {name} est inférieur à la limite définie."
            }
            self.api.trigger.create(triggerSize)
            parentID = TriggerID(parentName)
            selfID = TriggerID("FileSize_"+name)
            self.api.trigger.addDependencies({"triggerid":selfID, "dependsOnTriggerid":parentID})
            Zabbix.logger_zabbix.debug(f"\n\nCreation du trigger {triggerSize['event_name']}\ndependant de {parentName}\n")
            
        def ItemAge(host, name: str, item: str, age: str, parentName) -> None:
            itemAge: dict = {
                "hostid":host['hostid'],
                "name":"FileAge_"+name,
                "key_":"vfs.file.time["+item+"]",
                "type":0,
                "value_type":3,
                "interfaceid":host["interfaces"][0]["interfaceid"],
                "delay":f"{Zabbix.DELAY};{Zabbix.INTERVAL}",
            }
            self.api.item.create(
                hostid=itemAge['hostid'],
                name=itemAge['name'],
                key_=itemAge['key_'],
                type=itemAge['type'],
                value_type=itemAge['value_type'],
                interfaceid=itemAge['interfaceid'],
                delay=itemAge['delay'],
            )
            Zabbix.logger_zabbix.debug(f"Creation de l'item {itemAge['name']}")
            triggerAge: dict = {
                "event_name":"FileAge_"+name,
                "description":"FileAge_"+name,
                "expression":"abs(now()-last(/"+host['host']+"/"+itemAge['key_']+"))>"+age,
                "recovery_mode":1,"recovery_expression":"abs(now()-last(/"+host['host']+"/"+itemAge['key_']+"))<="+age,
                "priority":Zabbix.TRIGGER_PRIORITY,
                "comments":f"Pas fichier {name} récent trouvé."
            }
            self.api.trigger.create(triggerAge)
            parentID = TriggerID(parentName)
            selfID = TriggerID("FileAge_"+name)
            self.api.trigger.addDependencies({"triggerid":selfID, "dependsOnTriggerid":parentID})
            Zabbix.logger_zabbix.debug(f"\n\nCreation du trigger {triggerAge['event_name']}\ndependant de {parentName}\n")
            
        """
         _____            _                  _                       __  __       _       
        |  __ \          | |                | |                     |  \/  |     (_)      
        | |  | | ___  ___| | __ _ _ __   ___| |__   ___ _   _ _ __  | \  / | __ _ _ _ __  
        | |  | |/ _ \/ __| |/ _` | '_ \ / __| '_ \ / _ \ | | | '__| | |\/| |/ _` | | '_ \ 
        | |__| |  __/ (__| | (_| | | | | (__| | | |  __/ |_| | |    | |  | | (_| | | | | |
        |_____/ \___|\___|_|\__,_|_| |_|\___|_| |_|\___|\__,_|_|    |_|  |_|\__,_|_|_| |_|
                                                                                        
        """
        def main(name: str, file: str) -> None:
            itemsLst: list = []
            itemsNameLst: list = []
            hosts = self.api.host.get(selectInterfaces='extend', groupids=[Zabbix.SWITCHID.get('pyZabbixGitFileGroup')])
            items = self.api.item.get(groupids=[Zabbix.SWITCHID.get('pyZabbixGitFileGroup')])
            itemsLst = GetItems(items, itemsLst) # type: ignore
            exist: str = "FileExits_"+name
            for item in itemsLst:
                for it in item.keys():
                    itemsNameLst.append(it)
            if (exist not in itemsNameLst and exist not in items):
                for host in hosts:
                    Zabbix.logger_zabbix.debug(f"host: {host}, name: {name}, file: {file}")
                    ItemExist(host, name, file)
                    ItemSize(host, name, file, Zabbix.ITEM_SIZE, exist) # taille en octets ?
                    ItemAge(host, name, file, Zabbix.ITEM_AGE, exist) # 1800 sec == 30 min
                    Zabbix.logger_zabbix.debug(f"\n\n{'*'*50}\nCreation de triggers/items:{name}\nserver:{host['host']}\npriorite: {Zabbix.triggerPriority.get(Zabbix.TRIGGER_PRIORITY)}\n{'*'*50}\n")
        
        main(name, file)

if __name__=='__main__':
    Zapi = Zabbix("http://172.16.20.12/zabbix/", "053b13d15a1d00c45ce4d2efc7ac3fcbfab6f9d0c136669ef6ef159602652f38") # type: ignore
    Zapi.connexion()
    grp = Zapi.GetGroup()
    from pprint import pprint
    pprint(grp)