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

namespace MediaStorage.Libraries{
    /// <summary>
    /// Provides methods for working with data-structures.
    /// </summary>
    /// <remarks>
    /// It's unclear why most other systems provide thorough and transparent type-introspection while the CLR
    /// does not, but whatever.
    /// </remarks>
    internal static class Structures{
        /// <summary>
        /// Converts the given dictionary into something compatible with the JSON everything-is-an-object design.
        /// </summary>
        /// <returns>
        /// A transformed dictionary.
        /// </returns>
        /// <param name='source'>
        /// The dictionary to process.
        /// </param>
        /// <param name='buffer'>
        /// The number of additional slots to add to the dictionary.
        /// </param>
        public static System.Collections.Generic.IDictionary<string, object> ToJsonDictionary(System.Collections.Generic.IDictionary<string, ulong> source, int buffer=0){
            System.Collections.Generic.IDictionary<string, object> destination = new System.Collections.Generic.Dictionary<string, object>(source.Count + buffer);
            foreach(System.Collections.Generic.KeyValuePair<string, ulong> item in source){
                destination.Add(item.Key, item.Value);
            }
            return destination;
        }
    }
}

