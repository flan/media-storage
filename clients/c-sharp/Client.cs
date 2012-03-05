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
    /// Provides direct access to a media-storage server; appropriate for most deployments.
    /// </summary>
    public class Client : BaseClient, Interfaces.ControlConstruct{
        /// <summary>
        /// Initializes a new instance of the <see cref="MediaStorage.Client"/> class.
        /// </summary>
        /// <param name='server_host'>
        /// The address of the media-storage server.
        /// </param>
        /// <param name='server_port'>
        /// The port on which the media-storage server is listening.
        /// </param>
        public Client(string server_host, ushort server_port){
            this.server = string.Format("http://{0}:{1}/", server_host, server_port);
        }

        /// <summary>
        /// Requests load data from the server.
        /// </summary>
        /// <returns>
        /// A JSON-derived data-structure as follows:
        /// <code>
        /// 'process': {
        ///  'cpu': {'percent': 0.1,},
        ///  'memory': {'percent': 1.2, 'rss': 8220392,},
        ///  'threads': 4,
        /// },
        /// 'system': {
        ///  'load': {'t1': 0.2, 't5': 0.5, 't15': 0.1,},
        /// }
        /// </code>
        /// </returns>
        /// <param name='timeout'>
        /// The number of seconds to wait for a response; defaults to 2.5.
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
        public System.Collections.Generic.IDictionary<string, object> Status(float timeout=2.5f){
            System.Net.HttpWebRequest request = MediaStorage.Libraries.Communication.AssembleRequest(this.server + Libraries.Communication.SERVER_STATUS, new System.Collections.Generic.Dictionary<string, object>());
            return MediaStorage.Libraries.Communication.SendRequest(request, timeout:timeout).ToJson();
        }

        /// <summary>
        /// Lists all known families.
        /// </summary>
        /// <returns>
        /// A list of all known families, in alphabetical order.
        /// </returns>
        /// <param name='timeout'>
        /// The number of seconds to wait for a response; defaults to 2.5.
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
        public System.Collections.Generic.IList<string> ListFamilies(float timeout=2.5f){
            System.Net.HttpWebRequest request = MediaStorage.Libraries.Communication.AssembleRequest(this.server + Libraries.Communication.SERVER_LIST_FAMILIES, new System.Collections.Generic.Dictionary<string, object>());
            System.Collections.Generic.List<string> families = new System.Collections.Generic.List<string>();
            foreach(object family in (System.Collections.Generic.IList<object>)MediaStorage.Libraries.Communication.SendRequest(request, timeout:timeout).ToJson()["families"]){
                families.Add(family.ToString());
            }
            return families;
        }

        /// <summary>
        /// Stores the content of <c>data</c> on the server, returning information about how to access it later.
        /// </summary>
        /// <param name='data'>
        /// The content to be stored.
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
        /// Indicates whether the client should require the server to perform compression, rather than trying
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
        /// The number of seconds to wait for a response; defaults to 10.
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
         System.IO.Stream data, string mime, string family=null,
         COMPRESSION compression=COMPRESSION.NONE, bool compress_on_server=false,
         System.Collections.Generic.IDictionary<string, ulong> deletion_policy=null,
         System.Collections.Generic.IDictionary<string, ulong> compression_policy=null,
         COMPRESSION compression_policy_format=COMPRESSION.NONE,
         System.Collections.Generic.IDictionary<string, object> meta=null,
         string uid=null, System.Collections.Generic.IDictionary<string, string> keys=null,
         float timeout=10.0f
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

            System.Collections.Generic.Dictionary<string, string> headers = new System.Collections.Generic.Dictionary<string, string>();
            if(!compress_on_server){
                try{
                    data = Libraries.Compression.GetCompressor(compression).Invoke(data);
                    headers.Add(Libraries.Communication.HEADER_COMPRESS_ON_SERVER, Libraries.Communication.HEADER_COMPRESS_ON_SERVER_FALSE);
                }catch(System.Exception){
                    headers.Add(Libraries.Communication.HEADER_COMPRESS_ON_SERVER, Libraries.Communication.HEADER_COMPRESS_ON_SERVER_TRUE);
                }
            }else{
                headers.Add(Libraries.Communication.HEADER_COMPRESS_ON_SERVER, Libraries.Communication.HEADER_COMPRESS_ON_SERVER_TRUE);
            }

            System.Net.HttpWebRequest request = MediaStorage.Libraries.Communication.AssembleRequest(this.server + Libraries.Communication.SERVER_PUT, physical, headers:headers, data:data);
            Libraries.Communication.Response response = MediaStorage.Libraries.Communication.SendRequest(request, timeout:timeout);
            return response.ToJson();
        }

        /// <summary>
        /// Retrieves the requested data from the server.
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
        /// Favours decompression of content on the server; defaults to <c>false</c>.
        /// </param>
        /// <param name='timeout'>
        /// The number of seconds to wait for a response; defaults to 5.
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
        public MediaStorage.Interfaces.Content Get(string uid, string read_key, System.IO.Stream output_file=null, bool decompress_on_server=false, float timeout=5.0f){
            Jayrock.Json.JsonObject get_json = new Jayrock.Json.JsonObject();
            get_json.Add("uid", uid);

            Jayrock.Json.JsonObject keys = new Jayrock.Json.JsonObject();
            keys.Add("read", read_key);
            get_json.Add("keys", keys);

            System.Collections.Generic.Dictionary<string, string> headers = new System.Collections.Generic.Dictionary<string, string>();
            if(!decompress_on_server){
                headers.Add(Libraries.Communication.HEADER_SUPPORTED_COMPRESSION, string.Join(Libraries.Communication.HEADER_SUPPORTED_COMPRESSION_DELIMITER.ToString(), Libraries.Compression.supported_formats));
            }

            System.Net.HttpWebRequest request = MediaStorage.Libraries.Communication.AssembleRequest(this.server + Libraries.Communication.SERVER_GET, get_json, headers:headers);

            System.IO.Stream output;
            if(output_file != null){
                output = output_file;
            }else{
                output = new Libraries.TempFileStream();
            }

            MediaStorage.Libraries.Communication.Response response = MediaStorage.Libraries.Communication.SendRequest(request, output:output, timeout:timeout);

            MediaStorage.Interfaces.Content content = new MediaStorage.Interfaces.Content();
            content.Data = response.Data;
            content.Mime = (string)response.Properties[Libraries.Communication.PROPERTY_CONTENT_TYPE];
            content.Length = (uint)response.Properties[Libraries.Communication.PROPERTY_CONTENT_LENGTH];

            //Evaluate decompression requirements
            object applied_compression = response.Properties[Libraries.Communication.PROPERTY_APPLIED_COMPRESSION];
            if(applied_compression != null){
                System.IO.Stream decompressed_data = Libraries.Compression.GetDecompressor((COMPRESSION)applied_compression).Invoke(content.Data);
                if(output_file != null){ //Write to the given stream, since the caller might expect to use that
                    output_file.Seek(0, System.IO.SeekOrigin.Begin);
                    output_file.SetLength(0); //Truncate the file
                    content.Length = Libraries.Stream.TransferData(decompressed_data, output_file);
                    output_file.Seek(0, System.IO.SeekOrigin.Begin);
                    content.Data = output_file;
                }
            }

            return content;
        }

        /// <summary>
        /// Retrieves the requested record from the server as a dictionary.
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
        /// <exception cref="MediaStorage.HttpError">
        /// A problem occurred related to the transport protocol.
        /// </exception>
        /// <exception cref="MediaStorage.UrlError">
        /// A problem occurred related to the network environment.
        /// </exception>
        public System.Collections.Generic.IDictionary<string, object> Describe(string uid, string read_key, float timeout=2.5f){
            Jayrock.Json.JsonObject describe = new Jayrock.Json.JsonObject();
            describe.Add("uid", uid);

            Jayrock.Json.JsonObject keys = new Jayrock.Json.JsonObject();
            keys.Add("read", read_key);
            describe.Add("keys", keys);

            System.Net.HttpWebRequest request = MediaStorage.Libraries.Communication.AssembleRequest(this.server + Libraries.Communication.SERVER_DESCRIBE, describe);
            return MediaStorage.Libraries.Communication.SendRequest(request, timeout:timeout).ToJson();
        }

        /// <summary>
        /// Unlinks the identified data on the server.
        /// </summary>
        /// <param name='uid'>
        /// The UID of the record to be updated.
        /// </param>
        /// <param name='write_key'>
        /// A token that grants permission to modify the record.
        /// </param>
        /// <param name='timeout'>
        /// The number of seconds to wait for a response; defaults to 2.5.
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
        public void Unlink(string uid, string write_key, float timeout=2.5f){
            Jayrock.Json.JsonObject unlink = new Jayrock.Json.JsonObject();
            unlink.Add("uid", uid);

            Jayrock.Json.JsonObject keys = new Jayrock.Json.JsonObject();
            keys.Add("write", write_key);
            unlink.Add("keys", keys);

            System.Net.HttpWebRequest request = MediaStorage.Libraries.Communication.AssembleRequest(this.server + Libraries.Communication.SERVER_UNLINK, unlink);
            MediaStorage.Libraries.Communication.SendRequest(request, timeout:timeout);
        }

        /// <summary>
        /// Updates attributes of an existing record on a server.
        /// </summary>
        /// <param name='uid'>
        /// The UID of the record to be updated.
        /// </param>
        /// <param name='write_key'>
        /// A token that grants permission to modify the record.
        /// </param>
        /// <param name='new_meta'>
        /// Any newly added metadata; defaults to <c>null</c>.
        /// </param>
        /// <param name='removed_meta'>
        /// A list of all metadata to be removed; defaults to <c>null</c>.
        /// </param>
        /// <param name='deletion_policy'>
        /// May either be <c>null</c>, the default, which means no change (default) or a
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
        /// <param name='timeout'>
        /// The number of seconds to wait for a response; defaults to 2.5.
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
        public void Update(string uid, string write_key,
         System.Collections.Generic.IDictionary<string, object> new_meta=null,
         System.Collections.Generic.IList<string> removed_meta=null,
         System.Collections.Generic.IDictionary<string, ulong> deletion_policy=null,
         System.Collections.Generic.IDictionary<string, ulong> compression_policy=null,
         COMPRESSION compression_policy_format=COMPRESSION.NONE,
         float timeout=2.5f
        ){
            Jayrock.Json.JsonObject update = new Jayrock.Json.JsonObject();
            update.Add("uid", uid);

            Jayrock.Json.JsonObject keys = new Jayrock.Json.JsonObject();
            keys.Add("write", write_key);
            update.Add("keys", keys);

            Jayrock.Json.JsonObject policy = new Jayrock.Json.JsonObject();
            policy.Add("delete", deletion_policy);
            System.Collections.Generic.Dictionary<string, object> comp_policy = (System.Collections.Generic.Dictionary<string, object>)compression_policy;
            if(compression_policy != null){
                comp_policy.Add("comp", compression_policy_format != COMPRESSION.NONE ? compression_policy_format.ToString().ToLower() : null);
            }
            policy.Add("compression", comp_policy);
            update.Add("policy", policy);

            Jayrock.Json.JsonObject meta = new Jayrock.Json.JsonObject();
            meta.Add("new", new_meta != null ? new_meta : new System.Collections.Generic.Dictionary<string, object>());
            meta.Add("removed", removed_meta != null ? removed_meta : new System.Collections.Generic.List<string>());
            update.Add("meta", meta);

            System.Net.HttpWebRequest request = MediaStorage.Libraries.Communication.AssembleRequest(this.server + Libraries.Communication.SERVER_UPDATE, update);
            MediaStorage.Libraries.Communication.SendRequest(request, timeout:timeout);
        }

        /// <summary>
        /// Returns a list of matching records, up to the server's limit.
        /// </summary>
        /// <param name='query'>
        /// The query-structure to evaluate.
        /// </param>
        /// <param name='timeout'>
        /// The number of seconds to wait for a response; defaults to 5.
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
        public System.Collections.Generic.IDictionary<string, object> Query(MediaStorage.Query query, float timeout=5.0f){
            System.Net.HttpWebRequest request = MediaStorage.Libraries.Communication.AssembleRequest(this.server + Libraries.Communication.SERVER_QUERY, query.ToDictionary());
            return (System.Collections.Generic.IDictionary<string, object>)MediaStorage.Libraries.Communication.SendRequest(request, timeout:timeout).ToJson()["records"];
        }
    }
}
