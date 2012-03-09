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
    /// Contains content retrieved from the system.
    /// </summary>
    public struct Content{
        /// <summary>
        /// The MIME-type of the data.
        /// </summary>
        public string Mime;
        /// <summary>
        /// The data, as a stream of bytes.
        /// </summary>
        public System.IO.Stream Data;
        /// <summary>
        /// The length of the data, expressed in bytes.
        /// </summary>
        public long Length;
    }
}

