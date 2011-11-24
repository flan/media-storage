"""
Provides all resources needed for the HTTP interface.
"""
import compression
import database
import state

_CHUNK_SIZE = 16 * 1024 #Write 16k at a time.

#/get/<uid>
class GetHandler(BaseHandler):
    def _get(self):
        uid = self.request.path[request.path.rfind('/') + 1:]
        record = database.get_record(uid)
        if not record:
            #404
            
        filesystem = state.get_filesystem(record['physical']['family'])
        try:
            data = filesystem.get(record)
        except filesystem.FileNotFoundError as e:
            #log
            #404
        else:
            applied_compression = record['physical']['format'].get('comp')
            supported_compressions = (c.strip() for c in (self.request.headers.get('Ivr-Supported-Compression') or '').split(';'))
            if applied_compression and not applied_compression in supported_compressions: #Must be decompressed first
                #log
                decompressor = getattr(compression, 'decompress_' + applied_compression)
                data = decompressor(data)
                applied_compression = None
                
            self.headers['Content-Type'] = record['physical']['format']['mime']
            self.headers['Content-Length'] = str(filesystem.file_size(record))
            while True:
                chunk = data.read(_CHUNK_SIZE)
                if chunk:
                    self.write(chunk)
                    self.flush()
                else:
                    break
            self.close()
            self.finish()
            
