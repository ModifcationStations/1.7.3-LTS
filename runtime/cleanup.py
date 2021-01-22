import shutil
import os
import sys
import time
import configparser
import platform
import traceback


class Cleanup:
    _default_config = 'conf/mcp.cfg'

    def __init__(self, conffile=None):
        print(os.getcwd())
        self.conffile = conffile
        self.readconf()
        self.confdir = self.config.get("DEFAULT", "DirConf")
        self.tempdir = self.config.get("DEFAULT", "DirTemp")
        self.logdir = self.config.get("DEFAULT", "DirLogs")
        self.srcdir = self.config.get("DEFAULT", "DirSrc")
        self.bindir = self.config.get("DEFAULT", "DirBin")
        self.reobfdir = self.config.get("DEFAULT", "DirReobf")
        self.jardir = self.config.get("DEFAULT", "DirJars")
        self.mcplogfile = self.config.get('MCP', 'LogFile')
        self.mcperrlogfile = self.config.get('MCP', 'LogFileErr')
        if platform.system() == "Windows":
            self.systemext = "bat"
        else:
            self.systemext = "sh"

    def start(self):
        """
        ARE YOU *REALLY* SURE?!
        :return:
        """
        print("> Welcome to the LTS cleanup script!")
        print("> This script will delete your workspace and set most of it to factory defaults.")
        print("> Are you sure you want to clean up your workspace? [y/N]")
        inp = input(": ")
        if inp.lower() != "y":
            sys.exit(1)
        print("> Are you *REALLY* sure you want to clean up your workspace? [y/N]")
        print("> This deletes ALL your source files and jars! This is NOT recoverable!")
        inp = input(": ")
        if inp.lower() != "y":
            sys.exit(1)

        print("> Commencing the purge of the universe...")
        no_error = True

        print("> Deleting \"" + self.jardir + "\"...")
        jartime = time.time()
        # Delete jars while keeping server.properties.
        try:
            if os.path.exists(self.jardir):
                if not os.path.exists(self.tempdir):
                    os.makedirs(self.tempdir)
                if os.path.exists(os.path.join(self.jardir, "server.properties")):
                    shutil.copy2(os.path.join(self.jardir, "server.properties"), self.tempdir)
                shutil.rmtree(self.jardir)
                os.makedirs(self.jardir)
                if os.path.exists(os.path.join(self.tempdir, "server.properties")):
                    shutil.copy2(os.path.join(self.tempdir, "server.properties"), self.jardir)
        except Exception as e:
            no_error = False
            print("> Couldn't clear \"" + self.jardir + "\"!")
            traceback.print_exc()
        print('> Done in %.2f seconds' % (time.time() - jartime))

        for dir in [self.reobfdir, self.bindir, self.srcdir, self.tempdir]:
            print("> Deleting \"" + dir + "\"...")
            deltime = time.time()
            try:
                if os.path.exists(dir):
                    shutil.rmtree(dir)
            except Exception as e:
                no_error = False
                print("> Couldn't clear \"" + dir + "\"!")
                traceback.print_exc()
            print('> Done in %.2f seconds' % (time.time() - deltime))

        print("> Deleting non-default config...")
        conftime = time.time()
        try:
            if os.path.exists(self.confdir):
                if os.path.exists(os.path.join(self.confdir, "patches")) and os.path.isdir(os.path.join(self.confdir, "patches")):
                    shutil.rmtree(os.path.join(self.confdir, "patches"))
                for file in os.listdir(self.confdir):
                    if os.path.isfile(os.path.join(self.confdir, file)) and file not in ["mcp.cfg", "version.cfg"]:
                        os.unlink(os.path.join(self.confdir, file))
        except Exception as e:
            no_error = False
            print("> Couldn't clear \"" + self.confdir + "\"!")
            traceback.print_exc()
        print('> Done in %.2f seconds' % (time.time() - conftime))

        print("> Deleting system specific files from root...")
        systime = time.time()
        try:
            for file in ["decompile", "recompile", "reobfuscate", "startclient", "startserver", "updatemcp", "updatemd5", "makepatches"]:
                if os.path.exists(file + "." + self.systemext) and os.path.isfile(file + "." + self.systemext):
                    os.unlink(file + "." + self.systemext)
        except Exception as e:
            no_error = False
            print("> Couldn't clear system specific files!")
            traceback.print_exc()

        if no_error:
            os.unlink("cleanup." + self.systemext)
        else:
            print("> Cleanup file has not been deleted because an error occurred earlier.")
        print('> Done in %.2f seconds' % (time.time() - systime))

        print("> Done!")
        print("> Press enter to continue...")
        input()

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
    cleanup = Cleanup()
    try:
        cleanup.start()
        sys.exit(0)
    except:
        traceback.print_exc()
        sys.exit(1)
