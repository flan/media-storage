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
    /// Contains definitions for all methods and structures common to all client-types.
    /// </summary>
    public abstract class AbstractBaseClient : Interfaces.BaseConstruct{
        /// <summary>
        /// The details of the media-storage server.
        /// </summary>
        protected Server server;

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
        /// <exception cref="Exceptions.ProtocolError">
        /// A problem occurred related to the transport protocol.
        ///
        /// This usually means the host is up, but the service is unresponsive.
        /// </exception>
        /// <exception cref="Exceptions.UrlError">
        /// A problem occurred related to the network environment.
        ///
        /// This usually means the host is down or there's a DNS/routing issue.
        /// </exception>
        public bool Ping(float timeout=1.0f){
            System.Net.HttpWebRequest request = Libraries.Communication.AssembleRequest(this.GetServer() + Libraries.Communication.SERVER_PING, new System.Collections.Generic.Dictionary<string, object>());
            Libraries.Communication.SendRequest(request, timeout:timeout).ToDictionary();
            return true;
        }
		
		/// <summary>
		/// Provides the address of the server to access for queries.
		/// </summary>
		internal virtual string GetServer(){
			return this.server.GetHost();
		}
    }
}

