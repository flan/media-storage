// 
//  Policy.cs
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
    public abstract class Policy{
        public double? Stale;
        private System.DateTime? stale_time;
        public System.DateTime? StaleTime{
            get{
                if(this.stale_time != null){
                    return this.stale_time.Value;
                }
                if(this.Stale != null){
                    return System.DateTime.Now.AddSeconds(this.Stale.Value);
                }
                return null;
            }
        }
        public double? Fixed;
        public System.DateTime? FixedTime{
            get{
                if(this.Fixed != null){
                    return System.DateTime.Now.AddSeconds(this.Fixed.Value);
                }
                return null;
            }
        }

        protected Policy(){
        }
        internal Policy(System.Collections.Generic.IDictionary<string, object> policy){
            if(policy.ContainsKey("stale")){
                this.Stale = ((Jayrock.Json.JsonNumber)policy["stale"]).ToDouble();
            }
            if(policy.ContainsKey("staleTime")){
                this.stale_time = Libraries.Structures.ToCLRTimestamp(((Jayrock.Json.JsonNumber)policy["staleTime"]).ToDouble());
            }
            if(policy.ContainsKey("fixed")){
                this.Fixed = ((Jayrock.Json.JsonNumber)policy["fixed"]).ToDouble();
            }
        }

        internal virtual System.Collections.Generic.IDictionary<string, object> ToDictionary(){
            System.Collections.Generic.IDictionary<string, object> dictionary = new System.Collections.Generic.Dictionary<string, object>();
            if(this.Stale != null){
                dictionary.Add("stale", this.Stale.Value);
            }
            if(this.Fixed != null){
                dictionary.Add("fixed", this.Fixed.Value);
            }
            return dictionary;
        }
    }

    public class CompressionPolicy : Policy{
        public COMPRESSION Format = COMPRESSION.NONE;

        public CompressionPolicy() : base(){}
        internal CompressionPolicy(System.Collections.Generic.IDictionary<string, object> policy) : base(policy){
            this.Format = Libraries.Compression.ResolveCompressionFormat((string)policy["comp"]);
        }

        internal override System.Collections.Generic.IDictionary<string, object> ToDictionary(){
            System.Collections.Generic.IDictionary<string, object> dictionary = base.ToDictionary();
            if(this.Format != COMPRESSION.NONE){
                dictionary.Add("comp", this.Format.ToString().ToLower());
            }
            return dictionary;
        }
    }

    public class DeletionPolicy : Policy{
        public DeletionPolicy() : base(){}
        internal DeletionPolicy(System.Collections.Generic.IDictionary<string, object> policy) : base(policy){}
    }
}

