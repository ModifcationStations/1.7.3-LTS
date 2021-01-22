# -*- coding: utf-8 -*-
"""
This is horrible spaghetti code.
I like it.
Paths are hardcoded because no-one should ever need to change these paths.
"""
import time
import os
import sys
import shutil
import subprocess
import re
import glob
from optparse import OptionParser
sys.path.append(os.path.dirname(os.path.realpath(__file__)))  # Workaround for python 3.6's obtuse import system.
from filehandling.srgshandler import readsrgs
from commands import Commands


def main(conffile=None):
    commands.checkforupdates()

    decompile_side(0)
    decompile_side(1)


def decompile_side(side=0):
    filename = None
    if side == 0:
        commands.logger.info("== Decompiling Client ==")
        filename = "minecraft"
    elif side == 1:
        commands.logger.info("== Decompiling Server ==")
        filename = "minecraft_server"
    else:
        commands.logger.info("!! Side is not provided !!")
        return True

    if commands.checkjars(side):
        currenttime = time.time()
        commands.logger.info('> Creating SRGS')
        commands.createsrgs(side)
        commands.logger.info('> Applying SpecialSource')
        commands.applyss(side)
        commands.logger.info('> Applying Exceptor')
        commands.applyexceptor(side)
        commands.logger.info('> Decompiling...')
        commands.applyff(side)
        commands.logger.info('> Unzipping the sources')
        commands.extractsrc(side)
        commands.logger.info('> Unzipping the jar')
        commands.extractjar(side)
        commands.logger.info("> Applying existing patch files...")
        shutil.copytree("src/" + filename, "src/" + filename + "_unpatched")
        commands.applyffpatches(side)
        commands.logger.info("> Done in %.2f seconds" % (time.time() - currenttime))
        commands.logger.info("> Source located in src.")

    return False


def mainpatches():
    commands.checkforupdates()

    makepatches(0)
    makepatches(1)


def makepatches(side):
    filename = None
    if side == 0:
        commands.logger.info("== Generating Patches for Client ==")
        filename = "minecraft"
    elif side == 1:
        commands.logger.info("== Generating Patches for Server ==")
        filename = "minecraft_server"
    else:
        commands.logger.info("!! Side is not provided !!")
        return

    currenttime = time.time()

    commands.logger.info("> Generating new patch files...")
    
    if os.name.__contains__("posix"):
        cmd = ["diff -r -U3 --exclude=*~ " + filename + "_unpatched/net " + filename + "/net"]
    else:
        cmd = ["diff", "-r", "-U3", "--exclude=*~", filename + "_unpatched/net", filename + "/net"]
    with open("src/" + filename + ".patch", "w") as patchfile:
        subprocess.run(cmd, shell=True, stdout=patchfile,  stderr=subprocess.STDOUT, cwd="src/")

    commands.logger.info("> Done in %.2f seconds" % (time.time() - currenttime))
    commands.logger.info("> Patch files are located in src.")


if __name__ == "__main__":
    parser = OptionParser(version="MCP %s" % Commands.MCPVersion)
    parser.add_option("-c", "--config", dest="config", help="additional configuration file")
    (options, args) = parser.parse_args()
    commands = Commands(options.config)
    commands.logger.info("> This script REQUIRES that you have diff or diffutils installed and added to your path.")
    commands.logger.info("> https://sourceforge.net/projects/gnuwin32/files/diffutils/2.8.7-1/")
    commands.logger.info("> The command used is \"diff -r -U3 <patched source> <unpatched source>\".")
    commands.logger.info("> Do you have the prerequisites and know what you are doing? [y/N]")
    if os.path.exists(commands.dirsrc + "/minecraft_unpatched") or os.path.exists(commands.dirsrc + "/minecraft_server_unpatched"):
        commands.logger.info("This script will generate patch files.")
    else:
        commands.logger.info("This script will setup a workspace to make patches.")

    inp = input(": ")
    if inp.lower() == "y":
        if os.path.exists(commands.dirsrc + "/minecraft_unpatched") or os.path.exists(commands.dirsrc + "/minecraft_server_unpatched"):
            mainpatches()
            commands.logger.info("> Patches made!")
        else:
            main()
            commands.logger.info("> Setup complete! Edit the source as you need to, then run this script again!")
