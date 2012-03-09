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
    /// Defines attributes and methods common to all policy-types.
    /// </summary>
    public abstract class Policy{
        /// <summary>
        /// The number of seconds after last-access at which the data will be considered stale and
        /// eligible for the policy's intent.
        /// </summary>
        public double? Stale;
        /// <summary>
        /// The stale-time returned by the server, in the event that the policy is non-prescriptive.
        /// </summary>
        private System.DateTime? stale_time;
        /// <summary>
        /// Provides a local-time representation of when the data will be considered stale, using the
        /// value from the server if provided or computing one from <see cref="Stale"/>.
        /// </summary>
        /// <value>
        /// <c>null</c> if both the server's stale-time and the local stale-time are undefined.
        /// </value>
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
        /// <summary>
        /// The number of seconds until the data will be processed under the policy's intent.
        /// </summary>
        public double? Fixed;
        /// <summary>
        /// Computes the local-time at which execution of the policy's intent will occur.
        /// </summary>
        /// <value>
        /// <c>null</c> if no fixed time is set.
        /// </value>
        public System.DateTime? FixedTime{
            get{
                if(this.Fixed != null){
                    return System.DateTime.Now.AddSeconds(this.Fixed.Value);
                }
                return null;
            }
        }
     
        /// <summary>
        /// Creates an empty policy, to be filled out by the caller.
        /// </summary>
        protected Policy(){
        }
        /// <summary>
        /// Extracts policy information from the server's response.
        /// </summary>
        /// <param name='policy'>
        /// The structure to be dissected.
        /// </param>
        internal Policy(System.Collections.Generic.IDictionary<string, object> policy){
            if(policy.ContainsKey("stale")){
                this.Stale = ((Jayrock.Json.JsonNumber)policy ["stale"]).ToDouble();
            }
            if(policy.ContainsKey("staleTime")){
                this.stale_time = Libraries.Structures.ToCLRTimestamp(((Jayrock.Json.JsonNumber)policy ["staleTime"]).ToDouble());
            }
            if(policy.ContainsKey("fixed")){
                this.Fixed = ((Jayrock.Json.JsonNumber)policy ["fixed"]).ToDouble();
            }
        }
     
        /// <summary>
        /// Consturcts a dictionary representation of the policy-struct, to be sent to the server.
        /// </summary>
        internal virtual System.Collections.Generic.IDictionary<string, object> ToDictionary(){
            System.Collections.Generic.IDictionary<string, object > dictionary = new System.Collections.Generic.Dictionary<string, object>();
            if(this.Stale != null){
                dictionary.Add("stale", this.Stale.Value);
            }
            if(this.Fixed != null){
                dictionary.Add("fixed", this.Fixed.Value);
            }
            return dictionary;
        }
    }
 
    /// <summary>
    /// Defines a policy instance specific to compression intents.
    /// </summary>
    public class CompressionPolicy : Policy{
        /// <summary>
        /// The type of compression to be applied when the policy executes.
        /// </summary>
        public COMPRESSION Format = COMPRESSION.NONE;
     
        /// <summary>
        /// Initializes an empty compression policy for configuration by the caller.
        /// </summary>
        public CompressionPolicy() : base(){
        }
        /// <summary>
        /// Extracts policy information from the server's response.
        /// </summary>
        /// <param name='policy'>
        /// The structure to be dissected.
        /// </param>
        internal CompressionPolicy(System.Collections.Generic.IDictionary<string, object> policy) : base(policy){
            this.Format = Libraries.Compression.ResolveCompressionFormat((string)policy ["comp"]);
        }
     
        /// <summary>
        /// Consturcts a dictionary representation of the policy-struct, to be sent to the server.
        /// </summary>
        internal override System.Collections.Generic.IDictionary<string, object> ToDictionary(){
            System.Collections.Generic.IDictionary<string, object > dictionary = base.ToDictionary();
            if(this.Format != COMPRESSION.NONE){
                dictionary.Add("comp", this.Format.ToString().ToLower());
            }
            return dictionary;
        }
    }
 
    /// <summary>
    /// Defines a policy instance specific to deletion intents.
    /// </summary>
    public class DeletionPolicy : Policy{
        /// <summary>
        /// Initializes an empty deletion policy for configuration by the caller.
        /// </summary>
        public DeletionPolicy() : base(){
        }
        /// <summary>
        /// Extracts policy information from the server's response.
        /// </summary>
        /// <param name='policy'>
        /// The structure to be dissected.
        /// </param>
        internal DeletionPolicy(System.Collections.Generic.IDictionary<string, object> policy) : base(policy){
        }
    }
}

