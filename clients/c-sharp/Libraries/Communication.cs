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
    internal static class Communication{
        //Server path constants
        internal const string SERVER_PING = "ping";
        internal const string SERVER_LIST_FAMILIES = "list/families";
        internal const string SERVER_STATUS = "status";
        internal const string SERVER_PUT = "put";
        internal const string SERVER_GET = "get";
        internal const string SERVER_DESCRIBE = "describe";
        internal const string SERVER_UNLINK = "unlink";
        internal const string SERVER_UPDATE = "update";
        internal const string SERVER_QUERY = "query";

        //Constants to expedite construction of multipart/formdata packets
        private const string FORM_SEP = "--";
        private const string FORM_BOUNDARY = "---...???,,,$$$RFC-1867-kOmPl1aNt-bOuNdArY$$$,,,???...---";
        private const string FORM_CRLF = "\r\n";
        private const string FORM_CONTENT_TYPE = "multipart/form-data; boundary=" + FORM_BOUNDARY;
        private static byte[] FORM_HEADER = (new System.Text.ASCIIEncoding()).GetBytes(FORM_SEP + FORM_BOUNDARY + FORM_CRLF +
            "Content-Disposition: form-data; name=\"header\"" + FORM_CRLF + FORM_CRLF);
        private static byte[] FORM_PRE_CONTENT = (new System.Text.ASCIIEncoding()).GetBytes(FORM_CRLF + FORM_SEP + FORM_BOUNDARY + FORM_CRLF +
            "Content-Disposition: form-data; name=\"content\"; filename=\"payload\"" + FORM_CRLF +
            "Content-Type: application/octet-stream" + FORM_CRLF +
            "Content-Transfer-Encoding: binary" + FORM_CRLF + FORM_CRLF);
        private static byte[] FORM_FOOTER = (new System.Text.ASCIIEncoding()).GetBytes(FORM_CRLF + FORM_SEP + FORM_BOUNDARY + FORM_SEP + FORM_CRLF);

        //Request headers
        internal const string HEADER_COMPRESS_ON_SERVER = "Media-Storage-Compress-On-Server";
        internal const string HEADER_COMPRESS_ON_SERVER_TRUE = "yes";
        internal const string HEADER_COMPRESS_ON_SERVER_FALSE = "no"; //Implied by omission
        internal const string HEADER_SUPPORTED_COMPRESSION = "Media-Storage-Supported-Compression";
        internal const char HEADER_SUPPORTED_COMPRESSION_DELIMITER = ';';

        //Response headers
        internal const string HEADER_APPLIED_COMPRESSION = "Media-Storage-Applied-Compression";

        //Response properties
        internal const string PROPERTY_CONTENT_LENGTH = "content-length";
        internal const string PROPERTY_CONTENT_TYPE = "content-type";
        internal const string PROPERTY_APPLIED_COMPRESSION = "applied-compression";
        internal const string PROPERTY_FILE_ATTRIBUTES = "file-attributes";

        internal struct Response{
            public System.Collections.Generic.IDictionary<string, object> Properties;
            public System.IO.Stream Data;

            /// <summary>
            /// Evaluates the response's body as JSON.
            /// </summary>
            /// <returns>
            /// The response's body as a JSON-friendly dictionary.
            /// </returns>
            public System.Collections.Generic.IDictionary<string, object> ToDictionary(){
                string data = new System.IO.StreamReader(this.Data, System.Text.Encoding.UTF8).ReadToEnd();
                try{
                    Jayrock.Json.JsonObject json = Jayrock.Json.Conversion.JsonConvert.Import<Jayrock.Json.JsonObject>(data);
                    return json;
                }catch(System.Exception e){
                    throw new Exceptions.InvalidJsonError("Unable to decode JSON content received from server", e, data);
                }
            }
        }

        private static void EncodeMultipartFormdata(byte[] header, System.IO.Stream content, System.IO.Stream output){
            output.Write(Communication.FORM_HEADER, 0, Communication.FORM_HEADER.Length);
            output.Write(header, 0, header.Length);
            output.Write(Communication.FORM_PRE_CONTENT, 0, Communication.FORM_PRE_CONTENT.Length);
            content.CopyTo(output);
            output.Write(Communication.FORM_FOOTER, 0, Communication.FORM_FOOTER.Length);
        }

        /// <summary>
        /// Compiles and returns a media-storage-spec-compliant HTTP request.
        /// </summary>
        /// <returns>
        /// A request, ready to be executed.
        /// </returns>
        /// <param name='destination'>
        /// The URI to which the request will be sent.
        /// </param>
        /// <param name='header'>
        /// The JSON structure that contains the semantics of the request.
        /// </param>
        /// <param name='headers'>
        /// A dictionary containing any optional headers to be sent to the server, in addition to
        /// any required by the protocol (new headers will overwrite base ones).
        /// </param>
        /// <param name='data'>
        /// The binary payload to be delivered, if JSON dialogue isn't enough for the request.
        /// </param>
        internal static System.Net.HttpWebRequest AssembleRequest(
         string destination,
         System.Collections.Generic.IDictionary<string, object> header,
         System.Collections.Generic.IDictionary<string, string> headers=null,
         System.IO.Stream data=null
        ){
            System.Net.HttpWebRequest request = (System.Net.HttpWebRequest)System.Net.WebRequest.Create(destination);
            request.Method = "POST";

            request.ContentType = "application/json";
            if(headers != null){
                foreach(System.Collections.Generic.KeyValuePair<string, string> h in headers){
                    request.Headers.Add(h.Key, h.Value);
                }
            }

            byte[] body = (new System.Text.UTF8Encoding()).GetBytes(new Jayrock.Json.JsonObject((System.Collections.IDictionary)header).ToString());
            if(data != null){
                Communication.EncodeMultipartFormdata(body, data, request.GetRequestStream());
                request.ContentType = Communication.FORM_CONTENT_TYPE;
            }else{
                request.GetRequestStream().Write(body, 0, body.Length);
            }

            return request;
        }

        /// <summary>
        /// Sends an assembled <c>request</c>.
        /// </summary>
        /// <returns>
        /// Any interesting properties and, depending on whether <c>output</c> is set, an attached stream.
        /// If <c>output</c> is provided, it is used instead. the or writing the result to that
        /// provided, seeking back to 0 in either case.
        /// </returns>
        /// <param name='request'>
        /// Request.
        /// </param>
        /// <param name='output'>
        /// Output.
        /// </param>
        /// <param name='timeout'>
        /// Timeout.
        /// </param>
        internal static Response SendRequest(System.Net.HttpWebRequest request, System.IO.Stream output=null, float timeout=10.0f){
            try{
                request.GetRequestStream().Close();
                Response r = new Response();
                using(System.Net.HttpWebResponse response = (System.Net.HttpWebResponse)request.GetResponse()){
                    using(System.IO.Stream stream = response.GetResponseStream()){
                        r.Properties = new System.Collections.Generic.Dictionary<string, object>();
                        string applied_compression = response.Headers.Get(Communication.HEADER_APPLIED_COMPRESSION);
                        if(applied_compression != null){
                            r.Properties.Add(Communication.PROPERTY_APPLIED_COMPRESSION, Compression.ResolveCompressionFormat(applied_compression));
                        }else{
                            r.Properties.Add(Communication.PROPERTY_APPLIED_COMPRESSION, null);
                        }
                        r.Properties.Add(Communication.PROPERTY_CONTENT_TYPE, response.ContentType);
                        if(output != null){
                            stream.CopyTo(output);
                            r.Properties.Add(Communication.PROPERTY_CONTENT_LENGTH, output.Length);
                            output.Seek(0, System.IO.SeekOrigin.Begin);
                            r.Data = output;
                        }else{
                            r.Data = new System.IO.MemoryStream();
                            stream.CopyTo(r.Data);
                            r.Data.Seek(0, System.IO.SeekOrigin.Begin);
                            r.Properties.Add(Communication.PROPERTY_CONTENT_LENGTH, response.ContentLength);
                        }
                    }
                }
                return r;
            }catch(System.Net.WebException e){
                if(e.Status == System.Net.WebExceptionStatus.ProtocolError && e.Response != null){
                    System.Net.HttpWebResponse response = (System.Net.HttpWebResponse)e.Response;
                    if(response.StatusCode == System.Net.HttpStatusCode.Forbidden){
                        throw new Exceptions.NotAuthorisedError("The requested operation could not be performed because an invalid key was provided");
                    }else if(response.StatusCode == System.Net.HttpStatusCode.NotFound){
                        throw new Exceptions.NotFoundError("The requested resource was not retrievable; it may have been deleted or net yet defined");
                    }else if(response.StatusCode == System.Net.HttpStatusCode.Conflict){
                        throw new Exceptions.InvalidRecordError("The uploaded request is structurally flawed and cannot be processed");
                    }else if(response.StatusCode == System.Net.HttpStatusCode.PreconditionFailed){
                        throw new Exceptions.InvalidHeadersError("One or more of the headers supplied (likely Content-Length) was rejected by the server");
                    }else if(response.StatusCode == System.Net.HttpStatusCode.ServiceUnavailable){
                        throw new Exceptions.TemporaryFailureError("The server was unable to process the request");
                    }
                    throw new Exceptions.ProtocolError("Unable to send message; code: " + response.StatusCode, e);
                }else if(e.Status == System.Net.WebExceptionStatus.ConnectFailure || e.Status == System.Net.WebExceptionStatus.NameResolutionFailure){
                    throw new Exceptions.URLError("Unable to send message: " + e.Message, e);
                }
                throw;
            }
        }
    }
}
