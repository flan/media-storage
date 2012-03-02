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
    public interface StorageConstruct : BaseConstruct{
        /// <summary>
        /// 
        /// </summary>
        /// <param name="data">
        /// A <see cref="System.IO.Stream"/>
        /// </param>
        /// <param name="mime">
        /// A <see cref="System.String"/>
        /// </param>
        /// <param name="family">
        /// A <see cref="System.String"/>
        /// </param>
        /// <param name="compression">
        /// A <see cref="COMPRESSION"/>
        /// </param>
        /// <param name="compress_on_server">
        /// A <see cref="System.Boolean"/>
        /// </param>
        /// <param name="deletion_policy">
        /// A <see cref="System.Collections.Generic.IDictionary"/>
        /// </param>
        /// <param name="compression_policy">
        /// A <see cref="System.Collections.Generic.IDictionary"/>
        /// </param>
        /// <param name="compression_policy_format">
        /// A <see cref="COMPRESSION"/> value indicating the type of compression to apply when the compression policy
        /// activates.
        /// </param>
        /// <param name="meta">
        /// A <see cref="System.Collections.Generic.IDictionary"/>
        /// </param>
        /// <param name="uid">
        /// A <see cref="System.String"/>
        /// </param>
        /// <param name="keys">
        /// A <see cref="System.Collections.Generic.IDictionary"/>
        /// </param>
        /// <param name="timeout">
        /// A <see cref="System.Single"/>
        /// </param>
        /// <returns>
        /// A <see cref="System.Collections.Generic.IDictionary"/>
        /// </returns>
        System.Collections.Generic.IDictionary<string, object> Put(
         System.IO.Stream data, string mime, string family=null,
         COMPRESSION compression=COMPRESSION.NONE, bool compress_on_server=false,
         System.Collections.Generic.IDictionary<string, long> deletion_policy=null,
         System.Collections.Generic.IDictionary<string, long> compression_policy=null,
         COMPRESSION compression_policy_format=COMPRESSION.NONE,
         System.Collections.Generic.IDictionary<string, object> meta=null,
         string uid=null, System.Collections.Generic.IDictionary<string, string> keys=null,
         float timeout=10.0f
        );
    }
}
