//  
//  Author:
//       Neil Tallim <flan@uguu.ca>
// 
//  Copyright (c) 2012 Neil Tallim
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

namespace MediaStorage{
    /// <summary>
    /// Specifies the type of compression to apply to the data while it's in storage
    /// </summary>
    public enum COMPRESSION{
        /// <summary>
        /// No compression is applied
        /// </summary>
        NONE,
        /// <summary>
        /// Gzip is fast and does a decent job of compressing content like documents
        /// </summary>
        GZ,
        /// <summary>
        /// BZ2 offers a good mix of speed and compression of all content; it has no client-side CLR handling
        /// </summary>
        BZ2,
        /// <summary>
        /// LZMA is slow, but compresses very aggressively; it has no client-side CLR handling
        /// </summary>
        LZMA,
    }
}

namespace MediaStorage.Libraries{
    internal static class Compression{
        internal static COMPRESSION[] supported_formats = new COMPRESSION[]{COMPRESSION.GZ};

        internal static System.Func<System.IO.Stream, System.IO.Stream> GetCompressor(COMPRESSION compression){
            if(compression == COMPRESSION.NONE){
                return Compression.NullHandler;
            }else if(compression == COMPRESSION.GZ){
                return Compression.CompressGz;
            }
            throw new System.ArgumentException(compression.ToString() + " is unsupported");
        }

        internal static System.Func<System.IO.Stream, System.IO.Stream> GetDecompressor(COMPRESSION compression){
            if(compression == COMPRESSION.NONE){
                return Compression.NullHandler;
            }else if(compression == COMPRESSION.GZ){
                return Compression.DecompressGz;
            }
            throw new System.ArgumentException(compression.ToString() + " is unsupported");
        }

        internal static System.IO.Stream NullHandler(System.IO.Stream data){
            return data;
        }

        internal static System.IO.Stream CompressGz(System.IO.Stream data){
            System.IO.Compression.GZipStream gz = new System.IO.Compression.GZipStream(data, System.IO.Compression.CompressionMode.Compress);
            TempFileStream tfs = new TempFileStream();

            Stream.TransferData(gz, tfs);
            tfs.Seek(0, System.IO.SeekOrigin.Begin);

            return tfs;
        }

        internal static System.IO.Stream DecompressGz(System.IO.Stream data){
            System.IO.Compression.GZipStream gz = new System.IO.Compression.GZipStream(data, System.IO.Compression.CompressionMode.Decompress);
            TempFileStream tfs = new TempFileStream();

            Stream.TransferData(gz, tfs);
            tfs.Seek(0, System.IO.SeekOrigin.Begin);

            return tfs;
        }
    }
}
