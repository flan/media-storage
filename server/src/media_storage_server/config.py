# -*- encoding: utf-8 -*-
"""
media_storage_server.config
===========================

Purpose
-------

Provides a static access-point for the system's configuration data, loaded from files in
Linux-standard locations and supplemented with sane defaults.

Legal
+++++
 This file is part of media-storage.
 media-storage is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program. If not, see <http://www.gnu.org/licenses/>.
 
 (C) Neil Tallim, 2012 <flan@uguu.ca>
"""
import ConfigParser
import os
import sys

class _Config(ConfigParser.RawConfigParser):
    """
    A simple wrapper around RawConfigParser to extend it with support for default values.
    """
    def get(self, section, option, default):
        """
        Returns a custom value, if one is found. Otherwise, returns C{default}.
        
        @type section: basestring
        @param section: The section to be queried.
        @type option: basestring
        @param option: The option to be queried.
        @type default: object
        @param default: The value to be returned, if the requested option is undefined.
        
        @rtype: object
        @return: Either the requested value or the given default.
        """
        try:
            return ConfigParser.RawConfigParser.get(self, section, option)
        except ConfigParser.Error:
            return default
            
    def getint(self, section, option, default):
        """
        Returns a custom value, if one is found. Otherwise, returns C{default}.
        
        @type section: basestring
        @param section: The section to be queried.
        @type option: basestring
        @param option: The option to be queried.
        @type default: int
        @param default: The value to be returned, if the requested option is undefined.
        
        @rtype: int
        @return: Either the requested value or the given default.
        
        @raise ValueError: The value to be returned could not be converted to an C{int}.
        """
        return int(self.get(section, option, default))
        
    def getfloat(self, section, option, default):
        """
        Returns a custom value, if one is found. Otherwise, returns C{default}.
        
        @type section: basestring
        @param section: The section to be queried.
        @type option: basestring
        @param option: The option to be queried.
        @type default: float
        @param default: The value to be returned, if the requested option is undefined.
        
        @rtype: float
        @return: Either the requested value or the given default.
        
        @raise ValueError: The value to be returned could not be converted to a C{float}.
        """
        return float(self.get(section, option, default))
        
    def getboolean(self, section, option, default):
        """
        Returns a custom value, if one is found. Otherwise, returns C{default}.
        
        @type section: basestring
        @param section: The section to be queried.
        @type option: basestring
        @param option: The option to be queried.
        @type default: bool
        @param default: The value to be returned, if the requested option is undefined.
        
        @rtype: bool
        @return: Either the requested value or the given default.
        """
        return bool(str(self.get(section, option, default)).lower().strip() in (
         'y', 'yes',
         't', 'true',
         'ok', 'okay',
         '1',
        ))
        
class _Settings(_Config):
    """
    For details on what these attributes mean, please see the sample config file.
    """
    @property
    def run_as_daemon(self):
        return self.getboolean('general', 'run_as_daemon', True)
        
    @property
    def pidfile(self):
        return self.get('general', 'pidfile', '/var/run/media-storage.pid')
        
        
    @property
    def http_port(self):
        return self.getint('http', 'port', 1234)
        
        
    @property
    def database_address(self):
        return (
         self.get('database', 'host', 'localhost'),
         self.getint('database', 'port', 0)
        )
        
    @property
    def database_credentials(self):
        credentials = (
         self.get('database', 'username', None),
         self.get('database', 'password', None)
        )
        if all(credentials):
            return credentials
        return None
        
    @property
    def database_database(self):
        return self.get('database', 'database', 'media-storage')
        
    @property
    def database_collection(self):
        return self.get('database', 'collection', 'entities')
        
        
    @property
    def storage_minute_resolution(self):
        return self.getint('storage', 'minute_resolution', 5)
        
    @property
    def storage_generic_family(self):
        return self.get('storage', 'generic_family', None)
        

    @property
    def families(self):
        """
        Returns all specialised families as a list of (name, uri) tuples.
        """
        return self.has_section('families') and self.items('families') or []
        
        
    @property
    def security_trusted_hosts(self):
        return self.get('security', 'trusted_hosts', '')
        
    @property
    def security_query_size(self):
        return self.getint('security', 'query_size', 100)
        
        
    @property
    def maintainer_deletion_windows(self):
        return self.get('maintainers', 'deletion_windows', '')
        
    @property
    def maintainer_deletion_sleep(self):
        return self.getint('maintainers', 'deletion_sleep', 300)
        
    @property
    def maintainer_compression_windows(self):
        return self.get('maintainers', 'compression_windows', '')
        
    @property
    def maintainer_compression_sleep(self):
        return self.getint('maintainers', 'compression_sleep', 1800)
        
    @property
    def maintainer_database_windows(self):
        return self.get('maintainers', 'database_windows', '')
        
    @property
    def maintainer_database_sleep(self):
        return self.getint('maintainers', 'database_sleep', 43200)
        
    @property
    def maintainer_filesystem_windows(self):
        return self.get('maintainers', 'filesystem_windows', '')
        
    @property
    def maintainer_filesystem_sleep(self):
        return self.getint('maintainers', 'filesystem_sleep', 43200)
        
        
    @property
    def log_file_path(self):
        return self.get('log', 'file_path', None)
        
    @property
    def log_file_history(self):
        return self.getint('log', 'file_history', 7)

    @property
    def log_file_verbosity(self):
        return self.get('log', 'file_verbosity', 'INFO')

    @property    
    def log_console_verbosity(self):
        return self.get('log', 'console_verbosity', 'DEBUG')
        
        
    @property
    def email_timeout(self):
        return self.getfloat('email', 'timeout', 2.0)
        
    @property
    def email_host(self):
        return self.get('email', 'host', 'localhost')
        
    @property
    def email_port(self):
        return self.getint('email', 'port', 25)
        
    @property
    def email_tls(self):
        return self.getboolean('email', 'tls', False)
        
    @property
    def email_username(self):
        return self.get('email', 'username', None)
        
    @property
    def email_password(self):
        return self.get('email', 'password', None)
        
    @property
    def email_alert(self):
        return self.getboolean('email', 'alert', False)
        
    @property
    def email_alert_cooldown(self):
        return self.getfloat('email', 'alert_cooldown', 300.0)
        
    @property
    def email_alert_subject(self):
        return self.get('email', 'alert_subject', 'Critical failure')
        
    @property
    def email_alert_from(self):
        return self.get('email', 'alert_from', 'media-storage@example.org')
        
    @property
    def email_alert_to(self):
        return self.get('email', 'alert_to', 'media-storage@example.org')
        
        
#Initialisation
####################################################################################################
CONFIG = _Settings()
CONFIG.read([
 '/etc/media-storage/media-storage.ini',
 os.path.expanduser('~/.media-storage/media-storage.ini'),
 './media-storage.ini',
]) #Load config data in Linux-standard order
if len(sys.argv) > 1: #Load the first argument as a config file
   CONFIG.read(sys.argv[1]) 
   
