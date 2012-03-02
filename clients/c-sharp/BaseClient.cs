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
    public abstract class BaseClient : Interfaces.BaseConstruct{
        protected string server;

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
    }
}

