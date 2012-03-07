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
    /// Defines methods that must be implemented to allow data to be manipulated by a client.
    ///
    /// In its current form, also inherits storage and retreival methods, since there's no obvious
    /// case for allowing independent manuipulation.
    /// </summary>
    public interface ControlConstruct : StorageConstruct, RetrievalConstruct{
        /// <summary>
        /// Enumerates all families currently defined on the server.
        /// </summary>
        /// <returns>
        /// A sorted list of strings representing family names.
        /// </returns>
        /// <param name='timeout'>
        /// The number of seconds to wait for a response; defaults to 2.5.
        /// </param>
        System.Collections.Generic.IList<string> ListFamilies(float timeout=2.5f);

        /// <summary>
        /// Unlinks the identified data from the environment.
        /// </summary>
        /// <param name='uid'>
        /// The identifier of the data to be unlinked.
        /// </param>
        /// <param name='write_key'>
        /// A key, possibly <c>null</c>, used to establish permission to unlink the data.
        /// </param>
        /// <param name='timeout'>
        /// The number of seconds to wait for a response from the server; defaults to 2.5.
        /// </param>
        void Unlink(string uid, string write_key, float timeout=2.5f);

        /// <summary>
        /// Updates attributes of an existing record in the environment.
        /// </summary>
        /// <param name='uid'>
        /// The UID of the record to be updated.
        /// </param>
        /// <param name='write_key'>
        /// A token that grants permission to modify the record.
        /// </param>
        /// <param name='new_meta'>
        /// Any newly added metadata; defaults to <c>null</c>.
        /// </param>
        /// <param name='removed_meta'>
        /// A list of all metadata to be removed; defaults to <c>null</c>.
        /// </param>
        /// <param name='deletion_policy'>
        /// May either be <c>null</c>, the default, which means no change or a <see cref="Structures.DeletionPolicy"/>
        /// instance.
        /// </param>
        /// <param name='compression_policy'>
        /// May either be <c>null</c>, the default, which means no change or a <see cref="Structures.CompressionPolicy"/>
        /// instance.
        /// </param>
        /// <param name='compression_policy_format'>
        /// The format into which the file will be compressed once the compression policy activates; defaults to <c>COMPRESSION.NONE</c>.
        /// </param>
        /// <param name='timeout'>
        /// The number of seconds to wait for a response; defaults to 2.5.
        /// </param>
        void Update(string uid, string write_key,
         System.Collections.Generic.IDictionary<string, object> new_meta=null,
         System.Collections.Generic.IList<string> removed_meta=null,
         Structures.DeletionPolicy deletion_policy=null,
         Structures.CompressionPolicy compression_policy=null,
         float timeout=2.5f
        );

        /// <summary>
        /// Returns a list of matching records, up to the server's limit.
        /// </summary>
        /// <param name='query'>
        /// The query-structure to evaluate.
        /// </param>
        /// <param name='timeout'>
        /// The number of seconds to wait for a response; defaults to 5.
        /// </param>
        Structures.Internal.Query Query(Structures.Query query, float timeout=5.0f);
    }
}
