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
    public class Query{
        private static System.DateTime epoch = (new System.DateTime(1970, 1, 1, 0, 0, 0));
        
        System.DateTime? CtimeMin = null;
        System.DateTime? CtimeMax = null;
        System.DateTime? AtimeMin = null;
        System.DateTime? AtimeMax = null;
        ulong? AccessesMin = null;
        ulong? AccessesMax = null;
        
        string Family = null;
        string Mime = null;
        System.Collections.Generic.IDictionary<string, object> Meta = new Jayrock.Json.JsonObject();

        private static double? ToUnixTimestamp(System.DateTime? timestamp){
            if(timestamp == null){
                return null;
            }
            return (timestamp.Value.ToUniversalTime() - Query.epoch).TotalSeconds;
        }
        
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
    
    public interface ControlConstruct : StorageConstruct, RetrievalConstruct{
        System.Collections.Generic.IList<string> ListFamilies(float timeout=2.5f);

        void Unlink(string uid, string write_key, float timeout=2.5f);

        void Update(string uid, string write_key,
         System.Collections.Generic.IDictionary<string, object> new_meta=null,
         System.Collections.Generic.IList<string> removed_meta=null,
         System.Collections.Generic.IDictionary<string, long> deletion_policy=null,
         System.Collections.Generic.IDictionary<string, long> compression_policy=null,
         COMPRESSION compression_policy_format=COMPRESSION.NONE,
         float timeout=2.5f
        );

        System.Collections.Generic.IDictionary<string, object> Query(Query query, float timeout=5.0f);
    }
}
