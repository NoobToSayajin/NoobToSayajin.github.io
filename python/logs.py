import datetime, logging, time
from logging.handlers import TimedRotatingFileHandler
from dotenv import load_dotenv
from os import getenv, path, listdir, remove

load_dotenv("C:\\Scripts\\ENV_GIT_Main\\.env")

TODAY: str = datetime.date.today().strftime("%Y-%m-%d")
LOG_DIR: str | None = getenv("LOG_DIR")
LOG_LEVEL: str | None = getenv("LOG_LEVEL")
MAX_AGE: float | None = float(getenv("MAX_AGE"))
STREAM_HANDLER: str | None = getenv("STREAM_HANDLER")
LOG_FILE: str | None = LOG_DIR+"\\.log" if LOG_LEVEL else None

logLevel: dict = {
    "DEBUG":logging.DEBUG,
    "INFO":logging.INFO,
    "WARNING":logging.WARNING,
    "ERROR":logging.ERROR,
    "CRITICAL":logging.CRITICAL
}

logger = logging.getLogger(__name__)
logger.setLevel(logLevel[LOG_LEVEL])

formater = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:ligne_%(lineno)d -> %(message)s')

file_handler = TimedRotatingFileHandler(
    filename=LOG_FILE, # type: ignore
    when='H',
    interval=24,
    backupCount=5,
    encoding='utf-8'
)

file_handler.setFormatter(formater)
file_handler.setLevel(logLevel[LOG_LEVEL])

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formater)

logger.addHandler(file_handler)
logger.addHandler(stream_handler) if STREAM_HANDLER.lower() == 'true' else ...

def Timer(func):
    def wrapper(*args, **kwargs):
        msg: str = f"Debut de{func.__name__!r}"
        logger.debug(f'{"*"*10} {msg:^30} {"*"*10}')
        t1 = datetime.datetime.now()
        res = func(*args, **kwargs)
        t2 = datetime.datetime.now() - t1
        msg = f"Arret de{func.__name__!r}"
        logger.debug(f'{"*"*10} {msg:^30} {"*"*10}')
        logger.info(f'Fonction {func.__name__!r} executee en {(t2)}s')
        return res
    return wrapper

def Rotation(fileList: list):
    for fLst in fileList:
        with open(fLst+"."+TODAY, 'a') as newLog:
            logger.debug(f"Ouverture/Creation de {fLst+"."+TODAY}")
            with open(fLst, 'r') as log:
                logger.debug(f"Lecture de {fLst}")
                lines = log.readlines()
                for l in lines:
                    newLog.write(l)
                log.close()
            newLog.close()
        files = listdir(fLst)
        for file in files:
            age = time.time()-path.getctime(fLst+"\\"+file)
            if MAX_AGE <= age and file!=".log":
                logger.debug(f"Suppression de {file}")
                remove(fLst+"\\"+file)
        fLst.close()