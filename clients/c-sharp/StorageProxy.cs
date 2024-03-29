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
    /// A means of accessing a service running on localhost that buffers storage requests, allowing for
    /// both fast and fault-tolerant archival of content, provided that synchronous transactions are not
    /// a requirement of the usage domain.
    /// </summary>
    public class StorageProxy : AbstractBaseClient{
        /// <summary>
        /// The address of the media-storage proxy.
        /// </summary>
        private string proxy;

        /// <summary>
        /// Initializes a new instance of the <see cref="StorageProxy"/> class.
        /// </summary>
        /// <param name='server'>
        /// The details of the media-storage server.
        /// </param>
        /// <param name='proxy_port'>
        /// The port on which the media-storage proxy is listening.
        /// </param>
        public StorageProxy(Server server, ushort proxy_port){
            this.server = server;
            this.proxy = string.Format("http://localhost:{0}/", proxy_port);
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
        /// May either be <c>null</c>, the default, which means the file is never removed or a <see cref="Structures.DeletionPolicy"/>
        /// instance.
        /// </param>
        /// <param name='compression_policy'>
        /// May either be <c>null</c>, the default, which means the file is never compressed or a <see cref="Structures.CompressionPolicy"/>
        /// instance.
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
        /// or anonymous access policy, a <see cref="Structures.Keys"/> instance may be used, with either key set to an arbitrary string or
        /// <c>null</c>, with <c>null</c> granting anonymous access to the corresponding facet.
        ///
        /// Either element may be omitted to have it generated by the server.
        /// </param>
        /// <param name='timeout'>
        /// The number of seconds to wait for a response; defaults to 3.
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
        public Structures.Storage Put(
         string data, string mime, string family=null,
         COMPRESSION compression=COMPRESSION.NONE, bool compress_on_server=false,
         Structures.DeletionPolicy deletion_policy=null,
         Structures.CompressionPolicy compression_policy=null,
         COMPRESSION compression_policy_format=COMPRESSION.NONE,
         System.Collections.Generic.IDictionary<string, object> meta=null,
         string uid=null, Structures.Keys keys=null,
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
            policy.Add("delete", deletion_policy != null ? deletion_policy.ToDictionary() : null);
            policy.Add("compress", compression_policy != null ? compression_policy.ToDictionary() : null);
            put.Add("policy", policy);

            Jayrock.Json.JsonObject proxy = new Jayrock.Json.JsonObject();
            proxy.Add("server", this.server.ToDictionary());
            proxy.Add("data", data);
            put.Add("proxy", proxy);

            System.Net.HttpWebRequest request = Libraries.Communication.AssembleRequest(this.proxy + Libraries.Communication.SERVER_PUT, put);
            return new Structures.Storage(Libraries.Communication.SendRequest(request, timeout:timeout).ToDictionary());
        }
		
		/// <summary>
		/// Provides the address of the server to access for queries.
		/// </summary>
		internal override string GetServer(){
			return this.proxy;
		}
    }
}
