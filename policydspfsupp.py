# -*- coding: utf-8 -*-
#
#  Tumgreyspf
#  Copyright © 2004-2005, Sean Reifschneider, tummy.com, ltd.
#
#  pypolicyd-spf changes
#  Copyright © 2007,2008,2009,2010 Scott Kitterman <scott@kitterman.com>
'''
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License version 2 as published 
    by the Free Software Foundation.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.'''

import syslog
import os
import sys
import string
import re
import urllib
import stat


#  default values
defaultConfigData = {
        'debugLevel' : 1,
        'HELO_reject' : 'SPF_Not_Pass',
        'Mail_From_reject' : 'Fail',
        'PermError_reject' : 'False',
        'TempError_Defer'  : 'False',
        'skip_addresses' : '127.0.0.0/8,::ffff:127.0.0.0//104,::1//128',
        'defaultSeedOnly' : 1
        }


#################################
class ConfigException(Exception):
    '''Exception raised when there's a configuration file error.'''
    pass


####################################################################
def processConfigFile(filename = None, config = None, useSyslog = 1,
        useStderr = 0):
    '''Load the specified config file, exit and log errors if it fails,
    otherwise return a config dictionary.'''

    import policydspfsupp
    if config == None: config = policydspfsupp.defaultConfigData
    if filename != None:
        try:
            readConfigFile(filename, config)
        except Exception, e:
            if useSyslog:
                syslog.syslog(e.args[0])
            if useStderr:
                sys.stderr.write('%s\n' % e.args[0])
            sys.exit(1)
    return(config)


#################
class ExceptHook:
   def __init__(self, useSyslog = 1, useStderr = 0):
      self.useSyslog = useSyslog
      self.useStderr = useStderr
   
   def __call__(self, etype, evalue, etb):
      import traceback
      tb = traceback.format_exception(*(etype, evalue, etb))
      tb = map(string.rstrip, tb)
      tb = string.join(tb, '\n')
      for line in string.split(tb, '\n'):
         if self.useSyslog:
            syslog.syslog(line)
         if self.useStderr:
            sys.stderr.write(line + '\n')


####################
def setExceptHook():
    sys.excepthook = ExceptHook(useSyslog = 1, useStderr = 1)


####################
def quoteAddress(s):
    '''Quote an address so that it's safe to store in the file-system.
    Address can either be a domain name, or local part.
    Returns the quoted address.'''

    s = urllib.quote(s, '@_-+')
    if len(s) > 0 and s[0] == '.': s = '%2e' + s[1:]
    return(s)


######################
def unquoteAddress(s):
    '''Undo the quoting of an address.  Returns the unquoted address.'''

    return(urllib.unquote(s))


###############################################################
commentRx = re.compile(r'^(.*)#.*$')
def readConfigFile(path, configData = None, configGlobal = {}):
    '''Reads a configuration file from the specified path, merging it
    with the configuration data specified in configData.  Returns a
    dictionary of name/value pairs based on configData and the values
    read from path.'''

    debugLevel = configGlobal.get('debugLevel', 0)
    if debugLevel >= 5: syslog.syslog('readConfigFile: Loading "%s"' % path)
    if configData == None: configData = {}
    nameConversion = {
            'debugLevel' : int,
            'HELO_reject' : str,
            'Mail_From_reject' : str,
            'PermError_reject' : str,
            'TempError_Defer' : str,
            'Mail_From_pass_restriction' : str,
            'HELO_pass_restriction' : str,
            'Prospective' : str,
            'Whitelist' : str,
            'skip_addresses': str,
            'Domain_Whitelist' : str,
            'Reject_Not_Pass_Domains' : str,
            'defaultSeedOnly' : int
            }

    #  check to see if it's a file
    try:
        mode = os.stat(path)[0]
    except OSError, e:
        syslog.syslog('ERROR stating "%s": %s' % ( path, e.strerror ))
        return(configData)
    if not stat.S_ISREG(mode):
        syslog.syslog('ERROR: is not a file: "%s", mode=%s' % ( path, oct(mode) ))
        return(configData)

    #  load file
    fp = open(path, 'r')
    while 1:
        line = fp.readline()
        if not line: break

        #  parse line
        line = string.strip(string.split(line, '#', 1)[0])
        if not line: continue
        data = map(string.strip, string.split(line, '=', 1))
        if len(data) != 2:
            if len(data) == 1:
                if debugLevel >= 1:
                    syslog.syslog('Configuration item "%s" not defined in file "%s"'
                        % ( line, path ))
            else:
                syslog.syslog('ERROR parsing line "%s" from file "%s"'
                    % ( line, path ))
            continue
        name, value = data

        #  check validity of name
        conversion = nameConversion.get(name)
        if conversion == None:
            syslog.syslog('ERROR: Unknown name "%s" in file "%s"' % ( name, path ))
            continue

        if debugLevel >= 5: syslog.syslog('readConfigFile: Found entry "%s=%s"'
                % ( name, value ))
        configData[name] = conversion(value)
    fp.close()
    
    return(configData)

