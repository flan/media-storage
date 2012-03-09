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
        /// The smallest creation-time to select; defaults to unlimited.
        /// </summary>
        public System.DateTime? CtimeMin = null;
        /// <summary>
        /// The largest creation-time to select; defaults to unlimited.
        /// </summary>
        public System.DateTime? CtimeMax = null;
        /// <summary>
        /// The smallest last-access-time to select; defaults to unlimited.
        /// </summary>
        public System.DateTime? AtimeMin = null;
        /// <summary>
        /// The largest last-access-time to select; defaults to unlimited.
        /// </summary>
        public System.DateTime? AtimeMax = null;
        /// <summary>
        /// The smallest number of accesses to select; defaults to unlimited.
        /// </summary>
        public ulong? AccessesMin = null;
        /// <summary>
        /// The largest number of accesses to select; defaults to unlimited.
        /// </summary>
        public ulong? AccessesMax = null;

        /// <summary>
        /// The case-sensitive family from which to select data; defaults to the generic family, <c>null</c>.
        /// </summary>
        public string Family = null;
        /// <summary>
        /// The MIME-type of data to match; defaults to matching all; omitting the '/'-specifier selects the super-type.
        /// </summary>
        public string Mime = null;
        /// <summary>
        /// Any metadata that must be matched to select data; types matter, but strings are subject to filtering rules, described at the class-level.
        /// </summary>
        public System.Collections.Generic.IDictionary<string, object> Meta = new Jayrock.Json.JsonObject();

        /// <summary>
        /// Serialises the query object as a media-storage-query-compatible, JSON-friendly data-structure.
        /// </summary>
        /// <returns>
        /// A JSON-friendly dictionary representation of the query object in its current state.
        /// </returns>
        internal System.Collections.Generic.IDictionary<string, object> ToDictionary(){
            Jayrock.Json.JsonObject json_struct = new Jayrock.Json.JsonObject();

            Jayrock.Json.JsonObject ctime = new Jayrock.Json.JsonObject();
            ctime.Add("min", Libraries.Structures.ToUnixTimestamp(this.CtimeMin));
            ctime.Add("max", Libraries.Structures.ToUnixTimestamp(this.CtimeMax));
            json_struct.Add("ctime", ctime);
            
            Jayrock.Json.JsonObject atime = new Jayrock.Json.JsonObject();
            atime.Add("min", Libraries.Structures.ToUnixTimestamp(this.AtimeMin));
            atime.Add("max", Libraries.Structures.ToUnixTimestamp(this.AtimeMax));
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

