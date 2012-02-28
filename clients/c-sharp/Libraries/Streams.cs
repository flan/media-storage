// 
//  Streams.cs
//  
//  Author:
//       Neil Tallim <flan@uguu.ca>
// 
//  Copyright (c) 2012 Neil Tallim
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
    internal class TempFileStream : System.IO.FileStream, System.IDisposable{
        private bool disposed = false;

        public TempFileStream() : base(
         System.IO.Path.Combine(System.IO.Path.GetTempPath(), System.Guid.NewGuid().ToString()),
         System.IO.FileMode.CreateNew,
         System.IO.FileAccess.ReadWrite
        ){}

        ~TempFileStream(){
            try{
                base.Dispose(true);
            }catch{
                //Nothing can be done
            }
            this.Unlink();
        }

        protected override void Dispose(bool disposing){
            base.Dispose(disposing);
            if(!this.disposed){
                if(disposing){
                    this.Unlink();
                    this.disposed = true;
                }
            }
        }

        private void Unlink(){
            try{
                System.IO.File.Delete(this.Name);
            }catch{
                //Can't do anything, except maybe log a warning
            }
        }
    }

    internal static class Streams{
        //Transfer data in 32k chunks
        private const uint CHUNK_SIZE = 32 * 1024;

        /// <summary>
        /// Reads every byte, in reasonable-sized chunks, from <c>source</c> into
        /// <c>destination</c>. No seeking occurs after the transfer is complete.
        /// </summary>
        /// <returns>
        /// The number of bytes transferred.
        /// </returns>
        /// <param name='source'>
        /// The source from which data is read.
        /// </param>
        /// <param name='destination'>
        /// The destination to which data is written.
        /// </param>
        internal static uint TransferData(System.IO.Stream source, System.IO.Stream destination){
            uint size = 0;
            while(true){
                byte[] chunk = new byte[Streams.CHUNK_SIZE];
                int bytes_read = source.Read(chunk, 0, chunk.Length);
                if(bytes_read == 0){
                    break;
                }
                destination.Write(chunk, 0, bytes_read);
                destination.Flush();
                size += (uint)bytes_read;
            }
            return size;
        }
    }
}

