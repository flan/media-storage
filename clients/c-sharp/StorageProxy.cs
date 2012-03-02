//
//  Author:
//       Neil Tallim <flan@uguu.ca>
// 
//  Copyright (c) 2012 Neil Tallim
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
    public class StorageProxy : BaseClient{
        private string media_server_host;
        private ushort media_server_port;

        /// <summary>
        /// Initializes a new instance of the <see cref="MediaStorage.StorageProxy"/> class.
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
        public StorageProxy(string server_host, ushort server_port, ushort proxy_port){
            this.media_server_host = server_host;
            this.media_server_port = server_port;
            this.server = string.Format("http://localhost:{0}/", proxy_port);
        }

        /// <summary>
        /// Stores the content of <c>data</c> in the proxy's buffers, returning information about how to access it later.
        ///
        /// It is important to note that the data is NOT actually stored when this pointer is returned,
        /// but rather that the pointer will be valid at some point in the future (typically very soon,
        /// but not within a predictable timeframe).
        /// </summary>
        /// <param name='data'>
        /// The path to the content to be stored.
        /// </param>
        /// <param name='mime'>
        /// The MIME-type of the content being stored.
        /// </param>
        /// <param name='family'>
        /// The case-sensitive, arbitrary family to which the data belongs; defaults to <c>null</c>, for the
        /// generic family.
        /// </param>
        /// <param name='compression'>
        /// The type of compression to apply when storing the file; defaults to <c>COMPRESSION.NONE</c>
        /// </param>
        /// <param name='compress_on_server'>
        /// Indicates whether the proxy should require the server to perform compression, rather than trying
        /// locally; defaults to <c>false</c>.
        /// </param>
        /// <param name='deletion_policy'>
        /// May either be <c>null</c>, the default, which means the file is never deleted (default) or a
        /// dictionary containing one or both of the following:
        /// <list>
        ///     <item>'fixed': The number of seconds to retain the file from the time it was uploaded</item>
        ///     <item>'stale': The number of seconds that must elapse after the file was last downloaded to qualify it for deletion</item>
        /// </list>
        /// </param>
        /// <param name='compression_policy'>
        /// May either be <c>null</c>, the default, which means the file is never compressed (default) or a
        /// dictionary containing one or both of the following:
        /// <list>
        ///     <item>'fixed': The number of seconds to leave the file alone from the time it was uploaded</item>
        ///     <item>'stale': The number of seconds that must elapse after the file was last downloaded to qualify it for compression</item>
        /// </list>
        /// </param>
        /// <param name='compression_policy_format'>
        /// The format into which the file will be compressed once the compression policy activates; defaults to <c>COMPRESSION.NONE</c>.
        /// </param>
        /// <param name='meta'>
        /// Any additional metadata with which to tag the file; defaults to <c>null</c>, meaning no metadata.
        /// </param>
        /// <param name='uid'>
        /// If not implementing a proxy, leave this value at its default of <c>null</c> to have an identifier auto-generated or pick something that
        /// has no chance of colliding with a UUID(1).
        /// </param>
        /// <param name='keys'>
        /// In general, you should not need to specify anything, leaving it at <c>null</c>, but if you have a homogenous
        /// or anonymous access policy, it is a dictionary containing the elements 'read' and 'write',
        /// both strings or <c>null</c>, with <c>null</c> granting anonymous access to the corresponding facet.
        ///
        /// Either element may be omitted to have it generated by the server.
        /// </param>
        /// <param name='timeout'>
        /// The number of seconds to wait for a response; defaults to 3.
        /// </param>
        /// <exception cref="System.Exception">
        /// Some unknown problem occurred.
        /// </exception>
        /// <exception cref="MediaStorage.HttpError">
        /// A problem occurred related to the transport protocol.
        /// </exception>
        /// <exception cref="MediaStorage.UrlError">
        /// A problem occurred related to the network environment.
        /// </exception>
        public System.Collections.Generic.IDictionary<string, object> Put(
         string data, string mime, string family=null,
         COMPRESSION compression=COMPRESSION.NONE, bool compress_on_server=false,
         System.Collections.Generic.IDictionary<string, long> deletion_policy=null,
         System.Collections.Generic.IDictionary<string, long> compression_policy=null,
         COMPRESSION compression_policy_format=COMPRESSION.NONE,
         System.Collections.Generic.IDictionary<string, object> meta=null,
         string uid=null, System.Collections.Generic.IDictionary<string, string> keys=null,
         float timeout=3.0f
        ){
            Jayrock.Json.JsonObject put = new Jayrock.Json.JsonObject();
            put.Add("uid", uid);
            put.Add("keys", keys);
            put.Add("meta", meta);

            Jayrock.Json.JsonObject physical = new Jayrock.Json.JsonObject();
            physical.Add("family", family);

            Jayrock.Json.JsonObject format = new Jayrock.Json.JsonObject();
            format.Add("mime", mime);
            format.Add("comp", compression != COMPRESSION.NONE ? compression.ToString().ToLower() : null);
            physical.Add("format", format);
            put.Add("physical", physical);

            Jayrock.Json.JsonObject policy = new Jayrock.Json.JsonObject();
            policy.Add("delete", deletion_policy);
            System.Collections.Generic.Dictionary<string, object> comp_policy = (System.Collections.Generic.Dictionary<string, object>)compression_policy;
            if(compression_policy != null){
                comp_policy.Add("comp", compression_policy_format != COMPRESSION.NONE ? compression_policy_format.ToString().ToLower() : null);
            }
            policy.Add("compression", comp_policy);
            physical.Add("policy", policy);

            Jayrock.Json.JsonObject proxy = new Jayrock.Json.JsonObject();

            Jayrock.Json.JsonObject server = new Jayrock.Json.JsonObject();
            server.Add("host", this.media_server_host);
            server.Add("port", this.media_server_port);
            proxy.Add("server", server);

            proxy.Add("data", data);

            put.Add("proxy", proxy);

            System.Net.HttpWebRequest request = MediaStorage.Libraries.Communication.AssembleRequest(this.server + Libraries.Communication.SERVER_PUT, put);
            Libraries.Communication.Response response = MediaStorage.Libraries.Communication.SendRequest(request, timeout:timeout);
            return response.ToJson();
        }
    }
}
