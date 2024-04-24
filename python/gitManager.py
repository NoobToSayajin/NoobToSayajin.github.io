import logs, logging
from git import Repo, Actor, Remote, RemoteProgress, Commit # type: ignore
from logging.handlers import TimedRotatingFileHandler
from os import path, getenv, environ
from dotenv import load_dotenv

class MyProgressPrinter(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=""):
        print(
            op_code,
            cur_count,
            max_count,
            cur_count / (max_count or 100.0),
            message or "NO MESSAGE",
        )

class GitManager:
    load_dotenv("C:\\Scripts\\ENV_GIT_Main\\.env")
    GIT_SERVER: str | None = getenv("GIT_SERVER") if not environ.get("GIT_SERVER") else environ.get("GIT_SERVER")
    GIT_SSH_USER: str | None = getenv("GIT_SSH_USER") if not environ.get("GIT_SSH_USER") else environ.get("GIT_SSH_USER")
    GIT_REMOTE: str | None = getenv("GIT_REMOTE") if not environ.get("GIT_REMOTE") else environ.get("GIT_REMOTE")
    LOG_DIR: str | None = getenv("LOG_DIR")
    LOG_LEVEL: str | None = getenv("LOG_LEVEL")
    STREAM_HANDLER: str | None = getenv("STREAM_HANDLER")
    LOG_FILE: str | None = LOG_DIR+"\\.log" if LOG_LEVEL else None
    EMAIL = "null@null"
    NAME = "ConfigSaver"

    logLevel: dict = {
        "DEBUG":logging.DEBUG,
        "INFO":logging.INFO,
        "WARNING":logging.WARNING,
        "ERROR":logging.ERROR,
        "CRITICAL":logging.CRITICAL
    }

    logger_gittmanager = logging.getLogger(__name__)
    logger_gittmanager.setLevel(logLevel[LOG_LEVEL])

    formater_gitmanager = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:ligne_%(lineno)d -> %(message)s')

    file_handler_gitmanager = TimedRotatingFileHandler(
        filename=LOG_FILE, # type: ignore
        when='H',
        interval=24,
        backupCount=5,
        encoding='utf-8'
    )

    stream_handler_gitmanager = logging.StreamHandler()
    stream_handler_gitmanager.setFormatter(formater_gitmanager)

    file_handler_gitmanager.setFormatter(formater_gitmanager)
    file_handler_gitmanager.setLevel(logLevel[LOG_LEVEL])

    logger_gittmanager.addHandler(file_handler_gitmanager)
    logger_gittmanager.addHandler(stream_handler_gitmanager) if STREAM_HANDLER.lower() == 'true' else ...
    
    def __init__(self, dir: str, originPath: str) -> None:
        self.author: Actor = Actor(GitManager.NAME, GitManager.EMAIL)
        self.committer: Actor = Actor(GitManager.NAME, GitManager.EMAIL)
        self.dir: str = dir
        self.originPath: str = GitManager.GIT_SERVER+"\\"+originPath+".git" if GitManager.GIT_SERVER else originPath
        self.repo: Repo = Repo(self.dir) if path.exists(self.dir) else Repo.init(self.dir, mkdir=True)
        self.origin: Remote | None = self.Remote() if GitManager.GIT_SERVER else None

        GitManager.logger_gittmanager.debug(f"creation Objet git {self.repo}")

    def __del__(self) -> None:
        # GitManager.logger_gittmanager.debug(f"Destruction Objet git {self.repo}")
        pass

    def __str__(self) -> str:
        return f"Repo: {self.repo}, origin: {self.origin}"
        
    @logs.Timer
    def Remote(self) -> Remote:
        GitManager.logger_gittmanager.info(f"Server Origin: {GitManager.GIT_SERVER}")
        try:
            remote = Repo(self.originPath) if path.exists(self.originPath) else Repo.clone_from(self.dir, self.originPath, multi_options=["--bare"], progress=MyProgressPrinter) if path.exists(self.dir) else Repo.init(self.originPath, mkdir=True, bare=True) # type: ignore
        except Exception as e:
            GitManager.logger_gittmanager.exception(e)
        print(self.repo.remote("origin").exists())
        self.origin = self.repo.remote("origin") if self.repo.remote("origin").exists() else remote.create_remote('origin', f"{GitManager.GIT_SSH_USER}@{GitManager.GIT_REMOTE}:{self.originPath}")
        GitManager.logger_gittmanager.debug(f"git remote add origin {GitManager.GIT_SSH_USER}@{GitManager.GIT_REMOTE}:{self.originPath}")
        self.origin.fetch()
        self.origin.pull()
        GitManager.logger_gittmanager.debug(f"git fetch origin main\ngit pull origin main")
        return self.origin

    def Commit(self, addFile: list[str], msg: str) -> None:
        self.repo.index.add(addFile)
        self.repo.index.commit(msg, author=self.author, committer=self.committer)

    def last_commit_data(self) -> str:
        commit: Commit = self.repo.head.commit
        return f"\n\n{'*'*50}\n{str(commit.hexsha)}\n\"{commit.summary}\" by {commit.author.name} ({commit.author.email})\n{str(commit.authored_datetime)}\ncount: {commit.count()} and size: {commit.size}\n{'*'*50}\n"

    @property
    def Log(self):
        self.repo.git.log(p=True)

    """

     ██████╗██╗      █████╗ ███████╗███████╗    ███╗   ███╗ █████╗ ██╗███╗   ██╗
    ██╔════╝██║     ██╔══██╗██╔════╝██╔════╝    ████╗ ████║██╔══██╗██║████╗  ██║
    ██║     ██║     ███████║███████╗███████╗    ██╔████╔██║███████║██║██╔██╗ ██║
    ██║     ██║     ██╔══██║╚════██║╚════██║    ██║╚██╔╝██║██╔══██║██║██║╚██╗██║
    ╚██████╗███████╗██║  ██║███████║███████║    ██║ ╚═╝ ██║██║  ██║██║██║ ╚████║
    ╚═════╝╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝    ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝
                                                                                

    """

    @logs.Timer
    def main(self, dir: list[str], msg: str) -> None:
        self.Commit(dir, msg)
        GitManager.logger_gittmanager.info(self.last_commit_data())
        if GitManager.GIT_SERVER:
            self.origin.push() # type: ignore
