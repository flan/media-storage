// 
//  Query.cs
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
    public class Query{
        public System.Collections.Generic.IList<Description> Results;

        internal Query(System.Collections.Generic.IList<object> results){
            this.Results = new System.Collections.Generic.List<MediaStorage.Structures.Internal.Description>();
            foreach(object result in results){
                this.Results.Add(new Description((System.Collections.Generic.IDictionary<string, object>)result));
            }
        }
    }
}

