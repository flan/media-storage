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
    /// The base class from which all errors native to this assembly inherit.
    /// </summary>
    public class Error : System.Exception{
        public Error() : base(){}
        public Error(string message) : base(message){}
        public Error(string message, System.Exception innerException) : base(message, innerException){}
    }

    /// <summary>
    /// Indicates a problem with the transport protocol, which is, at this point, only HTTP.
    /// </summary>
    public class ProtocolError : Error{
        public ProtocolError() : base(){}
        public ProtocolError(string message) : base(message){}
        public ProtocolError(string message, System.Exception innerException) : base(message, innerException){}
    }

    /// <summary>
    /// The server returned a 403.
    /// </summary>
    public class NotAuthorisedError : ProtocolError{
        public NotAuthorisedError() : base(){}
        public NotAuthorisedError(string message) : base(message){}
        public NotAuthorisedError(string message, System.Exception innerException) : base(message, innerException){}
    }

    /// <summary>
    /// The server returned a 404.
    /// </summary>
    public class NotFoundError : ProtocolError{
        public NotFoundError() : base(){}
        public NotFoundError(string message) : base(message){}
        public NotFoundError(string message, System.Exception innerException) : base(message, innerException){}
    }

    /// <summary>
    /// The server returned a 409.
    /// </summary>
    public class InvalidRecordError : ProtocolError{
        public InvalidRecordError() : base(){}
        public InvalidRecordError(string message) : base(message){}
        public InvalidRecordError(string message, System.Exception innerException) : base(message, innerException){}
    }

    /// <summary>
    /// The server returned a 412.
    /// </summary>
    public class InvalidHeadersError : ProtocolError{
        public InvalidHeadersError() : base(){}
        public InvalidHeadersError(string message) : base(message){}
        public InvalidHeadersError(string message, System.Exception innerException) : base(message, innerException){}
    }

    /// <summary>
    /// The server returned a 503.
    /// </summary>
    public class TemporaryFailureError : ProtocolError{
        public TemporaryFailureError() : base(){}
        public TemporaryFailureError(string message) : base(message){}
        public TemporaryFailureError(string message, System.Exception innerException) : base(message, innerException){}
    }

    /// <summary>
    /// Indicates an error with URL resolution.
    /// </summary>
    public class URLError : Error{
        public URLError() : base(){}
        public URLError(string message) : base(message){}
        public URLError(string message, System.Exception innerException) : base(message, innerException){}
    }
}
