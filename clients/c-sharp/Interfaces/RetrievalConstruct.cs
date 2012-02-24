//  
//  Author:
//       Neil Tallim <flan@uguu.ca>
// 
//  Copyright (c) 2012 Neil Tallim
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

using System;

namespace MediaStorage.Interfaces{
    public struct Content{
        string Mime;
        System.IO.Stream Data;
    }
    
    public interface RetrievalConstruct : BaseConstruct{
        /// <summary>
        /// 
        /// </summary>
        /// <param name="uid">
        /// A <see cref="System.String"/>
        /// </param>
        /// <param name="read_key">
        /// A <see cref="System.String"/>
        /// </param>
        /// <param name="output_file">
        /// A <see cref="System.IO.Stream"/>, which is where retrieved content will be written; if <c>null</c>, an
        /// in-memory buffer is used. The buffer is always seeked back to start after writing, but untouched before.
        /// </param>
        /// <param name="decompress_on_server">
        /// A <see cref="System.Boolean"/>
        /// </param>
        /// <param name="timeout">
        /// A <see cref="System.Single"/>
        /// </param>
        /// <returns>
        /// A <see cref="Content"/>
        /// </returns>
        Content Get(string uid, string read_key, System.IO.Stream output_file=null, bool decompress_on_server=false, float timeout=5.0f);

        System.Collections.Generic.IDictionary<string, object> Describe(string uid, string read_key, float timeout=2.5f);
    }
}
