# -*- coding: utf-8 -*-
#
#  pypolicyd-spf
#  Copyright © 2010 Scott Kitterman <scott@kitterman.com>
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
import re
import string
import os

###############################################################
commentRx = re.compile(r'^(.*)#.*$')
def readUserConfigFile(path, recipient, configData):
    '''Reads a configuration file from the specified path, merging it
    with the configuration data specified in configData for the identified
    recipient.  Returns updated configData for the user.'''

    debugLevel = configData.get('debugLevel', 0)
    if debugLevel >= 4: syslog.syslog('readConfigFile: Loading "%s"' % path)
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
            'Domain_Whitelist_PTR': str,
            'No_Mail': str,
            'Reject_Not_Pass_Domains' : str,
            'defaultSeedOnly' : int
            }

    #  check to see if it's a file
    try:
        mode = os.stat(path)[0]
    except OSError, e:
        syslog.syslog('ERROR stating "%s": %s' % ( path, e.strerror ))
        return(configData)

    #  load file
    fp = open(path, 'r')
    while 1:
        line = fp.readline()
        if not line: break

        #  parse line
        line = string.strip(string.split(line, '#', 1)[0])
        if not line: continue
        data = map(string.strip, string.split(line, ',', 1))
        user, value = data
        if user != recipient:
            peruser = False
            continue
        values = {}
        valuelist = string.split(value, '|')
        for valuepair in valuelist:
            key, item = string.split(valuepair, '=')
            values[key] = item
        for config in values.iteritems():
            #  check validity of name
            conversion = nameConversion.get(config[0])
            name, value = config
            if conversion == None:
                syslog.syslog('ERROR: Unknown name "%s" in file "%s"' % ( name, path ))
                continue
            if debugLevel >= 5: syslog.syslog('readConfigFile: Found entry "%s=%s"'
                % ( name, value ))
            configData[name] = conversion(value)
        peruser = True
    fp.close()

    return configData, peruser


def datacheck(configData, recipient):
    debugLevel = configData.get('debugLevel', 1)
    if debugLevel >= 3: syslog.syslog('Starting to process per-user settings')
    userdata = configData.get('Per_User')
    if debugLevel >= 3: syslog.syslog('User data: '+ str(userdata))
    usertype, userlocation = string.split(userdata, ',')
    if usertype == "text":
         if debugLevel >= 4: syslog.syslog('Reading per user data (type text) from:  "%s"' % userlocation)
         configData, peruser = readUserConfigFile(userlocation, recipient, configData)
         if debugLevel >= 4: syslog.syslog('Per-user settings for "%s": "%s"' % (recipient, str(configData)))

    return configData, peruser
