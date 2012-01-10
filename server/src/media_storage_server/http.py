"""
media-storage.http
==================

Provides all logic needed to support the system's webservice interface.

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
import base64
import collections
import json
import logging
import os
import random
import re
import tempfile
import threading
import time
import traceback
import types
import uuid

import pymongo
import tornado.httpserver
import tornado.ioloop
import tornado.web

from config import CONFIG
import compression
import database
import mail
import filesystem
import state

_CHUNK_SIZE = 16 * 1024 #Write 16k at a time.
_TEMPFILE_THRESHOLD = 128 * 1024 #Buffer up to 128k in memory

_FILTER_RE = re.compile(r':(?P<filter>.+?):(?P<query>.+)')

_TrustLevel = collections.namedtuple('TrustLevel', ('read', 'write',))

_logger = logging.getLogger("media_storage.http")

def _get_trust(record, keys, host):
    """
    Determines which permissions to expose for a record, returning the result as a namedtuple with
    ``read`` and ``write`` booleans.
    
    `record` is the record being evaluated and `keys` is a dictionary containing any of
    ('read', 'write'), which may be omitted or ``None`` to force evaluation against anonymous
    access. `host` is the address from which the client is connecting; if in the system-wide trust
    list, all permissions are immediately granted.
    """
    for trusted in CONFIG.security_trusted_hosts.split():
        if host == trusted:
            _logger.debug("Request received from trusted host %(host)s" % {
             'host': host,
            })
            return _TrustLevel(True, True)
    if not record: #If `record` is omitted, the test is to see if the host is trusted globally
        return _TrustLevel(False, False)
        
    return _TrustLevel(
     record['keys']['read'] is None or keys and record['keys']['read'] == keys.get('read'),
     record['keys']['write'] is None or keys and record['keys']['write'] == keys.get('write'),
    )
    
def _get_json(body):
    """
    Converts the JSON `body` of a request into a Python data structure.
    """
    try:
        return json.loads(body or 'null')
    except ValueError as e:
        _logger.warn(str(e))
        raise
        
def _unpack_policy(policy):
    """
    Given a `policy` section from a storage or update request, converts the data structure into
    something sutiable for the database, adding appropriate timestamps and optimised fields as
    needed.
    """
    new_policy = {}
    current_time = int(time.time())
    
    expiration = policy.get('fixed')
    if expiration:
        new_policy['fixed'] = current_time + int(expiration)
        
    stale = policy.get('stale')
    if stale:
        stale = int(stale)
        new_policy['stale'] = stale
        new_policy['staleTime'] = current_time + stale
        
    return new_policy
    
    
class BaseHandler(tornado.web.RequestHandler):
    """
    A generalised request-handler for inbound communication.
    
    Responds with one of the following codes::
    
    - 200 if everything went well
    - 404 if the requested resource was unavailable
    - 409 if the request made no sense
    - 500 if an internal exception happened
    - 503 if a short-term problem occurred
    """
    def send_error(self, code, **kwargs):
        _logger.info("Request from %(address)s served with failure code %(code)i" % {
         'address': self.request.remote_ip,
         'code': code,
        })
        tornado.web.RequestHandler.send_error(self, code, **kwargs)
        
    def post(self):
        """
        Handles an HTTP POST request.
        """
        _logger.info("Received an HTTP POST request for '%(path)s' from %(address)s" % {
         'path': self.request.path,
         'address': self.request.remote_ip,
        })
        try:
            _logger.debug("Processing request...")
            output = self._post()
        except filesystem.Error as e:
            summary = "Filesystem error; exception details follow:\n" + traceback.format_exc()
            _logger.critical(summary)
            mail.send_alert(summary)
            self.send_error(500)
        except pymongo.errors.AutoReconnect:
            summary = "Database unavailable; exception details follow:\n" + traceback.format_exc()
            _logger.error(summary)
            mail.send_alert(summary)
            self.send_error(503)
        except Exception as e:
            summary = "Unknown error; exception details follow:\n" + traceback.format_exc()
            _logger.error(summary)
            mail.send_alert(summary)
            self.send_error(500)
        else:
            _logger.debug("Responding to request...")
            try:
                if not output is None:
                    self.write(output)
                self.finish()
            except Exception as e:
                _logger.error("Unknown error when writing response; exception details follow:\n" + traceback.format_exc())
                
    def _post(self):
        """
        Returns the current time; override this to do useful things.
        """
        return {
         'timestamp': int(time.time()),
         'note': "This timestamp is in UTC; thanks for POSTing",
        }
        
        
class PingHandler(BaseHandler):
    def _post(self):
        return {
         'online': True,
        }
        
class ListFamiliesHandler(BaseHandler):
    def _post(self):
        families = set(database.list_families()).union(state.get_families())
        families.discard(None)
        return {
         'families': sorted(families),
        }
        
class PutHandler(BaseHandler):
    def _post(self):
        (header, data) = self._get_payload()
        
        current_time = time.time()
        try:
            _logger.debug("Assembling database record...")
            record = {
             '_id': header.get('uid') or uuid.uuid1().hex,
             'keys': self._build_keys(header),
             'physical': {
              'family': header['physical'].get('family'),
              'ctime': current_time,
              'minRes': CONFIG.storage_minute_resolution,
              'atime': int(current_time),
              'format': self._build_format(header),
             },
             'policy': self._build_policy(header),
             'stats': {
              'accesses': 0,
             },
             'meta': header.get('meta') or {},
            }
        except (KeyError, TypeError, AttributeError) as e:
            _logger.error("Request received did not adhere to expected structure: %(error)s" % {
             'error': str(e),
            })
            self.send_error(409)
            return
        else:
            _logger.info("Proceeding with storage request for '%(uid)s'..." % {
             'uid': record['_id'],
            })
            
        _logger.debug("Evaluating compression requirements...")
        target_compression = record['physical']['format'].get('comp')
        if target_compression and self.request.headers.get('Media-Storage-Compress-On-Server') == 'yes':
            _logger.info("Compressing file...")
            data = compression.get_compressor(target_compression)(data)
            
        _logger.debug("Storing entity...")
        database.add_record(record)
        fs = state.get_filesystem(record['physical']['family'])
        fs.put(record, data)
        
        return {
         'uid': record['_id'],
         'keys': record['keys'],
        }
        
    def _get_payload(self):
        """
        Depending on whether the request came through an nginx proxy, this will determine the right
        way to expose the received data. Regardless of method, the values returned will be a JSON
        object descriptor and a file-like object containing the submitted bytes.
        """
        header = _get_json(self.get_argument('header', ''))
        content=None
        if self.get_argument('nginx', None): #nginx proxy
            _logger.debug("Extracting payload from nginx proxy structure...")
            filepath = self.get_argument('content', None)
            if not filepath:
                raise IOError("No file specified by nginx")
            content = open(filepath, 'rb')
            try:
                _logger.debug("Unlinking nginx tempfile...")
                os.unlink(filepath) #Reclaim space when the handle is closed
            except Exception as e:
                _logger.error("Unable to reclaim space used by nginx tempfile '%(path)s' (media-storage and nginx should run as the same user): %(error)s" % {
                 'path': filepath,
                 'error': str(e),
                })
        else:
            _logger.debug("Extracting payload from Tornado structure...")
            content = tempfile.SpooledTemporaryFile(_TEMPFILE_THRESHOLD)
            content.write(self.request.files['content'][0]['body'])
            content.flush()
            content.seek(0)
        return (header, content)
        
    def _build_keys(self, header):
        keys = header.get('keys')
        return {
         'read': keys and keys.get('read') or base64.urlsafe_b64encode(os.urandom(random.randint(5, 10)))[:-2],
         'write': keys and keys.get('write') or base64.urlsafe_b64encode(os.urandom(random.randint(5, 10)))[:-2],
        }
        
    def _build_format(self, header):
        format = {
         'mime': header['physical']['format']['mime'],
        }
        
        target_compression = header['physical']['format'].get('comp')
        if target_compression:
            format['comp'] = target_compression
            
        return format
        
    def _build_policy(self, header):
        policy = {
         'delete': {},
         'compress': {},
        }
        
        header_policy = header.get('policy')
        if header_policy:
            delete_policy = header_policy.get('delete')
            if delete_policy:
                policy['delete'].update(_unpack_policy(delete_policy))
                
            compress_policy = header_policy.get('compress')
            if compress_policy:
                compress_format = compress_policy.get('comp')
                if compress_format in compression.SUPPORTED_FORMATS:
                    policy['compress']['comp'] = compress_format
                    policy['compress'].update(_unpack_policy(compress_policy))
                else:
                    _logger.warn("Unsupported compression format specified: %(format)s" % {
                     'format': compress_format,
                    })
                    
        return policy
        
class DescribeHandler(BaseHandler):
    def _post(self):
        request = _get_json(self.request.body)
        uid = request['uid']
        _logger.info("Proceeding with description request for '%(uid)s'..." % {
         'uid': uid,
        })
        
        record = database.get_record(uid)
        if not record:
            self.send_error(404)
            return
            
        trust = _get_trust(record, request.get('keys'), self.request.remote_ip)
        if not trust.read:
            self.send_error(403)
            return
            
        _logger.debug("Describing entity...")
        del record['physical']['minRes']
        del record['keys']
        return record
        
class GetHandler(BaseHandler):
    def _post(self):
        request = _get_json(self.request.body)
        uid = request['uid']
        _logger.info("Proceeding with retrieval request for '%(uid)s'..." % {
         'uid': uid,
        })
        
        record = database.get_record(uid)
        if not record:
            self.send_error(404)
            return
            
        trust = _get_trust(record, request.get('keys'), self.request.remote_ip)
        if not trust.read:
            self.send_error(403)
            return
            
        current_time = int(time.time())
        record['physical']['atime'] = current_time
        record['stats']['accesses'] += 1
        for policy in ('delete', 'compress'):
            if 'stale' in record['policy'][policy]:
                record['policy'][policy]['staleTime'] = current_time + record['policy'][policy]['stale']
        database.update_record(record)
        
        fs = state.get_filesystem(record['physical']['family'])
        try:
            data = fs.get(record)
        except filesystem.FileNotFoundError as e:
            _logger.error("Database record exists for '%(uid)s', but filesystem entry does not" % {
             'uid': uid,
            })
            self.send_error(404)
            return
        else:
            _logger.debug("Evaluating decompression requirements...")
            applied_compression = record['physical']['format'].get('comp')
            supported_compressions = (c.strip() for c in (self.request.headers.get('Media-Storage-Supported-Compression') or '').split(';'))
            if applied_compression and not applied_compression in supported_compressions: #Must be decompressed first
                data = compression.get_decompressor(applied_compression)(data)
                applied_compression = None
                
            _logger.debug("Returning entity...")
            self.set_header('Content-Type', record['physical']['format']['mime'])
            if applied_compression:
                self.set_header('Media-Storage-Applied-Compression', applied_compression)
            while True:
                chunk = data.read(_CHUNK_SIZE)
                if chunk:
                    self.write(chunk)
                else:
                    break
                    
class UnlinkHandler(BaseHandler):
    def _post(self):
        request = _get_json(self.request.body)
        uid = request['uid']
        _logger.info("Proceeding with unlink request for '%(uid)s'..." % {
         'uid': uid,
        })
        
        record = database.get_record(uid)
        if not record:
            self.send_error(404)
            return
            
        trust = _get_trust(record, request.get('keys'), self.request.remote_ip)
        if not trust.write:
            self.send_error(403)
            return
        
        fs = state.get_filesystem(record['physical']['family'])
        try:
            fs.unlink(record)
        except filesystem.FileNotFoundError as e:
            _logger.error("Database record exists for '%(uid)s', but filesystem entry does not" % {
             'uid': uid,
            })
            self.send_error(404)
            return
        else:
            database.drop_record(uid)
            
class UpdateHandler(BaseHandler):
    def _post(self):
        request = _get_json(self.request.body)
        uid = request['uid']
        _logger.info("Proceeding with unlink request for '%(uid)s'..." % {
         'uid': uid,
        })
        
        record = database.get_record(uid)
        if not record:
            self.send_error(404)
            return
            
        trust = _get_trust(record, request.get('keys'), self.request.remote_ip)
        if not trust.write:
            self.send_error(403)
            return
            
        self._update_policy(record, request)
        
        for removed in request['meta']['removed']:
            if removed in record['meta']:
                del record['meta'][removed]
        record['meta'].update(request['meta']['new'])
        
        database.update_record(record)
        
    def _update_policy(self, record, request):
        request_policy = request.get('policy')
        if request_policy:
            policy = record['policy']
            
            delete_policy = request_policy.get('delete')
            if not delete_policy is None:
                policy['delete'] = _unpack_policy(delete_policy)
                
            compress_policy = request_policy.get('compress')
            if not compress_policy is None:
                compress_format = compress_policy.get('comp')
                if compress_format in compression.SUPPORTED_FORMATS:
                    policy['compress'] = _unpack_policy(compress_policy)
                    policy['compress']['comp'] = compress_format
                else:
                    _logger.warn("Unsupported compression format specified: %(format)s" % {
                     'format': compress_format,
                    })
                    
class QueryHandler(BaseHandler):
    def _post(self):
        request = _get_json(self.request.body)
        
        query = {}
        trust = _get_trust(None, None, self.request.remote_ip)
        if not trust.read:
            query['keys.read'] = None #Anonymous records only
            
        def _assemble_block(name, attribute):
            attribute_block = {}
            _min = request[name]['min']
            _max = request[name]['max']
            _block = {}
            if _min:
                attribute_block['$gte'] = _min
            if _max:
                attribute_block['$lte'] = _max
            if attribute_block:
                query[attribute] = attribute_block
        _assemble_block('ctime', 'physical.ctime')
        _assemble_block('atime', 'physical.atime')
        _assemble_block('accesses', 'stats.accesses')
        
        query['physical.family'] = request['family']
        
        mime = request['mime']
        if mime:
            if '/' in mime:
                query['physical.mime'] = mime
            else:
                query['physical.mime'] = {'$regex': '^' + mime}
                
        for (key, value) in request['meta'].items():
            key = 'meta.' + key
            
            if type(value) in types.StringTypes:
                if value.startswith('::'):
                    value = value[1:]
                else:
                    match = _FILTER_RE.match(value)
                    if match:
                        filter = match.group('filter')
                        query = match.group('query')
                        if filter == 'range':
                            (_min, _max) = (float(v) for v in query.split(':', 1))
                            value = {'$gte': _min, '$lte': _max}
                        elif filter == 'lte':
                            value = {'$lte': float(query)}
                        elif filter == 'gte':
                            value = {'$gte': float(query)}
                        elif filter == 're':
                            value = {'$regex': query}
                        elif filter == 're':
                            value = {'$regex': query}
                        elif filter == 're.i':
                            value = {'$regex': query, '$options': 'i'}
                        elif filter == 'like':
                            if query.count('%') == 1 and query.endswith('%'):
                                value = {'$regex': '^' + query[:-1]}
                            else:
                                value = {'$regex': '^' + query.replace('%', '.*') + '$'}
                        elif filter == 'ilike':
                            value = {'$regex': '^' + query.replace('%', '.*') + '$', '$options': 'i'}
                        else:
                            raise ValueError("Unrecognised filter: %(filter)s" % {
                             'filter': filter,
                            })
            query[key] = value
            
        records = []
        for record in database.enumerate_where(query):
            if not trust.read:
                del record['keys']
            else:
                record['physical']['path'] = state.get_filesystem(request['family']).resolve_path(record)
            del record['physical']['minRes']
            records.append(record)
        return {
         'records': records,
        }
        
class StatusHandler(BaseHandler):
    def _post(self):
        process = psutil.Process(os.getpid())
        return {
         'process': {
          'cpu': {
           'percent': process.get_cpu_percent() / 100.0,
          },
          'memory': {
           'percent': process.get_memory_percent() / 100.0,
           'rss': process.get_memory_info().rss,
          },
          'threads': process.get_num_threads(),
         },
         'system': {
          'load': dict(zip(('t1', 't5', 't15'), os.getloadavg())),
         },
         'families': sorted(state.get_families()),
        }
        
        
class HTTPService(threading.Thread):
    """
    A threaded handler for HTTP requests, so that client interaction can happen in parallel with
    other processing.
    
    Starts with `start()` and executes until `kill()` is invoked.
    """
    _http_application = None #The Tornado HTTP application code to be driven
    _http_server = None #The Tornado HTTP server instance
    _http_loop = None #The Tornado IOLoop instance
    
    def __init__(self, port, handlers, daemon=True):
        """
        Sets up and binds the HTTP server. All interfaces are glommed, though a port must be
        specified. The thread is run in daemon mode by default.
        
        `handlers` is a collection of tuples that connect a string or regular expression object that
        represents a path and a subclass of "BaseHandler".
        """
        threading.Thread.__init__(self)
        self.daemon = daemon
        self.name = "http"
        
        _logger.info("Configuring HTTP server on port %(port)i..." % {
         'port': port,
        })
        self._http_loop = tornado.ioloop.IOLoop.instance()
        self._http_application = tornado.web.Application(handlers, log_function=(lambda x:''), xheaders=True)
        self._http_server = tornado.httpserver.HTTPServer(self._http_application)
        self._http_server.listen(port)
        
        _logger.info("Configured HTTP server")
        
    def kill(self):
        """
        Ends execution of the HTTP server, allowing the thread to die.
        """
        _logger.info("HTTP server's kill-flag set")
        self._http_loop.stop()
        
    def run(self):
        """
        Continuously accepts requests until killed; any exceptions that occur are logged.
        """
        _logger.info("Starting Tornado HTTP server engine...")
        self._http_loop.start()
        _logger.info("Tornado HTTP server engine terminated")
        
