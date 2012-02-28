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
    /// <summary>
    /// Provides direct access to a media-storage server; appropriate for most deployments.
    /// </summary>
    public class Client : Interfaces.ControlConstruct{
        private string server;

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
        /// Pings the server.
        /// </summary>
        /// <returns>
        /// <c>true</c> if the server is up and responding normally.
        /// </returns>
        /// <param name='timeout'>
        /// The number of seconds to wait for a response; defaults to 1.
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
        public bool Ping(float timeout=1.0f){
            System.Net.HttpWebRequest request = MediaStorage.Libraries.Communication.AssembleRequest(this.server + Libraries.Communication.SERVER_PING, new System.Collections.Generic.Dictionary<string, object>());
            MediaStorage.Libraries.Communication.SendRequest(request, timeout:timeout).ToJson();
            return true;
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
        /// Retrieves the requested record from the server as a dictionary.
        /// </summary>
        /// <param name='uid'>
        /// The UID of the record to be updated.
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
        /// Rules defining when the record should be deleted; defaults to <c>null</c>, meaning no change.
        /// </param>
        /// <param name='compression_policy'>
        /// Rules describing when the record should be compressed; defaults to <c>null</c>, meaning no change.
        /// </param>
        /// <param name='compression_policy_format'>
        /// The type of compression to apply upon compression; defaults to <c>COMPRESSION.NONE</c>.
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
         System.Collections.Generic.IDictionary<string, long> deletion_policy=null,
         System.Collections.Generic.IDictionary<string, long> compression_policy=null,
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
        public System.Collections.Generic.IDictionary<string, object> Query(MediaStorage.Interfaces.Query query, float timeout=5.0f){
            System.Net.HttpWebRequest request = MediaStorage.Libraries.Communication.AssembleRequest(this.server + Libraries.Communication.SERVER_QUERY, query.ToDictionary());
            return (System.Collections.Generic.IDictionary<string, object>)MediaStorage.Libraries.Communication.SendRequest(request, timeout:timeout).ToJson()["records"];
        }
    }
}
