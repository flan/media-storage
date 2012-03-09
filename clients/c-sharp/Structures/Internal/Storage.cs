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

namespace MediaStorage.Structures{
    /// <summary>
    /// Provides retrieval information for stored data.
    /// </summary>
    public class Storage{
        /// <summary>
        /// The UID of the stored data.
        /// </summary>
        public string Uid;
        /// <summary>
        /// The keys used to access the stored data.
        /// </summary>
        public Keys Keys;

        /// <summary>
        /// Extracts storage information from the server's response.
        /// </summary>
        /// <param name='storage'>
        /// The structure to be dissected.
        /// </param>
        internal Storage(System.Collections.Generic.IDictionary<string, object> storage){
            this.Uid = (string)storage["uid"];
            this.Keys = new Keys((System.Collections.Generic.IDictionary<string, object>)storage["keys"]);
        }
    }
}

