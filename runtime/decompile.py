# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 16:54:36 2011

@author: ProfMobius
@version: v1.2
"""
import time
import os
import sys
import shutil
from optparse import OptionParser
sys.path.append(os.path.dirname(os.path.realpath(__file__)))  # Workaround for python 3.6's obtuse import system.
from commands import Commands
import recompile as recompile


def main(conffile=None):
    commands = Commands(conffile)
    commands.checkforupdates()

    cltdone = decompile_side(0, commands)
    srvdone = decompile_side(1, commands)

    commands.logger.info('== Post decompiling operations ==')
    if not cltdone or not srvdone:
        commands.logger.info('> Recompiling')
        recompile.main(conffile)
    if not cltdone:
        commands.logger.info('> Generating the md5 (client)')
        commands.gathermd5s(0)
    if not srvdone:
        commands.logger.info('> Generating the md5 (server)')
        commands.gathermd5s(1)


def decompile_side(side=0, commands=None, force_jad=False):
    use_ff = os.path.exists(commands.fernflower) and not force_jad

    srcdir = None

    if side == 0:
        srcdir = os.path.join(commands.srcclient, commands.ffsource).replace('/', os.sep).replace('\\', os.sep)
    if side == 1:
        srcdir = os.path.join(commands.srcserver, commands.ffsource).replace('/', os.sep).replace('\\', os.sep)

    if not srcdir:
        commands.logger.info('!! Side is not provided !!')
        return True

    if not os.path.exists(srcdir):
        if side == 0:
            commands.logger.info('== Decompiling Client ==')
        if side == 1:
            commands.logger.info('== Decompiling Server ==')

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
            commands.logger.info('> Applying patches')
            commands.applyffpatches(side)
            # LTS JAVADOC
            commands.logger.info('> Adding javadoc')
            commands.process_javadoc(side)
            # LTS END JAVADOC
            commands.logger.info('> Renaming sources')
            commands.rename(side)
            # TODO: Improve ModLoader installation. 
            if os.path.exists("conf/ModLoader.java") and side == 0:
                commands.logger.info('> Do you want to install a fixed class for ModLoader? [y/N]')
                commands.logger.info('> You will still need to change some errored variables from int to boolean.')
                inp = str(input(": "))
                if inp.lower() == "yes" or inp.lower() == "y":
                    shutil.copyfile("conf/ModLoader.java", commands.dirsrc + "/minecraft/net/minecraft/src/ModLoader.java")
                
            commands.logger.info('> Done in %.2f seconds' % (time.time() - currenttime))
    else:
        if side == 0:
            commands.logger.warn('!! Client already decompiled. Run cleanup before decompiling again !!')
        if side == 1:
            commands.logger.warn('!! Server already decompiled. Run cleanup before decompiling again !!')
        return True

    return False


if __name__ == '__main__':
    parser = OptionParser(version='MCP %s' % Commands.MCPVersion)
    parser.add_option('-c', '--config', dest='config', help='additional configuration file')
    (options, args) = parser.parse_args()
    main(options.config)
