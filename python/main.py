import csv,logs,argparse,logging
from logging.handlers import TimedRotatingFileHandler
from switch import SSH,Telnet
from zabbix import Zabbix
from dotenv import load_dotenv
from time import sleep
from os import getenv, environ, path

# class logging.handlers.SysLogHandler(address=('localhost', SYSLOG_UDP_PORT), facility=LOG_USER, socktype=socket.SOCK_DGRAM)

load_dotenv("C:\\Scripts\\ENV_GIT_Main\\.env")
# load_dotenv("C:\\Users\\MERIELJ\\Desktop\\Stage_2024\\ENV_GIT\\ENV_GIT_Main - Copie (2)\\.env")
sleep(1)
DIR: str | None = getenv("DIR")
BASEFILE: str | None = getenv("BASEFILE")
ZABBIXIP: str | None = environ.get("ZABBIXIP")
ZABBIXTOKEN: str | None = environ.get("ZABBIXTOKEN")
LOG_DIR: str | None = getenv("LOG_DIR")
LOG_LEVEL: str | None = getenv("LOG_LEVEL")
STREAM_HANDLER: str | None = getenv("STREAM_HANDLER")
DISCONNECT: str | None = getenv("DISCONNECT")
PASS_BIS: str | None = getenv("PASS_BIS")
LOG_FILE: str | None = LOG_DIR+"\\.log" if LOG_LEVEL else None
ERR_LOG_CSV: str | None = LOG_DIR+"\\err.csv" if LOG_LEVEL else None

AVAYA_USER: str | None = getenv("AVAYA_USER") if not environ.get("AVAYA_USER") else environ.get("AVAYA_USER")
AVAYA_PASS: str | None = getenv("AVAYA_PASS") if not environ.get("AVAYA_PASS") else environ.get("AVAYA_PASS")
ARUBA_ERS_USER: str | None = getenv("ARUBA_ERS_USER") if not environ.get("ARUBA_ERS_USER") else environ.get("ARUBA_ERS_USER")
ARUBA_ERS_PASS: str | None = getenv("ARUBA_ERS_PASS") if not environ.get("ARUBA_ERS_PASS") else environ.get("ARUBA_ERS_PASS")
ARUBA_ERS_USER_BIS: str | None = getenv("ARUBA_ERS_USER_BIS") if not environ.get("ARUBA_ERS_USER_BIS") else environ.get("ARUBA_ERS_USER_BIS")

logLevel: dict = {
    "DEBUG":logging.DEBUG,
    "INFO":logging.INFO,
    "WARNING":logging.WARNING,
    "ERROR":logging.ERROR,
    "CRITICAL":logging.CRITICAL
}

# ------ log standard ------
logger_main = logging.getLogger(__name__)
logger_main.setLevel(logLevel[LOG_LEVEL])
formater_main = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:ligne_%(lineno)d -> %(message)s')
file_handler_main = TimedRotatingFileHandler(
    filename=LOG_FILE, # type: ignore
    when='H',
    interval=24,
    backupCount=5,
    encoding='utf-8'
)
file_handler_main.setFormatter(formater_main)
file_handler_main.setLevel(logLevel[LOG_LEVEL])

stream_handler_main = logging.StreamHandler()
stream_handler_main.setFormatter(formater_main)

logger_main.addHandler(file_handler_main)
logger_main.addHandler(stream_handler_main) if STREAM_HANDLER.lower() == 'true' else ...

rotatingLogger: bool = True

# -------------------------------

def GetParser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sauvegarde des configuration de Switch via SSH et Telnet")
    
    parser.add_argument('-f', '--filelog',  dest="ZabbixFileLog", help="Sauvegarder la liste des switchs trouvé dans Zabbix", required=False, action='store_true')
    parser.add_argument('-g', '--group',  dest="group", help="renvoie la liste des groupes trouvé", required=False, action='store_true')
    parser.add_argument('--src', type=str, nargs="*", dest="source", help='source du fichier csv', required=False)

    return parser.parse_args()

@logs.Timer
def Reroll(fileList: list):
    for fLst in fileList:
        with open(fLst, 'w') as newLog:
            newLog.close()

@logs.Timer
def OpenCSV(file:str) -> list:
    switchLst: list=[]

    with open(file,"r") as c:
        read = csv.reader(c, delimiter=";")
        logger_main.debug(f"Lecture .csv: {read}")
        for row in read:
            logger_main.debug(f"{read}")
            if 0<len(row):
                if row[0] == "type":
                    continue
                match(row[4]):
                    case "aruba_os":
                        device: dict = {
                            "ip":row[3],
                            "username":ARUBA_ERS_USER,
                            "password":ARUBA_ERS_PASS,
                            "device_type":row[4]
                            # 'use_keys': True, # Activer cle ssh
                            # 'key_file': '/data/05_PYTHON_DEMO/SSH_KEY/admin1' # chemin cle ssh
                        }
                    case "avaya_ers":
                        device: dict = {
                            "ip":row[3],
                            "username":AVAYA_USER,
                            "password":AVAYA_PASS,
                            "device_type":row[4]
                            # 'use_keys': True, # Activer cle ssh
                            # 'key_file': '/data/05_PYTHON_DEMO/SSH_KEY/admin1' # chemin cle ssh
                        }
                    case _:
                        raise ValueError
                s=[row[0], row[1], row[2], device]
                switchLst.append(s)
    
    return switchLst

def DisconnectSwitch(file:str) -> list:
    switchLst: list=[]

    with open(file,"r") as c:
        read = csv.reader(c, delimiter=";")
        for row in read:
            switchLst.append(row)
    
    return switchLst

def PassBisSwitch(file:str) -> list:
    switchLst: list=[]

    with open(file,"r") as c:
        read = csv.reader(c, delimiter=";")
        for row in read:
            switchLst.append(row)
    
    return switchLst

def WriteCSV(file: str, msg: list) -> None:
    logger_main.debug(f"Call by {msg}")
    with open(file, 'a') as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(msg)
        logger_main.debug(f"Write in {f}; msg: {msg}")
        f.close()

@logs.Timer
def saveSwitch(switch: list, Zapi: Zabbix) -> None:
    match(switch[0]):
        case "ssh":
            ssh = SSH(DIR, switch[1], switch[2], switch[3]) # type: ignore
            ssh.main()
            Zapi.Declancheur(ssh.Name, ssh.File) # type: ignore
        case "telnet":
            tn = Telnet(DIR, switch[1], switch[2], switch[3]) # type: ignore
            tn.main()
            Zapi.Declancheur(tn.Name, tn.File) # type: ignore
        case _:
            logger_main.error(f"{switch[1]}:{switch[1]}: Erreur lors de la creation de la class (type de connexion errone).")

@logs.Timer
def main(args: argparse.Namespace) -> int:
    device: dict
    sw: tuple
    succ: int = 0; err: int = 0;
    if args.group:
        ZabbixGrp = Zabbix(ZABBIXIP, ZABBIXTOKEN)  # type: ignore
        ZabbixGrp.connexion()
        grp = ZabbixGrp.GetGroup()
        from pprint import pprint
        pprint(grp, indent=4)
        exit()
    if (args.source != None):
        logger_main.info(f"run from '--src' {args.source}")
        Zapi = Zabbix(ZABBIXIP, ZABBIXTOKEN) # type: ignore
        Zapi.connexion()
        Zapi.Disconnect = DisconnectSwitch(DISCONNECT) if path.exists(DISCONNECT) else []
        Zapi.PassBis = PassBisSwitch(PASS_BIS) if path.exists(PASS_BIS) else []
        for file in args.source:
            switchLst = OpenCSV(file)
            logger_main.debug(f"Switchs recuperer: {len(switchLst)} -> {switchLst}")
            for switch in switchLst:
                total: int = len(switchLst)
                logger_main.info(f"Total de switch trouvé: {total:>4}")
                try:
                    saveSwitch(switch, Zapi)
                    succ += 1
                except Exception as e:
                    err += 1
                    row = [switch[0],switch[1],switch[2],switch[3],switch[6]]
                    WriteCSV(ERR_LOG_CSV, row)
                    logger_main.exception(e)
                finally:
                    progress: str = f"success: {succ:>3}/{total:>3}; error {err:>3}/{total:>3};"
                    logger_main.info(f"\n\n{"-"*25} {progress:^40} {"-"*25}\n")
                    progress: str = f"progress: {((succ+err)*100)/total:>6.2f}%"
                    logger_main.info(f"\n\n{"-"*25} {progress:^40} {"-"*25}\n")
                    continue
    else:
        logger_main.info(f"run from Default Zabbix")
        Reroll([ERR_LOG_CSV])
        Zapi = Zabbix(ZABBIXIP, ZABBIXTOKEN) # type: ignore
        Zapi.connexion()
        Zapi.Disconnect = DisconnectSwitch(DISCONNECT) if path.exists(DISCONNECT) else []
        Zapi.PassBis = PassBisSwitch(PASS_BIS) if path.exists(PASS_BIS) else []
        swLst = Zapi.main(args.ZabbixFileLog)
        total: int = len(swLst)
        logger_main.info(f"Total de switch trouvé: {total:>4}")
        for s in swLst:
            device = {
                "ip":s[3],
                "username":s[4],
                "password":s[5],
                "device_type":s[6],
                "secret":s[7],
                "conn_timeout":30
            }
            sw = (s[0], s[1], s[2], device)

            try:
                saveSwitch(sw, Zapi)
                succ += 1
            except Exception as e:
                err += 1
                row = [sw[0],sw[1],sw[2],device["ip"],device["device_type"]]
                WriteCSV(ERR_LOG_CSV, row)
                logger_main.exception(e)
            finally:
                progress: str = f"success: {succ:>3}/{total:>3}; error {err:>3}/{total:>3};"
                logger_main.info(f"\n\n{"-"*25} {progress:^40} {"-"*25}\n")
                progress: str = f"progress: {((succ+err)*100)/total:>6.2f}%"
                logger_main.info(f"\n\n{"-"*25} {progress:^40} {"-"*25}\n")
                continue

    return 0

if __name__=="__main__":
    try:
        Reroll([LOG_FILE])
        logger_main.info(f"\n\n{'='*100}\n\n{"*"*20}{"Debut du programme":^30}{"*"*20}\n\n")
        args = GetParser()
        main(args)
    except Exception as e:
        logger_main.exception(e)
    logger_main.info(f'\n\n\n{"*"*20}{"Arret du programme":^30}{"*"*20}\n\n{'='*100}\n')
    try:
        file_handler_main.doRollover()
    except PermissionError as p:
        logger_main.debug(f"Impossible deffectuer une rotation de log via logging: {p}")
        rotatingLogger = False
    finally:
        logs.Rotation([LOG_FILE]) if not rotatingLogger else ...
    exit()
