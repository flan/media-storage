// 
//  DescriptionPhysical.cs
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

namespace MediaStorage.Structures.Internal{
    public class Description{
        public string Uid;
        public Keys Keys = null;
        public Internal.DescriptionPhysical Physical;
        public Internal.DescriptionPolicy Policy;
        public Internal.DescriptionStats Stats;
        public System.Collections.Generic.IDictionary<string, object> Meta;

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

    public class DescriptionPhysical{
        public double Atime;
        public double Ctime;
        public string Family;
        public DescriptionPhysicalFormat Format;

        public DescriptionPhysical(System.Collections.Generic.IDictionary<string, object> physical){
            this.Atime = ((Jayrock.Json.JsonNumber)physical["atime"]).ToDouble();
            this.Ctime = ((Jayrock.Json.JsonNumber)physical["ctime"]).ToDouble();
            this.Family = (string)physical["family"];
            this.Format = new DescriptionPhysicalFormat((System.Collections.Generic.IDictionary<string, object>)physical["format"]);
        }
    }

    public class DescriptionPhysicalFormat{
        public string Mime;
        public COMPRESSION Compression = COMPRESSION.NONE;

        public DescriptionPhysicalFormat(System.Collections.Generic.IDictionary<string, object> format){
            this.Mime = (string)format["mime"];
            if(format.ContainsKey("comp")){
                this.Compression = Libraries.Compression.ResolveCompressionFormat((string)format["comp"]);
            }
        }
    }

    public class DescriptionPolicy{
        public CompressionPolicy Compress;
        public DeletionPolicy Delete;

        public DescriptionPolicy(System.Collections.Generic.IDictionary<string, object> policy){
            if(policy.ContainsKey("compress")){
                this.Compress = new CompressionPolicy((System.Collections.Generic.IDictionary<string, object>)policy["compress"]);
            }
            if(policy.ContainsKey("delete")){
                this.Delete = new DeletionPolicy((System.Collections.Generic.IDictionary<string, object>)policy["delete"]);
            }
        }
    }

    public class DescriptionStats{
        public long Accesses;

        public DescriptionStats(System.Collections.Generic.IDictionary<string, object> stats){
            this.Accesses = ((Jayrock.Json.JsonNumber)stats["accesses"]).ToInt64();
        }
    }
}
