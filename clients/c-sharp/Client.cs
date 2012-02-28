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
    public class Client : Interfaces.ControlConstruct{
        private string server;

        public Client(string server_host, ushort server_port){
            this.server = string.Format("http://{0}:{1}/", server_host, server_port);
        }

        /// <summary>
        /// Pings the server, returning <c>true</c> if the server is up and responding normally or raising an exception otherwise.
        /// </summary>
        /// <param name='timeout'>
        /// The number of seconds to wait for a response; defaults to 1.
        /// </param>
        public bool Ping(float timeout=1.0f){
            System.Net.HttpWebRequest request = MediaStorage.Libraries.Communication.AssembleRequest(this.server, new Jayrock.Json.JsonObject());
            MediaStorage.Libraries.Communication.SendRequest(request, timeout:timeout).ToJson();
            return true;
        }
    }
}
