// 
//  DescriptionKeys.cs
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
using System;

namespace MediaStorage.Structures{
    public class Keys{
        /// <summary>
        /// The read-key of the stored data.
        /// </summary>
        public string Read;
        /// <summary>
        /// The write-key of the stored data.
        /// </summary>
        public string Write;
		
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

        internal virtual System.Collections.Generic.IDictionary<string, object> ToDictionary(){
            System.Collections.Generic.IDictionary<string, object> dictionary = new System.Collections.Generic.Dictionary<string, object>();
            dictionary.Add("read", this.Read);
            dictionary.Add("write", this.Write);
            return dictionary;
        }
    }
}
