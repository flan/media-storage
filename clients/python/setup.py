#!/usr/bin/env python
"""
Deployment script for the media-storage client.
"""
__author__ = 'Neil Tallim'

from distutils.core import setup

setup(
 name = 'media-storage',
 version = '0.9.0',
 description = 'Python bindings for the media-storage system',
 author = 'Neil Tallim',
 author_email = 'neil.tallim@linux.com',
 license = 'LGPLv3',
 url = 'http://code.google.com/p/media-storage/',
 packages = [
  'media_storage',
 ],
)

