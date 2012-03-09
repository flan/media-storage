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
        /// The epoch, needed to compute UNIX timestamps.
        /// </summary>
        private static System.DateTime epoch = (new System.DateTime(1970, 1, 1, 0, 0, 0));

        /// <summary>
        /// Serialises the given CLR timestamp, if any, into a UNIX timestamp.
        /// </summary>
        /// <returns>
        /// A UNIX timestamp or <code>null</code>.
        /// </returns>
        /// <param name='timestamp'>
        /// The CLR timestamp to be converted.
        /// </param>
        internal static double? ToUnixTimestamp(System.DateTime? timestamp){
            if(timestamp == null){
                return null;
            }
            return (timestamp.Value.ToUniversalTime() - Structures.epoch).TotalSeconds;
        }

        /// <summary>
        /// Deserialises the given UNIX timestamp, if any, into a CLR timestamp.
        /// </summary>
        /// <returns>
        /// A CLR timestamp or <code>null</code>.
        /// </returns>
        /// <param name='timestamp'>
        /// The UNIX timestamp to be converted.
        /// </param>
        internal static System.DateTime? ToCLRTimestamp(double? timestamp){
            if(timestamp == null){
                return null;
            }
            return Structures.epoch.AddSeconds(timestamp.Value).ToLocalTime();
        }
    }
}

