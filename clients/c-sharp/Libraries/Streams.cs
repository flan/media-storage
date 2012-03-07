// 
//  Streams.cs
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
}

