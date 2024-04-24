# Sauvegarde des .cfg

## Require

les dépendances nécessaires sont situé dans requirements.txt
pour les installer lancer la commande dans le terminal:
```pip install -r requirements.txt```
ou
`py -m pip install -r requirements.txt`

## Compilation

pour compiler le script en executable le module pyinstaller doit être installer
lancer un terminal et se déplacer dans le dossier du script et lancer la commande:
`pyinstaller --onefile <nomDuScript.py> -n <nomDeLexe.exe>`
l'executable sera situé dans le dossier dist

## CSV

les fichiers cvs doivent être structuré comme suit:
![
    `type;name;loc;ip;username;password;device_type`
    `ssh;Nom_Du_Switch;BAT-A;192.168.0.0;user;password;cisco_ios`
](img/csv.png)

`type;name;loc;ip;username;password;device_type`

## LOGS

le chemin des logs sont est indiqué dans le fichier `.env`
|VERBOSE         |NUMERIQUE|DESCRIPTION                                                                                                                                                           |
|:---------------|:-------:|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|logging.DEBUG   |10       |Detailed information, typically only of interest to a developer trying to diagnose a problem.                                                                         |
|logging.INFO    |20       |Confirmation that things are working as expected.                                                                                                                     |
|logging.WARNING |30       |An indication that something unexpected happened, or that a problem might occur in the near future (e.g. ‘disk space low’). The software is still working as expected.|
|logging.ERROR   |40       |Due to a more serious problem, the software has not been able to perform some function.                                                                               |
|logging.CRITICAL|50       |A serious error, indicating that the program itself may be unable to continue running.                                                                                |

par défaut les logs sont enregistrés
>C:\\TFTP\\GIT\\LOGS

si l'option `--filelog` est ajouté
>C:\\TFTP\\GIT\\LOGS\\SwitchList\\[hhmm].ZabbixFileLogs.json

pour observer les logs en direct lancer un terminal powershell et rentré la commande
`Get-Content .log -wait`

## File Environement

Le fichier .env doit contenir les information suivantes
![
    "
    LOG_DIR        : Chemin racine de la sauveguarde des logs
    LOG_LEVEL      : niveau de log à enregistrer
        "DEBUG"
        "INFO"
        "WARNING"
        "ERROR"
        "CRITICAL"
    DIR            : Chemin racine de la sauveguarde des configurations
    ZABBIXIP       : Adresse IP du serveur zabbix
    ZABBIXTOKEN    : TOKEN de connexion au compte zabbix
    AVAYA_USER     : utilisateur de connexion pour les switchs avaya
    AVAYA_PASS     : mot de passe de connexion pour les switchs avaya
    ARUBA_ERS_USER : utilisateur de connexion pour les switchs HP aruba
    ARUBA_ERS_PASS : mot de passe de connexion pour les switchs HP aruba
    DELAY          : interval entre deux requêtes de valeur d'éléments zabbix
    GIT_REMOTE     : IP du serveur
    GIT_SERVER     : Chemin du repertoire du serveur
    GIT_SSH_USER   : Utilisateur de connexion ssh
    "
](img/env.png)

## Programme

pour démarer la sauvegarde des configurations lancer l'executable ConfigSaver.exe
par défaut l'exe récupère les informations depuis le serveur Zabbix et les informations contenues dans .env
`ConfigSaver.exe -h`
en cli les arguments suivants peuvent être passé:

`-g, --group`
`--group` permet de récupérer les groupes accessibles

la sortie peut être redirigée vers un fichier `.txt` ou `.json`
`ConfigSaver.exe -g > group.json`

`--src <nomFichier.csv>`
`--src` permet de donner un nombre non limité de fichiers source

[Liste des OS compatible](device_type_list.md)

`-f, --filelog`
`-f` ou `--filelog` permet de sauvegarder la liste des switchs trouvé dans Zabbix au format .json
![`
    "{
        "TYPE_OS": [
            [
                "ssh",
                "NOM_SWITCH",
                "GROUPE",
                "XX.XX.XX.XX",
                "USER",
                "PASSWORD",
                "device_type"
            ]
        ]
    }"
`](img/json.png)
