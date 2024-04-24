import tempfile, datetime, logs, logging
from logging.handlers import TimedRotatingFileHandler
from gitManager import GitManager
from dotenv import load_dotenv
from os import path, getenv


class ErrorSize(Exception):
    """Le fichier de configuration est vide"""
    f"Le fichier de configuration est vide"

    def __init__(self, size: int, maxSize: int):
        self.size = size
        self.maxSize = maxSize
        self.message = f"Taille du fichier ({self.size}) inferieur a: {self.maxSize} Bytes"
        super().__init__(self.message)

"""

██████╗  █████╗ ███████╗███████╗
██╔══██╗██╔══██╗██╔════╝██╔════╝
██████╔╝███████║███████╗█████╗  
██╔══██╗██╔══██║╚════██║██╔══╝  
██████╔╝██║  ██║███████║███████╗
╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝
                                

"""
class Switch:
    load_dotenv("C:\\Scripts\\ENV_GIT_Main\\.env")
    # load_dotenv("C:\\Users\\MERIELJ\\Desktop\\Stage_2024\\ENV_GIT\\ENV_GIT_Main - Copie (2)\\.env")
    ban: tuple=("\x1b","","-","\n","# show running-config","#show running-config","Running configuration:")
    TODAY: str = datetime.date.today().strftime("%Y-%m-%d")
    LOG_DIR: str | None = getenv("LOG_DIR")
    LOG_LEVEL: str | None = getenv("LOG_LEVEL")
    STREAM_HANDLER: str | None = getenv("STREAM_HANDLER")
    FILE_MIN_SIZE: int | None = int(getenv("FILE_MIN_SIZE"))
    LOG_FILE: str | None = LOG_DIR+"\\.log" if LOG_LEVEL else None

    logLevel: dict = {
        "DEBUG":logging.DEBUG,
        "INFO":logging.INFO,
        "WARNING":logging.WARNING,
        "ERROR":logging.ERROR,
        "CRITICAL":logging.CRITICAL
    }

    logger_switch = logging.getLogger(__name__)
    logger_switch.setLevel(logLevel[LOG_LEVEL])

    formater_switch = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:ligne_%(lineno)d -> %(message)s')

    file_handler_switch = TimedRotatingFileHandler(
        filename=LOG_FILE, # type: ignore
        when='H',
        interval=24,
        backupCount=5,
        encoding='utf-8'
    )
    file_handler_switch.setFormatter(formater_switch)
    file_handler_switch.setLevel(logLevel[LOG_LEVEL])

    stream_handler_switch = logging.StreamHandler()
    stream_handler_switch.setFormatter(formater_switch)

    logger_switch.addHandler(file_handler_switch)
    logger_switch.addHandler(stream_handler_switch) if STREAM_HANDLER.lower() == 'true' else ...
    
    def __init__(self, pDir:str, pName:str, pLoc:str, pProp:dict, pConnType: str) -> None:
        self.name: str = pName
        self.localisation: str = pLoc
        self.property: dict = pProp
        self.connType: str = pConnType
        self.dir: str = pDir+"\\"+self.localisation+"\\"+self.name
        self.file: str = self.dir+"\\"+self.name+".cfg"
        self.git: GitManager = GitManager(self.dir, self.localisation+"\\"+self.name)
        Switch.logger_switch.debug(f"Creation: {self}")
    
    def __str__(self) -> str:
        return f"{self.name}, type de connexion: {self.connType}, local: {self.localisation}, ip: {self.property["ip"]}, OS type: {self.property["device_type"]}"
    
    @property
    def Name(self) -> str:
        return self.name
    
    @property
    def Dir(self) -> str:
        return self.dir
    
    @property
    def File(self) -> str:
        return self.file

    @logs.Timer
    def saveConf(self, conf:str) -> None:
        Switch.logger_switch.info("Sauvegarde de la configuration")
        tmp: tempfile._TemporaryFileWrapper[str] = tempfile.TemporaryFile("w+t",delete=False)
        with open(tmp.name, "w") as f:
            f.write(conf)
            Switch.logger_switch.debug(f"Creation fichier temporaire: {tmp.name}")
        Switch.logger_switch.debug(f"sizeof: {tmp.name}, {path.getsize(tmp.name)} Bytes")
        if path.getsize(tmp.name) <= Switch.FILE_MIN_SIZE:
            Switch.logger_switch.error(f"Taille du fichier inferieur a: {Switch.FILE_MIN_SIZE} Bytes")
            raise ErrorSize(path.getsize(tmp.name), Switch.FILE_MIN_SIZE)
        else:
            with open(self.file, "w") as c:
                with open(tmp.name,"r") as f:
                    lines = f.readlines()
                    for line in lines:
                        c.write(line) if not(line.startswith(Switch.ban) or line.upper().startswith(self.name.upper()+"#") or line.__contains__("# show running-config")) else ...
                    f.close()
                c.close()
                msg = f'Sauvegarde le la config {self.name} - {datetime.datetime.now().strftime("%Y-%m-%d.%Hh%M")}'
            self.git.main([self.file], msg)
    
    def __del__(self) -> None:
        Switch.logger_switch.debug(f"Destruction: {self}")
        pass

"""

███████╗███████╗██╗  ██╗
██╔════╝██╔════╝██║  ██║
███████╗███████╗███████║
╚════██║╚════██║██╔══██║
███████║███████║██║  ██║
╚══════╝╚══════╝╚═╝  ╚═╝
                        
"""

from netmiko import ConnectHandler, BaseConnection # type: ignore
class SSH(Switch):

    def __init__(self, pDir:str, pName:str, pLoc:str, pProp:dict) -> None:
        self.connType = "ssh"
        self.conn: BaseConnection
        super().__init__(pDir, pName, pLoc, pProp, self.connType)
        Switch.logger_switch.debug(f"Creation: {self}")
    
    @logs.Timer
    def connection(self) -> bool:
        Switch.logger_switch.info(f"{self.name}:{self.property['ip']}: Connexion")
        self.conn = ConnectHandler(**self.property)
        self.conn.enable()
        # self.conn.send_command_timing("enable")
        # self.conn.send_command_timing(self.property['secret'])
        return True
    
    @logs.Timer
    def showRun(self) -> str:
        Switch.logger_switch.debug(f"{self.name}:{self.property['ip']}: Envoie commande show running-config")
        return self.conn.send_command_timing("display current-configuration", last_read=45.0, read_timeout=120.0)
        # if "VSP" in self.name or "vsp" in self.name:
        #     return self.conn.send_command_timing("show running-config", last_read=45.0, read_timeout=120.0)
        # elif self.property["device_type"]=="huawei":
        #     return self.conn.send_command_timing("display current-configuration", last_read=45.0, read_timeout=120.0)
        # else:
        #     return self.conn.send_command_timing("show running-config")
    
    """

     ██████╗██╗      █████╗ ███████╗███████╗    ███╗   ███╗ █████╗ ██╗███╗   ██╗
    ██╔════╝██║     ██╔══██╗██╔════╝██╔════╝    ████╗ ████║██╔══██╗██║████╗  ██║
    ██║     ██║     ███████║███████╗███████╗    ██╔████╔██║███████║██║██╔██╗ ██║
    ██║     ██║     ██╔══██║╚════██║╚════██║    ██║╚██╔╝██║██╔══██║██║██║╚██╗██║
    ╚██████╗███████╗██║  ██║███████║███████║    ██║ ╚═╝ ██║██║  ██║██║██║ ╚████║
     ╚═════╝╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝    ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝
                                                                                

    """

    @logs.Timer
    def main(self) -> int:
        isConnect: bool
        isConnect = self.connection()
        if isConnect:
            output: str = self.showRun()
            self.saveConf(output)
            self.conn.disconnect()
            Switch.logger_switch.debug(f"{self.name}:{self.property['ip']}: Deconnexion")
            return 0
        else:
            Switch.logger_switch.error(f"{self.name}:{self.property['ip']}: connexion impossible")
            return 1

"""

████████╗███████╗██╗     ███╗   ██╗███████╗████████╗
╚══██╔══╝██╔════╝██║     ████╗  ██║██╔════╝╚══██╔══╝
   ██║   █████╗  ██║     ██╔██╗ ██║█████╗     ██║   
   ██║   ██╔══╝  ██║     ██║╚██╗██║██╔══╝     ██║   
   ██║   ███████╗███████╗██║ ╚████║███████╗   ██║   
   ╚═╝   ╚══════╝╚══════╝╚═╝  ╚═══╝╚══════╝   ╚═╝   
                                                    
"""

import telnetlib
from time import sleep
class Telnet(Switch):

    start: str = "\x19"
    space: str = "\x20"
    enter: str = "\x0D"
    
    def __init__(self, pDir:str, pName:str, pLoc:str, pProp:dict) -> None:
        self.connType = "telnet"
        self.conn: telnetlib.Telnet
        super().__init__(pDir, pName, pLoc, pProp, self.connType)
        Switch.logger_switch.debug(f"Creation: {self}")
    
    @logs.Timer
    def connection(self) -> tuple[bool, Exception | None]:
        Switch.logger_switch.info(f"{self.name}:{self.property['ip']}: Connexion")
        self.conn = telnetlib.Telnet(self.property["ip"], 23, timeout=2)
        sleep(1)
        self.conn.write(Telnet.start.encode("ascii"))
        sleep(1)
        # Switch.logger_switch.debug(f"{self.conn.read_very_eager().decode("ascii")}{"\n"*100}") # Voir la console dans les logs direct
        # self.conn.read_until(b"Username:") # switch test: SW_IUTC_2eme ne permet pas d'utiliser read_until UI non compatible
        # sleep(1)
        self.conn.write(self.property["username"].encode("ascii")+b"\n")
        self.conn.write(b"\r")
        sleep(3)
        # lSwitch.logger_switch.debug(f"{self.conn.read_very_eager().decode("ascii")}") # Voir la console dans les logs direct
        # self.conn.read_until(b"Password:") # switch test: SW_IUTC_2eme ne permet pas d'utiliser read_until UI non compatible
        # sleep(1)
        self.conn.write(b"\r")
        self.conn.write(self.property["password"].encode(encoding="ascii")+b"\n")
        # Switch.logger_switch.debug(f"{self.conn.read_very_eager().decode("ascii")}") # Voir la console dans les logs direct
        sleep(3)
        self.conn.write(b"\r")
        # self.conn.read_until(b"#") # switch test: SW_IUTC_2eme ne permet pas d'utiliser read_until UI non compatible
        # sleep(1)
        self.conn.write("enable".encode(encoding="ascii")+b"\n")
        sleep(3)
        self.conn.write(b"\r")
        # self.conn.read_until(b"#") # switch test: SW_IUTC_2eme ne permet pas d'utiliser read_until UI non compatible
        # sleep(1)
        # Switch.logger_switch.debug(f"{self.conn.read_very_eager().decode("ascii")}") # Voir la console dans les logs direct
        Switch.logger_switch.info(f"{self.name}:{self.property['ip']}: Connexion semble effectue")
        return True, None
    
    @logs.Timer
    def showRun(self) -> str:
        sleep(3)
        self.conn.write(b"\r")
        # Switch.logger_switch.debug(f"{self.conn.read_very_eager().decode("ascii")}") # Voir la console dans les logs direct
        Switch.logger_switch.debug(f"{self.name}:{self.property['ip']}: Envoie commande show running-config")
        self.conn.write("show running-config".encode("ascii"))
        sleep(.5)
        self.conn.write(b"\r")
        # Switch.logger_switch.debug(f"{self.conn.read_very_eager().decode("ascii")}") # Voir la console dans les logs direct
        sleep(2)
        for _ in range(0,11):
            self.conn.write(Telnet.space.encode("ascii"))
            sleep(2)
            # Switch.logger_switch.debug(f"{self.conn.read_very_eager().decode("ascii")}") # Voir la console dans les logs direct
        Switch.logger_switch.debug(f"{self.name}:{self.property['ip']}: Commande show running-config semble effectue")
        return self.conn.read_very_eager().decode("ascii")
        
    """

     ██████╗██╗      █████╗ ███████╗███████╗    ███╗   ███╗ █████╗ ██╗███╗   ██╗
    ██╔════╝██║     ██╔══██╗██╔════╝██╔════╝    ████╗ ████║██╔══██╗██║████╗  ██║
    ██║     ██║     ███████║███████╗███████╗    ██╔████╔██║███████║██║██╔██╗ ██║
    ██║     ██║     ██╔══██║╚════██║╚════██║    ██║╚██╔╝██║██╔══██║██║██║╚██╗██║
    ╚██████╗███████╗██║  ██║███████║███████║    ██║ ╚═╝ ██║██║  ██║██║██║ ╚████║
     ╚═════╝╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝    ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝
                                                                                

    """

    @logs.Timer
    def main(self) -> int:
        isConnect: bool; e: Exception | None
        isConnect,e = self.connection()
        if isConnect:
            output: str = self.showRun()
            self.saveConf(output)
            self.conn.write(b"exit")
            self.conn.write(b"\r")
            Switch.logger_switch.info(f"{self.name}:{self.property['ip']}: Deconnexion")
            return 0
        else:
            Switch.logger_switch.error(f"{self.name}:{self.property['ip']}: {e}")
            return 1
