# -*- encoding: utf-8 -*-
"""
media_storage_caching_proxy.config
==================================

Purpose
-------

Provides a static access-point for the system's configuration data, loaded from files in
Linux-standard locations and supplemented with sane defaults.

Legal
-----

(C) Neil Tallim <flan@uguu.ca>, 2011
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
    def http_port(self):
        return self.getint('http', 'port', 1236)
        
        
    @property
    def compression_formats(self):
        if self.has_section('compression'):
            return set((key for (key, value) in self.items('compression') if key.lower() == 'yes'))
        return set()
        
        
    @property
    def storage_path(self):
        return self.get('storage', 'path', None)
        
    @property
    def storage_metadata_extension(self):
        return self.get('storage', 'metadata_extension', 'meta')
        
    @property
    def storage_purge_interval(self):
        return self.getfloat('storage', 'purge_interval', 5.0)


    @property
    def rules_min_cache_time(self):
        return self.getfloat('rules', 'min_cache_time', 10.0)
        
    @property
    def rules_max_cache_time(self):
        return self.getfloat('rules', 'max_cache_time', 7200.0)
        
    @property
    def rules_timeout(self):
        return self.getfloat('rules', 'timeout', 60.0)
        
        
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
 '/etc/media-storage/media-storage_caching_proxy.ini',
 os.path.expanduser('~/.media-storage/media-storage_caching_proxy.ini'),
 './media-storage_caching_proxy.ini',
]) #Load config data in Linux-standard order
if len(sys.argv) > 1:
   CONFIG.read(sys.argv[1]) 
   
