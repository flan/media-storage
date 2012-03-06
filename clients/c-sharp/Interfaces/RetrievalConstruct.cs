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

namespace MediaStorage.Structs{
    /// <summary>
    /// Contains content retrieved from the system.
    /// </summary>
    public struct Content{
        /// <summary>
        /// The MIME-type of the data.
        /// </summary>
        public string Mime;
        /// <summary>
        /// The data, as a stream of bytes.
        /// </summary>
        public System.IO.Stream Data;
        /// <summary>
        /// The length of the data, expressed in bytes.
        /// </summary>
        public uint Length;
    }
}
namespace MediaStorage.Interfaces{
    /// <summary>
    /// Defines methods that must be implemented to allow data to be retrieved by a client.
    /// </summary>
    public interface RetrievalConstruct : BaseConstruct{
        /// <summary>
        /// Retrieves the requested data from the server.
        /// </summary>
        /// <returns>
        /// Returns the content's MIME and the decompressed data as a stream (optionally that
        /// supplied as <c>output_file</c>), along with the length of the content in bytes.
        /// </returns>
        /// <param name='uid'>
        /// The UID of the record to be retrieved.
        /// </param>
        /// <param name='read_key'>
        /// A token that grants permission to read the record.
        /// </param>
        /// <param name='output_file'>
        /// An optional stream into which retrieved content may be written; if <c>null</c>, an
        /// appropriate backing store will be chosen.
        /// </param>
        /// <param name='decompress_on_server'>
        /// Favours decompression of content on the server; defaults to <c>false</c>.
        /// </param>
        /// <param name='timeout'>
        /// The number of seconds to wait for a response; defaults to 5.
        /// </param>
        Structs.Content Get(string uid, string read_key, System.IO.Stream output_file=null, bool decompress_on_server=false, float timeout=5.0f);

        /// <summary>
        /// Retrieves details about the requested record from the server.
        /// </summary>
        /// <param name='uid'>
        /// The UID of the record to be read.
        /// </param>
        /// <param name='read_key'>
        /// A token that grants permission to read the record.
        /// </param>
        /// <param name='timeout'>
        /// The number of seconds to wait for a response; defaults to 2.5.
        /// </param>
        Structures.Internal.Description Describe(string uid, string read_key, float timeout=2.5f);
    }
}
