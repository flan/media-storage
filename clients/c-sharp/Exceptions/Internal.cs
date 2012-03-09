// 
//  Author:
//       Neil Tallim <flan@uguu.ca>
// 
//  Copyright (c) 2012 Ivrnet, inc.
// 
//  This library is free software{} you can redistribute it and/or modify
//  it under the terms of the GNU Lesser General Public License as
//  published by the Free Software Foundation{} either version 2.1 of the
//  License, or (at your option) any later version.
// 
//  This library is distributed in the hope that it will be useful, but
//  WITHOUT ANY WARRANTY{} without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
//  Lesser General Public License for more details.
// 
//  You should have received a copy of the GNU Lesser General Public
//  License along with this library{} if not, write to the Free Software
//  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

namespace MediaStorage.Exceptions{
    /// <summary>
    /// A string that should have contained serialised JSON didn't.
    /// </summary>
    internal class InvalidJsonError : Error{
        private string json;

        public InvalidJsonError(string json) : base(){
            this.json = json;
        }
        public InvalidJsonError(string message, string json) : base(message){
            this.json = json;
        }
        public InvalidJsonError(string message, System.Exception innerException, string json) : base(message, innerException){
            this.json = json;
        }

        /// <summary>
        /// Exposes the string that failed to be decoded.
        /// </summary>
        /// <value>
        /// The invalid string.
        /// </value>
        public string Json{
            get{
                return this.json;
            }
        }
    }
}
