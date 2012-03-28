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

namespace MediaStorage{
	/// <summary>
	/// Describes the server-environment for data-storage.
	/// </summary>
	public class Server{
		private string host = null;
		private ushort port = 0;
		private bool ssl = false;
		private bool srv = false;
		
		/// <summary>
		/// Initializes a new instance of the <see cref="MediaStorage.Server"/> class.
		/// </summary>
		/// <param name='host'>
		/// May be an address or IP.
		/// </param>
		/// <param name='port'>
		/// The port to which connections should be made; ignored if <c>srv</c> is set.
		/// </param>
		/// <param name='ssl'>
		/// Uses HTTPS for communications; must match the server's config. Introduces considerable overhead.
		/// </param>
		/// <param name='srv'>
		/// Uses SRV records to resolve the best server-candidate in the environment; negates <c>port</c>.
		/// </param>
		public Server(string host, ushort port=0, bool ssl=false, bool srv=false){
			if(port == 0 && !srv){
				throw new System.ArgumentException("Port may only be undefined when using SRV records");
			}
			
			this.host = host;
			if(srv){
				this.port = 0;
			}else{
				this.port = port;
			}
			this.ssl = ssl;
			this.srv = srv;
		}
		
		/// <summary>
		/// Provides all meaningful constructor parameters as a dictionary.
		/// </summary>
		internal System.Collections.Generic.IDictionary<string, object> ToDictionary(){
			System.Collections.Generic.IDictionary<string, object> dict = new System.Collections.Generic.Dictionary<string, object>();
			dict.Add("host", this.host);
			dict.Add("port", this.port);
			dict.Add("ssl", this.ssl);
			dict.Add("srv", this.srv);
			return dict;
		}
		
		/// <summary>
		/// Provides a schema-complete address for a host.
		/// </summary>
		private string Assemble(string host, ushort port, bool ssl){
			return "http" + (ssl ? "s" : "") + "://" + host + ':' + port;
		}
		
		/// <summary>
		/// Resolves a schema-complete address for a usable host.
		/// </summary>
		/// <exception cref="URLError">
		/// Thrown if resolution fails.
		/// </exception>
		public string GetHost(){
			if(this.srv){
				System.Collections.Generic.IDictionary<uint, System.Collections.Generic.IList<Heijden.DNS.RecordSRV>> candidates = new System.Collections.Generic.SortedDictionary<uint, System.Collections.Generic.IList<Heijden.DNS.RecordSRV>>();
				try{
					foreach(Heijden.DNS.AnswerRR response in new Heijden.DNS.Resolver().Query(this.host, Heijden.DNS.QType.SRV).Answers){
						Heijden.DNS.RecordSRV record = (Heijden.DNS.RecordSRV)response.RECORD;
						System.Collections.Generic.IList<Heijden.DNS.RecordSRV> container;
						if(candidates.ContainsKey(record.PRIORITY)){
						 	container = candidates[record.PRIORITY];
						}else{
							container = new System.Collections.Generic.List<Heijden.DNS.RecordSRV>();
							candidates.Add(record.PRIORITY, container);
						}
						container.Add(record);
					}
				}catch(System.Exception e){
					throw new MediaStorage.Exceptions.URLError("Unable to resolve SRV record: " + e.Message);
				}
				
				foreach(System.Collections.Generic.KeyValuePair<uint, System.Collections.Generic.IList<Heijden.DNS.RecordSRV>> c in candidates){
					while(c.Value.Count > 0){
						uint weight_total = 0;
						foreach(Heijden.DNS.RecordSRV option in c.Value){
							weight_total += option.WEIGHT;
						}
						uint selection = (uint)((new System.Random()).NextDouble() * weight_total);
						Heijden.DNS.RecordSRV choice = null;
						foreach(Heijden.DNS.RecordSRV option in c.Value){
							selection -= option.WEIGHT;
							if(selection <= 0){
								choice = option;
								break;
							}
						}
						
						if(choice == null){ //Should never happen, but C# is a mystery I don't care to understand.
							break;
						}
						
						string address = this.Assemble(choice.TARGET, choice.PORT, this.ssl);
						try{
							System.Net.HttpWebRequest request = Libraries.Communication.AssembleRequest(address + Libraries.Communication.SERVER_PING, new System.Collections.Generic.Dictionary<string, object>());
            				Libraries.Communication.SendRequest(request, timeout:1).ToDictionary();
							return address;
						}catch(System.Exception){
							c.Value.Remove(choice);
						}
					}
				}
				throw new MediaStorage.Exceptions.URLError("Unable to resolve a viable server via SRV lookup");
			}else{
				return this.Assemble(this.host, this.port, this.ssl);
			}
		}
	}
}
