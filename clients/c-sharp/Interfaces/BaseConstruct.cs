//  
//  Author:
//       Neil Tallim <flan@uguu.ca>
// 
//  Copyright (c) 2012 Ivrnet, inc.
// 
//  This program is free software: you can redistribute it and/or modify
//  it under the terms of the GNU General Public License as published by
//  the Free Software Foundation, either version 3 of the License, or
//  (at your option) any later version.
// 
//  This program is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details.
// 
//  You should have received a copy of the GNU General Public License
//  along with this program.  If not, see <http://www.gnu.org/licenses/>.
// 

namespace MediaStorage.Interfaces{
    /// <summary>
    /// Defines methods that must be implemented by all clients.
    /// </summary>
    public interface BaseConstruct{
        /// <summary>
        /// Pings the server to indicate whether it is alive or not.
        /// </summary>
        /// <param name='timeout'>
        /// The number of seconds to wait for a response; defaults to 1.
        /// </param>
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
        bool Ping(float timeout=1.0f);
    }
}
