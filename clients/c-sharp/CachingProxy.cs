//
//  Author:
//       Neil Tallim <flan@uguu.ca>
// 
//  Copyright (c) 2012 Ivrnet, inc.
// 
//  This library is free software; you can redistribute it and/or modify
//  it under the terms of the GNU Lesser General Public License as
//  published by the Free Software Foundation; either version 2.1 of the
//  License, or (at your option) any later version.
// 
//  This library is distributed in the hope that it will be useful, but
//  WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
//  Lesser General Public License for more details.
// 
//  You should have received a copy of the GNU Lesser General Public
//  License along with this library; if not, write to the Free Software
//  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

namespace MediaStorage{
    /// <summary>
    /// A means of accessing a service running on localhost that pulls files from a central server and
    /// caches them locally for frequent re-use. Data is made available synchronously.
    /// </summary>
    public class CachingProxy : AbstractBaseClient, Interfaces.RetrievalConstruct{
        /// <summary>
        /// The address of the media-storage server.
        /// </summary>
        private string media_server_host;
        /// <summary>
        /// The port of the media-storage server.
        /// </summary>
        private ushort media_server_port;

        /// <summary>
        /// Initializes a new instance of the <see cref="CachingProxy"/> class.
        /// </summary>
        /// <param name='server_host'>
        /// The address of the media-storage server.
        /// </param>
        /// <param name='server_port'>
        /// The port on which the media-storage server is listening.
        /// </param>
        /// <param name='proxy_port'>
        /// The port on which the media-storage proxy is listening.
        /// </param>
        public CachingProxy(string server_host, ushort server_port, ushort proxy_port){
            this.media_server_host = server_host;
            this.media_server_port = server_port;
            this.server = string.Format("http://localhost:{0}/", proxy_port);
        }

        /// <summary>
        /// Retrieves the requested data from the cache.
        /// </summary>
        /// <returns>
        /// Returns the content's MIME and the decompressed data as a stream (optionally that
        /// supplied as <c>output_file</c>), along with the length of the content in bytes.
        /// </returns>
        /// <param name='uid'>
        /// The UID of the record to be retrieved.
        /// </param>
        /// <param name='read_key'>
        /// A token that grants permission to read the record.
        /// </param>
        /// <param name='output_file'>
        /// An optional stream into which retrieved content may be written; if <c>null</c>, the
        /// default, an on-disk, self-cleaning tempfile, is used instead.
        /// </param>
        /// <param name='decompress_on_server'>
        /// Ignored, since this decision is up to the proxy.
        /// </param>
        /// <param name='timeout'>
        /// The number of seconds to wait for a response; defaults to 5.
        /// </param>
        /// <exception cref="System.Exception">
        /// Some unknown problem occurred.
        /// </exception>
        /// <exception cref="Exceptions.ProtocolError">
        /// A problem occurred related to the transport protocol.
        /// </exception>
        /// <exception cref="Exceptions.UrlError">
        /// A problem occurred related to the network environment.
        /// </exception>
        /// <exception cref="Exceptions.NotFoundError">
        /// The requested record was not found.
        /// </exception>
        /// <exception cref="Exceptions.NotAuthorisedError">
        /// The requested record was not accessible with the given credentials.
        /// </exception>
        public Structures.Internal.Content Get(string uid, string read_key, System.IO.Stream output_file=null, bool decompress_on_server=false, float timeout=5.0f){
            Jayrock.Json.JsonObject get_json = new Jayrock.Json.JsonObject();
            get_json.Add("uid", uid);

            Jayrock.Json.JsonObject keys = new Jayrock.Json.JsonObject();
            keys.Add("read", read_key);
            get_json.Add("keys", keys);

            Jayrock.Json.JsonObject proxy = new Jayrock.Json.JsonObject();

            Jayrock.Json.JsonObject server = new Jayrock.Json.JsonObject();
            server.Add("host", this.media_server_host);
            server.Add("port", (int)this.media_server_port);
            proxy.Add("server", server);
            get_json.Add("proxy", proxy);

            System.Net.HttpWebRequest request = Libraries.Communication.AssembleRequest(this.server + Libraries.Communication.SERVER_GET, get_json);
            Libraries.Communication.Response response = Libraries.Communication.SendRequest(request, timeout:timeout);

            Structures.Internal.Content content = new Structures.Internal.Content();
            if(output_file != null){
                content.Data = output_file;
            }else{
                content.Data = new Libraries.TempFileStream();
            }
            response.Data.CopyTo(content.Data);
            content.Length = content.Data.Length;
            content.Data.Seek(0, System.IO.SeekOrigin.Begin);
            content.Mime = (string)response.Properties[Libraries.Communication.PROPERTY_CONTENT_TYPE];

            return content;
        }

        /// <summary>
        /// Retrieves details about the requested record from the cache.
        ///
        /// The provided details may not be entirely current, since cached copies will be used when possible.
        /// </summary>
        /// <param name='uid'>
        /// The UID of the record to be read.
        /// </param>
        /// <param name='read_key'>
        /// A token that grants permission to read the record.
        /// </param>
        /// <param name='timeout'>
        /// The number of seconds to wait for a response; defaults to 2.5.
        /// </param>
        /// <exception cref="System.Exception">
        /// Some unknown problem occurred.
        /// </exception>
        /// <exception cref="Exceptions.ProtocolError">
        /// A problem occurred related to the transport protocol.
        /// </exception>
        /// <exception cref="Exceptions.UrlError">
        /// A problem occurred related to the network environment.
        /// </exception>
        /// <exception cref="Exceptions.NotFoundError">
        /// The requested record was not found.
        /// </exception>
        /// <exception cref="Exceptions.NotAuthorisedError">
        /// The requested record was not accessible with the given credentials.
        /// </exception>
        public Structures.Internal.Description Describe(string uid, string read_key, float timeout=2.5f){
            Jayrock.Json.JsonObject describe = new Jayrock.Json.JsonObject();
            describe.Add("uid", uid);

            Jayrock.Json.JsonObject keys = new Jayrock.Json.JsonObject();
            keys.Add("read", read_key);
            describe.Add("keys", keys);

            Jayrock.Json.JsonObject proxy = new Jayrock.Json.JsonObject();

            Jayrock.Json.JsonObject server = new Jayrock.Json.JsonObject();
            server.Add("host", this.media_server_host);
            server.Add("port", (int)this.media_server_port);
            proxy.Add("server", server);

            describe.Add("proxy", proxy);

            System.Net.HttpWebRequest request = Libraries.Communication.AssembleRequest(this.server + Libraries.Communication.SERVER_DESCRIBE, describe);
            return new Structures.Internal.Description(Libraries.Communication.SendRequest(request, timeout:timeout).ToDictionary());
        }
    }
}
