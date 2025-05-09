import json
import os.path
from tkinter import filedialog, messagebox
from typing import Any

import arrow
from cryptography.fernet import Fernet

from Modules.Constants import Constants
from Modules.Logger import Logger


class ConfigObject:
  dyflexis = None
  ics = None
  google = None
  persistentStorageAllowed = None
  debug = None
  fileName = "data"

  def __init__(self):
    self.__version__ = Constants.version
    self.dyflexis = {"username": "", "password": "", "location": "", "organisation": ""}
    self.ics = {"url": ""}
    self.google = {"calendarId": None, 'credentials': None}
    # todo persistentStorageAllowed config een checkbox geven in gui
    self.persistentStorageAllowed = None
    self.debug = {}
    self.github_version = {"name": None, 'date': None}

    self.askStorageQuestion()

  def askStorageQuestion(self):
    base_path = os.path.expanduser('~/' + Constants.userStorageLocation)
    if not os.path.isdir(base_path):
      msgBox = messagebox.askyesno("persistent storage",
                                   "Mogen wij een folder 'dycol' aanmaken in uw thuis folder om configuratie en log data op te slaan?".format())
      if msgBox:
        self.persistentStorageAllowed = True
        os.makedirs(base_path)
    else:
      self.persistentStorageAllowed = True

  def __getattr__(self, name: str) -> Any:
    return self.__dict__[name]

  def __setattr__(self, name, value):
    # na elke set slaan we op naar de config, zo is die altijd up to date
    self.__dict__[name] = value

  def save(self, location=None):
    if not self.persistentStorageAllowed:
      return self
    # alleen als we de config gebruiken save ik de waarden. anders draaien we in memory
    savePath = Constants.resource_path(ConfigObject.fileName)
    if location is not None:
      savePath = location
    with open(savePath, 'wb') as fp:
      data = self.toJson()
      bytesData = bytes(data.encode())
      encryptedData = self.encrypt(bytesData)
      fp.write(encryptedData)
      fp.close()
    return self

  @staticmethod
  def encrypt(content):
    f = Fernet(Constants.getEncryptionKey())
    return f.encrypt(content)

  @staticmethod
  def decrypt(content):
    f = Fernet(Constants.getEncryptionKey())
    return f.decrypt(content)

  @staticmethod
  def loadFromFile():

    if os.path.isfile(Constants.resource_path(ConfigObject.fileName)):
      try:
        with open(Constants.resource_path(ConfigObject.fileName), 'r') as fp:
          superValue = fp.read()
          configObject = ConfigObject.fromJson(ConfigObject.decrypt(superValue))
          fp.close()
        configObject.__version__ = Constants.version
        return configObject
      except Exception as e:
        Logger.getLogger(__name__).error('error bij laden', exc_info=True)

        return ConfigObject()
    else:
      return ConfigObject()

  def toJson(self):
    return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=2)

  @staticmethod
  def fromJson(jsonText):
    """
    load a configuration from json text
    :param jsonText:
    :return:
    """
    config = json.loads(jsonText)
    configObject = ConfigObject()
    # we zetten de keys van de json in onze classe, alles wat niet ingevuld word blijft zo standaard
    for key in config:
      configObject.__setattr__(key, config[key])
    configObject.__version__ = Constants.version
    # configObject.save()
    return configObject


class ConfigLand:
  __configLand = None

  @staticmethod
  def getConfigLand():
    if ConfigLand.__configLand is None:
      ConfigLand.__configLand = ConfigLand()
    return ConfigLand.__configLand

  def __init__(self):
    self.__config = ConfigObject.loadFromFile()
    self.checkGithub()
    self.__updateHandlers = []
    self.__loadHandlers = []

  def save(self):
    self.handleUpdateHandlers()
    self.__config.save()

  def checkGithub(self):
    version = Constants.githubVersion()
    self.__config.github_version['name'] = version['name']
    self.__config.github_version['date'] = version['github_published_at']

  def addUpdateHandler(self, handler):
    """
    update config
    :param handler:
    :return:
    """
    self.__updateHandlers.append(handler)

  def addLoadHandler(self, handler):
    """
    load from config
    :param handler:
    :return:
    """
    self.__loadHandlers.append(handler)

  def handleUpdateHandlers(self):
    Logger.getLogger(__name__).info('handeling handlers')
    for handler in self.__updateHandlers:
      if handler is not None:
        handler()

  def handleLoadHandlers(self):
    Logger.getLogger(__name__).info('handeling handlers')
    for handler in self.__loadHandlers:
      if handler is not None:
        handler()

  def getKey(self, key):
    return self.__config.__getattr__(key)

  def setKey(self, key, value):
    self.__config.__setattr__(key, value)  # self.__config.save()

  def reset(self):
    if os.path.isfile(Constants.resource_path(ConfigObject.fileName)):
      os.remove(Constants.resource_path(ConfigObject.fileName))

    self.__config = ConfigObject()
    self.handleLoadHandlers()

  def exportConfig(self):
    self.handleUpdateHandlers()
    name = "Dycal-config-" + arrow.get().format('YYYY-MM-DD')

    target_dir = filedialog.asksaveasfilename(title="Locatie om naartoe te exporteren",
                                              initialdir=os.path.expanduser('~/Downloads'), initialfile=name)
    self.__config.save(target_dir)

  def importConfig(self):
    targetfile = filedialog.askopenfilename(title="locatie van uw config", filetypes=[('Json bestand', '')])
    if targetfile is not None and targetfile != "":
      with open(targetfile, 'r') as fp:
        content = fp.read()
        fp.close()
        self.__config = ConfigObject.fromJson(ConfigObject.decrypt(content))
    self.handleLoadHandlers()
