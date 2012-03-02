#!/usr/bin/env python
"""
Deployment script for media-storage.
"""
__author__ = 'Neil Tallim'

import os
import subprocess

from distutils.core import setup

setup(
 name = 'media-storage',
 version = '0.9.0',
 description = "Centralised, stateless file-entity-storage and retrieval system",
 author = 'Neil Tallim',
 author_email = 'flan@uguu.ca',
 license = 'GPLv3',
 url = 'http://media-storage.googlecode.com/',
 package_dir = {
  '': 'src',
 },
 packages = [
  'media_storage_server',
  'media_storage_server.backends',
 ],
 data_files = [
  ('/etc/media-storage', [
   'src/media-storage.ini.sample',
  ]),
  ('/etc/init.d', [
   'init/media-storage',
  ]),
 ],
 scripts = [
  'src/media-storage',
 ],
)

#Post-installation stuff
print("Registering init-script to start on system boot...")
subprocess.call(('/bin/chmod', 'a+x', '/etc/init.d/media-storage'))
subprocess.check_call(('/usr/sbin/update-rc.d', 'media-storage', 'defaults',))

