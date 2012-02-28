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
        /// <exception cref="System.Exception">
        /// Some unknown problem occurred.
        /// </exception>
        /// <exception cref="MediaStorage.HttpError">
        /// A problem occurred related to the transport protocol.
        /// </exception>
        /// <exception cref="MediaStorage.UrlError">
        /// A problem occurred related to the network environment.
        /// </exception>
        /// <param name='timeout'>
        /// The number of seconds to wait for a response; defaults to 2.5.
        /// </param>
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
        /// <exception cref="System.Exception">
        /// Some unknown problem occurred.
        /// </exception>
        /// <exception cref="MediaStorage.HttpError">
        /// A problem occurred related to the transport protocol.
        /// </exception>
        /// <exception cref="MediaStorage.UrlError">
        /// A problem occurred related to the network environment.
        /// </exception>
        /// <param name='timeout'>
        /// The number of seconds to wait for a response; defaults to 1.
        /// </param>
        public bool Ping(float timeout=1.0f){
            System.Net.HttpWebRequest request = MediaStorage.Libraries.Communication.AssembleRequest(this.server + Libraries.Communication.SERVER_PING, new System.Collections.Generic.Dictionary<string, object>());
            MediaStorage.Libraries.Communication.SendRequest(request, timeout:timeout).ToJson();
            return true;
        }
    }
}
