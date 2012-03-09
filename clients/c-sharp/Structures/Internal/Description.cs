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

namespace MediaStorage.Structures.Internal{
    /// <summary>
    /// Describes data stored on the server.
    /// </summary>
    public class Description{
        /// <summary>
        /// The UID of the stored data.
        /// </summary>
        public string Uid;
        /// <summary>
        /// The keys used to access the data; <c>null</c> if the data is being described by an untrusted source.
        /// </summary>
        public Keys Keys = null;
        /// <summary>
        /// Physical attributes of the stored data.
        /// </summary>
        public Internal.DescriptionPhysical Physical;
        /// <summary>
        /// Policies in place over the stored data.
        /// </summary>
        public Internal.DescriptionPolicy Policy;
        /// <summary>
        /// Statistics related to the stored data.
        /// </summary>
        public Internal.DescriptionStats Stats;
        /// <summary>
        /// Any metadata associated with the stored data; must be cast before use in most cases.
        /// </summary>
        public System.Collections.Generic.IDictionary<string, object> Meta;

        /// <summary>
        /// Extracts description information from the server's response.
        /// </summary>
        /// <param name='description'>
        /// The structure to be dissected.
        /// </param>
        internal Description(System.Collections.Generic.IDictionary<string, object> description){
            this.Uid = (string)description["uid"];
            if(description.ContainsKey("keys")){
                this.Keys = new Keys((System.Collections.Generic.IDictionary<string, object>)description["keys"]);
            }
            this.Physical = new Internal.DescriptionPhysical((System.Collections.Generic.IDictionary<string, object>)description["physical"]);
            this.Policy = new Internal.DescriptionPolicy((System.Collections.Generic.IDictionary<string, object>)description["policy"]);
            this.Stats = new Internal.DescriptionStats((System.Collections.Generic.IDictionary<string, object>)description["stats"]);
            this.Meta = (System.Collections.Generic.IDictionary<string, object>)description["meta"];
        }
    }

    /// <summary>
    /// Describes physical properties of data stored on the server.
    /// </summary>
    public class DescriptionPhysical{
        /// <summary>
        /// The time at which the data was last accessed.
        /// </summary>
        public System.DateTime Atime;
        /// <summary>
        /// The time at which the data was created.
        /// </summary>
        public System.DateTime Ctime;
        /// <summary>
        /// The family to which the data belongs; <c>null</c> refers to the generic family.
        /// </summary>
        public string Family;
        /// <summary>
        /// Format details of the stored data.
        /// </summary>
        public DescriptionPhysicalFormat Format;

        /// <summary>
        /// Extracts physical description information from the server's response.
        /// </summary>
        /// <param name='physical'>
        /// The structure to be dissected.
        /// </param>
        internal DescriptionPhysical(System.Collections.Generic.IDictionary<string, object> physical){
            this.Atime = Libraries.Structures.ToCLRTimestamp(((Jayrock.Json.JsonNumber)physical["atime"]).ToDouble()).Value;
            this.Ctime = Libraries.Structures.ToCLRTimestamp(((Jayrock.Json.JsonNumber)physical["ctime"]).ToDouble()).Value;
            this.Family = (string)physical["family"];
            this.Format = new DescriptionPhysicalFormat((System.Collections.Generic.IDictionary<string, object>)physical["format"]);
        }
    }

    /// <summary>
    /// Describes physical format properties of data stored on the server.
    /// </summary>
    public class DescriptionPhysicalFormat{
        /// <summary>
        /// The MIME-type of the stored data.
        /// </summary>
        public string Mime;
        /// <summary>
        /// The compression format currently in use on the data.
        /// </summary>
        public COMPRESSION Compression = COMPRESSION.NONE;

        /// <summary>
        /// Extracts format description information from the server's response.
        /// </summary>
        /// <param name='format'>
        /// The structure to be dissected.
        /// </param>
        internal DescriptionPhysicalFormat(System.Collections.Generic.IDictionary<string, object> format){
            this.Mime = (string)format["mime"];
            if(format.ContainsKey("comp")){
                this.Compression = Libraries.Compression.ResolveCompressionFormat((string)format["comp"]);
            }
        }
    }

    /// <summary>
    /// Describes policies applied to data stored on the server.
    /// </summary>
    public class DescriptionPolicy{
        /// <summary>
        /// The compression policy applied to the data; <c>null</c> if no policy is defined.
        /// </summary>
        public CompressionPolicy Compress = null;
        /// <summary>
        /// The deletion policy applied to the data; <c>null</c> if no policy is defined.
        /// </summary>
        public DeletionPolicy Delete = null;

        /// <summary>
        /// Extracts policy description information from the server's response.
        /// </summary>
        /// <param name='policy'>
        /// The structure to be dissected.
        /// </param>
        internal DescriptionPolicy(System.Collections.Generic.IDictionary<string, object> policy){
            if(policy.ContainsKey("compress")){
                this.Compress = new CompressionPolicy((System.Collections.Generic.IDictionary<string, object>)policy["compress"]);
            }
            if(policy.ContainsKey("delete")){
                this.Delete = new DeletionPolicy((System.Collections.Generic.IDictionary<string, object>)policy["delete"]);
            }
        }
    }

    /// <summary>
    /// Describes statistical properties of data stored on the server.
    /// </summary>
    public class DescriptionStats{
        /// <summary>
        /// The number of times the data has been accessed.
        /// </summary>
        public long Accesses;

        /// <summary>
        /// Extracts stats description information from the server's response.
        /// </summary>
        /// <param name='stats'>
        /// The structure to be dissected.
        /// </param>
        internal DescriptionStats(System.Collections.Generic.IDictionary<string, object> stats){
            this.Accesses = ((Jayrock.Json.JsonNumber)stats["accesses"]).ToInt64();
        }
    }
}
