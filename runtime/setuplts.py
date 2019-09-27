import sys
import shutil
import os.path
import configparser
import logging
import time
import urllib.request
import traceback
import platform
import zipfile
sys.path.append(os.path.dirname(os.path.realpath(__file__)))  # Workaround for python 3.6's obtuse import system.
import minecraftversions

class InstallMC:
    _default_config = 'conf/mcp.cfg'

    def __init__(self, conffile=None):
        self.conffile = conffile
        self.readconf()
        if platform.system() == "Windows":
            self.platform = "windows"
        else:
            self.platform = "linux"
        self.confdir = self.config.get("DEFAULT", "DirConf")
        self.jardir = self.config.get("DEFAULT", "DirJars")
        self.tempdir = self.config.get("DEFAULT", "DirTemp")
        self.logdir = self.config.get("DEFAULT", "DirLogs")
        self.mcplogfile = self.config.get('MCP', 'LogFile')
        self.mcperrlogfile = self.config.get('MCP', 'LogFileErr')
        self.startlogger()

    def startlogger(self):
        """
        Basically sets up a logger and different logger handlers for different levels and such.
        Code copied from commands.py:92
        :return:
        """
        if not os.path.exists(self.logdir):
            os.makedirs(self.logdir)
        self.logger = logging.getLogger('MCPLog')
        self.logger.setLevel(logging.DEBUG)
        # create file handler which logs even debug messages
        fh = logging.FileHandler(filename=self.mcplogfile, mode='w')
        fh.setLevel(logging.DEBUG)
        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        # File output of everything Warning or above
        eh = logging.FileHandler(filename=self.mcperrlogfile, mode='w')
        eh.setLevel(logging.WARNING)
        # create formatter and add it to the handlers
        formatterconsole = logging.Formatter('%(message)s')
        ch.setFormatter(formatterconsole)
        formatterfile = logging.Formatter('%(asctime)s - %(module)11s.%(funcName)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M')
        fh.setFormatter(formatterfile)
        eh.setFormatter(formatterfile)
        # add the handlers to logger
        self.logger.addHandler(ch)
        self.logger.addHandler(fh)
        self.logger.addHandler(eh)

    def start(self, scriptsonly=False):
        """
        Main entry function.
        :return:
        """
        print(sys.version)

        self.logger.info("> Welcome to the LTS setup script!")
        self.logger.info("> This script will automatically set up your MCP workspace.")

        self.logger.info("\n> Setting up your workspace...")

        self.logger.info("\n> Making sure temp exists...")
        if not os.path.exists(self.tempdir):
            os.makedirs(self.tempdir)
        self.logger.info("> Making sure jars/bin/natives exists.")
        if not os.path.exists(os.path.join(self.jardir, "bin", "natives")):
            os.makedirs(os.path.join(self.jardir, "bin", "natives"))

        if scriptsonly:
            self.logger.info("\n> Copying scripts...")
            for file in os.listdir(os.path.join("runtime", self.platform + "_scripts")):
                shutil.copy2(os.path.join("runtime", self.platform + "_scripts", file), ".")
        else:
            self.logger.info("\n> Downloading LWJGL...")
            libtime = time.time()
            self.download("http://central.maven.org/maven2/org/lwjgl/lwjgl/lwjgl/2.8.4/lwjgl-2.8.4.jar", os.path.join(self.jardir, "bin", "lwjgl.jar"))
            self.download("http://central.maven.org/maven2/org/lwjgl/lwjgl/lwjgl_util/2.8.4/lwjgl_util-2.8.4.jar", os.path.join(self.jardir, "bin", "lwjgl_util.jar"))
            if self.platform == "win":
                self.logger.info("> Downloading LWJGL natives for windows...")
                self.download("http://central.maven.org/maven2/org/lwjgl/lwjgl/lwjgl-platform/2.8.4/lwjgl-platform-2.8.4-natives-windows.jar", os.path.join(self.jardir, "bin", "lwjgl_natives.zip"))
            else:
                self.logger.info("> Downloading LWJGL natives for linux...")
                self.download("http://central.maven.org/maven2/net/java/jinput/jinput-platform/2.0.5/jinput-platform-2.0.5-natives-linux.jar", os.path.join(self.jardir, "bin", "lwjgl_natives.zip"))

            self.logger.info("\n> Downloading JInput...")
            self.download("http://central.maven.org/maven2/net/java/jinput/jinput/2.0.5/jinput-2.0.5.jar", os.path.join(self.jardir, "bin", "jinput.jar"))
            if self.platform == "win":
                self.logger.info("> Downloading JInput natives for windows...")
                self.download("http://central.maven.org/maven2/net/java/jinput/jinput-platform/2.0.5/jinput-platform-2.0.5-natives-windows.jar", os.path.join(self.jardir, "bin", "jinput_natives.zip"))
            else:
                self.logger.info("> Downloading JInput natives for linux...")
                self.download("http://central.maven.org/maven2/org/lwjgl/lwjgl/lwjgl-platform/2.8.4/lwjgl-platform-2.8.4-natives-linux.jar", os.path.join(self.jardir, "bin", "jinput_natives.zip"))
            self.logger.info('> Done in %.2f seconds' % (time.time() - libtime))

            self.logger.info("\n> Extracting natives...")
            exttime = time.time()
            nativezip = zipfile.ZipFile(os.path.join(self.jardir, "bin", "lwjgl_natives.zip"))
            nativezip.extractall(os.path.join(self.jardir, "bin", "natives"))
            nativezip = zipfile.ZipFile(os.path.join(self.jardir, "bin", "jinput_natives.zip"))
            nativezip.extractall(os.path.join(self.jardir, "bin", "natives"))
            self.logger.info('> Done in %.2f seconds' % (time.time() - exttime))

            self.logger.info("\n> Copying scripts...")
            for file in os.listdir(os.path.join("runtime", self.platform + "_scripts")):
                shutil.copy2(os.path.join("runtime", self.platform + "_scripts", file), ".")

            self.logger.info("\n> Setting up minecraft...")
            self.setupmc()


    def setupmc(self):
        self.logger.info("> If you wish to supply your own configuration, type \"none\".")
        self.logger.info("> Any two versions joined by a comma (b1.5_01,1.5_02) are client vs server version.")
        self.logger.info("> Only b1.7.3 is supported as of now.")

        versions = ["b1.7.3"]
        versionsstring = "b1.7.3"
        #for version in os.listdir(self.confdir):
        #    if os.path.isdir(os.path.join(self.confdir, version)) and version not in ["patches"]:
        #        versionsstring += version + ", "
        #        versions.append(version)
        #versionsstring = versionsstring.strip(", ")

        inp = ""
        while inp not in versions:
            self.logger.info("> Current versions are: " + versionsstring)
            self.logger.info("> What version would you like to install?")

            inp = str(input(": "))

            if inp == "none":
                return

        self.logger.info("> Copying config.")
        copytime = time.time()
        self.copydir(os.path.join(self.confdir, inp), self.confdir)
        self.logger.info('> Done in %.2f seconds' % (time.time() - copytime))

        self.logger.info("> Downloading Minecraft client...")
        clientdltime = time.time()
        self.download(minecraftversions.versions["client"][inp.split(",")[0]]["url"],
                      os.path.join(self.jardir, "bin", "minecraft.jar"))
        self.logger.info('> Done in %.2f seconds' % (time.time() - clientdltime))

        self.logger.info("> Downloading Minecraft server...")
        if inp.__contains__(","):
            ver = inp.split(",")[0][0] + inp.split(",")[1]
        else:
            ver = inp
        serverdltime = time.time()
        self.download(minecraftversions.versions["server"][ver]["url"],
                      os.path.join(self.jardir, "minecraft_server.jar"))
        self.logger.info('> Done in %.2f seconds' % (time.time() - serverdltime))

    def download(self, url, dst):
        # Because legacy code is stupid.
        try:
            print("> Downloading \"" + url + "\"...")
            response = urllib.request.urlopen(url)
            data = response.read()
            with open(dst, "wb") as file:
                file.write(data)

            self.logger.info("> Done!")
        except:
            traceback.print_exc()
            print("> Unable to download \"" + url + "\"")

    def copydir(self, src, dst, replace=True):
        """
        Shutil's built in copytree function raises an exception if src exists.
        This is basically copytree minus the exceptions and added logging.
        :param src:
        :param dst:
        :param replace:
        :return:
        """
        for file in os.listdir(src):
            if os.path.isfile(os.path.join(src, file)):
                if os.path.exists(os.path.join(dst, file)) and not replace:
                    self.logger.debug("> Skipped file \"" + os.path.join(src, file) + "\": Already exists.")
                elif os.path.exists(os.path.join(dst, file)):
                    os.unlink(os.path.join(dst, file))
                    shutil.copy2(os.path.join(src, file), dst)
                    self.logger.debug("> Replaced file \"" + os.path.join(src, file) + "\".")
                else:
                    shutil.copy2(os.path.join(src, file), dst)
                    self.logger.debug("> Copied file \"" + os.path.join(src, file) + "\".")
            elif os.path.isdir(os.path.join(dst, file)):
                self.copydir(os.path.join(src, file), os.path.join(dst, file))
            else:
                os.makedirs(os.path.join(dst, file))
                self.copydir(os.path.join(src, file), os.path.join(dst, file))

    def readconf(self):
        """
        Reads config and creates a class from it.
        Code copied from commands.py:126
        :return:
        """
        config = configparser.ConfigParser()
        with open(self._default_config) as config_file:
            config.read_file(config_file)
        if self.conffile is not None:
            config.read(self.conffile)
        self.config = config


if __name__ == '__main__':
    installmc = InstallMC()
    try:
        if sys.argv[1] == "scriptsonly":
            installmc.start(True)
        else:
            installmc.start()
    except:
        installmc.start()
