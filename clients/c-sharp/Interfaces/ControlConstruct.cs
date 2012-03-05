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

namespace MediaStorage{
    /// <summary>
    /// Exposes all facets needed to enumerate matching data in the system.
    ///
    /// All fields are meant to be accessed as public struct-members:
    /// <list>
    ///     <item><see cref="ctime_min"/>/<see cref="ctime_max"/> : if either is set, it serves as an <=/>= check against ctime</item>
    ///     <item><see cref="atime_min"/>/<see cref="atime_max"/> : if either is set, it serves as an <=/>= check against atime</item>
    ///     <item><see cref="accesses_min"/>/<see cref="accesses_max"/> : if either is set, it serves as an <=/>= check against accesses</item>
    ///     <item><see cref="family"/> : if set, performs an explicit match against family</item>
    ///     <item><see cref="mime"/> : if set, if a '/' is present, performs an explicit match against MIME; otherwise, performs a match against the super-type of MIME</item>
    /// </list>
    ///
    /// To perform non-matching queries on metadata, the following filters may be used:
    /// <list>
    ///     <item>':range:<min>:<max>' : range queries over numeric types, inclusive on both ends</item>
    ///     <item>':lte:<number>'/':gte:<number>' : relative queries over numeric types</item>
    ///     <item>':re:<pcre>'/':re.i:<pcre>' : PCRE regular expression, with the second form being case-insensitive</item>
    ///     <item>':like:<pattern>' : behaves like SQL 'LIKE', with '%' as wildcards</item>
    ///     <item>':ilike:<pattern>' : behaves like SQL 'ILIKE', with '%' as wildcards</item>
    ///     <item>'::<whatever>' : Ignores the first colon and avoids parsing, in case a value actually starts with a ':<filter>:' structure</item>
    /// </list>
    /// </summary>
    public class Query{
        /// <summary>
        /// The epoch, needed to compute UNIX timestamps.
        /// </summary>
        private static System.DateTime epoch = (new System.DateTime(1970, 1, 1, 0, 0, 0));

        /// <summary>
        /// The smallest creation-time to select; defaults to unlimited.
        /// </summary>
        System.DateTime? CtimeMin = null;
        /// <summary>
        /// The largest creation-time to select; defaults to unlimited.
        /// </summary>
        System.DateTime? CtimeMax = null;
        /// <summary>
        /// The smallest last-access-time to select; defaults to unlimited.
        /// </summary>
        System.DateTime? AtimeMin = null;
        /// <summary>
        /// The largest last-access-time to select; defaults to unlimited.
        /// </summary>
        System.DateTime? AtimeMax = null;
        /// <summary>
        /// The smallest number of accesses to select; defaults to unlimited.
        /// </summary>
        ulong? AccessesMin = null;
        /// <summary>
        /// The largest number of accesses to select; defaults to unlimited.
        /// </summary>
        ulong? AccessesMax = null;

        /// <summary>
        /// The case-sensitive family from which to select data; defaults to the generic family, <c>null</c>.
        /// </summary>
        string Family = null;
        /// <summary>
        /// The MIME-type of data to match; defaults to matching all; omitting the '/'-specifier selects the super-type.
        /// </summary>
        string Mime = null;
        /// <summary>
        /// Any metadata that must be matched to select data; types matter, but strings are subject to filtering rules, described at the class-level.
        /// </summary>
        System.Collections.Generic.IDictionary<string, object> Meta = new Jayrock.Json.JsonObject();

        /// <summary>
        /// Serialises the given timestamp, if any, into a UNIX timestamp.
        /// </summary>
        /// <returns>
        /// A UNIX timestamp or <code>null</code>.
        /// </returns>
        /// <param name='timestamp'>
        /// The timestamp to be converted.
        /// </param>
        private static double? ToUnixTimestamp(System.DateTime? timestamp){
            if(timestamp == null){
                return null;
            }
            return (timestamp.Value.ToUniversalTime() - Query.epoch).TotalSeconds;
        }

        /// <summary>
        /// Serialises the query object as a media-storage-query-compatible, JSON-friendly data-structure.
        /// </summary>
        /// <returns>
        /// A JSON-friendly dictionary representation of the query object in its current state.
        /// </returns>
        internal System.Collections.Generic.IDictionary<string, object> ToDictionary(){
            Jayrock.Json.JsonObject json_struct = new Jayrock.Json.JsonObject();

            Jayrock.Json.JsonObject ctime = new Jayrock.Json.JsonObject();
            ctime.Add("min", Query.ToUnixTimestamp(this.CtimeMin));
            ctime.Add("max", Query.ToUnixTimestamp(this.CtimeMax));
            json_struct.Add("ctime", ctime);
            
            Jayrock.Json.JsonObject atime = new Jayrock.Json.JsonObject();
            atime.Add("min", Query.ToUnixTimestamp(this.AtimeMin));
            atime.Add("max", Query.ToUnixTimestamp(this.AtimeMax));
            json_struct.Add("atime", atime);

            Jayrock.Json.JsonObject accesses = new Jayrock.Json.JsonObject();
            accesses.Add("min", this.AccessesMin);
            accesses.Add("max", this.AccessesMax);
            json_struct.Add("accesses", accesses);

            json_struct.Add("family", this.Family);
            json_struct.Add("mime", this.Mime);
            json_struct.Add("meta", this.Meta);
            
            return json_struct;
        }
    }
}

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
        /// May either be <c>null</c>, the default, which means no change (default) or a
        /// dictionary containing one or both of the following:
        /// <list>
        ///     <item>'fixed': The number of seconds to retain the file from the time it was uploaded</item>
        ///     <item>'stale': The number of seconds that must elapse after the file was last downloaded to qualify it for deletion</item>
        /// </list>
        /// </param>
        /// <param name='compression_policy'>
        /// May either be <c>null</c>, the default, which means the file is never compressed (default) or a
        /// dictionary containing one or both of the following:
        /// <list>
        ///     <item>'fixed': The number of seconds to leave the file alone from the time it was uploaded</item>
        ///     <item>'stale': The number of seconds that must elapse after the file was last downloaded to qualify it for compression</item>
        /// </list>
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
         System.Collections.Generic.IDictionary<string, ulong> deletion_policy=null,
         System.Collections.Generic.IDictionary<string, ulong> compression_policy=null,
         COMPRESSION compression_policy_format=COMPRESSION.NONE,
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
        System.Collections.Generic.IDictionary<string, object> Query(MediaStorage.Query query, float timeout=5.0f);
    }
}
