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
    /// Holds keys used to access stored data.
    /// </summary>
    public class Keys{
        /// <summary>
        /// The read-key of the stored data.
        /// </summary>
        public string Read = null;
        /// <summary>
        /// The write-key of the stored data.
        /// </summary>
        public string Write = null;

        /// <summary>
        /// Creates an empty keys-structure to be filled by the caller.
        /// </summary>
        public Keys(){
        }
        /// <summary>
        /// Creates a keys-structure using data from a server.
        /// </summary>
        /// <param name='keys'>
        /// The data from the server.
        /// </param>
        public Keys(System.Collections.Generic.IDictionary<string, object> keys){
            if(keys.ContainsKey("read")){
                this.Read = (string)keys["read"];
            }
            if(keys.ContainsKey("write")){
                this.Write = (string)keys["write"];
            }
        }

        /// <summary>
        /// Serialises the keys object as a media-storage-query-compatible, JSON-friendly data-structure.
        /// </summary>
        /// <returns>
        /// A JSON-friendly dictionary representation of the keys object in its current state.
        /// </returns>
        internal virtual System.Collections.Generic.IDictionary<string, object> ToDictionary(){
            System.Collections.Generic.IDictionary<string, object> dictionary = new System.Collections.Generic.Dictionary<string, object>();
            dictionary.Add("read", this.Read);
            dictionary.Add("write", this.Write);
            return dictionary;
        }
    }
}

