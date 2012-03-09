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
    /// Contains statistics about the server's current status.
    /// </summary>
    public class Status{
        /// <summary>
        /// Details about the executing process on the server.
        /// </summary>
        public StatusProcess Process;
        /// <summary>
        /// Details about the server as a host.
        /// </summary>
        public StatusSystem System;

        /// <summary>
        /// Extracts status information from the server's response.
        /// </summary>
        /// <param name='status'>
        /// The structure to be dissected.
        /// </param>
        internal Status(System.Collections.Generic.IDictionary<string, object> status){
            this.Process = new StatusProcess((System.Collections.Generic.IDictionary<string, object>)status["process"]);
            this.System = new StatusSystem((System.Collections.Generic.IDictionary<string, object>)status["system"]);
        }
    }

    /// <summary>
    /// Contains statistics about the executing process.
    /// </summary>
    public class StatusProcess{
        /// <summary>
        /// Details about the process's CPU usage.
        /// </summary>
        public StatusProcessCpu Cpu;
        /// <summary>
        /// Details about the process's memory usage.
        /// </summary>
        public StatusProcessMemory Memory;
        /// <summary>
        /// The number of the threads the process is currently using.
        /// </summary>
        public uint Threads;

        /// <summary>
        /// Extracts process information from the server's response.
        /// </summary>
        /// <param name='process'>
        /// The structure to be dissected.
        /// </param>
        internal StatusProcess(System.Collections.Generic.IDictionary<string, object> process){
            this.Cpu = new StatusProcessCpu((System.Collections.Generic.IDictionary<string, object>)process["cpu"]);
            this.Memory = new StatusProcessMemory((System.Collections.Generic.IDictionary<string, object>)process["memory"]);
            this.Threads = (uint)((Jayrock.Json.JsonNumber)process["threads"]).ToInt32();
        }
    }

    /// <summary>
    /// Contains statistics about the executing process's CPU usage.
    /// </summary>
    public class StatusProcessCpu{
        /// <summary>
        /// The current percentage of CPU power in use.
        /// </summary>
        public float Percent;

        /// <summary>
        /// Extracts CPU information from the server's response.
        /// </summary>
        /// <param name='cpu'>
        /// The structure to be dissected.
        /// </param>
        internal StatusProcessCpu(System.Collections.Generic.IDictionary<string, object> cpu){
            this.Percent = ((Jayrock.Json.JsonNumber)cpu["percent"]).ToSingle();
        }
    }

    /// <summary>
    /// Contains statistics about the executing process's memory usage.
    /// </summary>
    public class StatusProcessMemory{
        /// <summary>
        /// The current percentage of memory in use.
        /// </summary>
        public float Percent;
        /// <summary>
        /// The number of bytes of resident memory.
        /// </summary>
        public ulong Rss;

        /// <summary>
        /// Extracts memory information from the server's response.
        /// </summary>
        /// <param name='memory'>
        /// The structure to be dissected.
        /// </param>
        internal StatusProcessMemory(System.Collections.Generic.IDictionary<string, object> memory){
            this.Percent = ((Jayrock.Json.JsonNumber)memory["percent"]).ToSingle();
            this.Rss = (ulong)((Jayrock.Json.JsonNumber)memory["rss"]).ToInt64();
        }
    }

    /// <summary>
    /// Contains statistics about the host.
    /// </summary>
    public class StatusSystem{
        /// <summary>
        /// Details about the host's load.
        /// </summary>
        public StatusSystemLoad Load;

        /// <summary>
        /// Extracts system information from the server's response.
        /// </summary>
        /// <param name='system'>
        /// The structure to be dissected.
        /// </param>
        internal StatusSystem(System.Collections.Generic.IDictionary<string, object> system){
            this.Load = new StatusSystemLoad((System.Collections.Generic.IDictionary<string, object>)system["load"]);
        }
    }

    /// <summary>
    /// Contains details about the host's load.
    /// </summary>
    public class StatusSystemLoad{
        /// <summary>
        /// The load-average over the past minute.
        /// </summary>
        public float T1;
        /// <summary>
        /// The load-average over the past five minutes.
        /// </summary>
        public float T5;
        /// <summary>
        /// The load-average over the past fifteen minutes.
        /// </summary>
        public float T15;

        /// <summary>
        /// Extracts load information from the server's response.
        /// </summary>
        /// <param name='load'>
        /// The structure to be dissected.
        /// </param>
        internal StatusSystemLoad(System.Collections.Generic.IDictionary<string, object> load){
            this.T1 = ((Jayrock.Json.JsonNumber)load["t1"]).ToSingle();
            this.T5 = ((Jayrock.Json.JsonNumber)load["t5"]).ToSingle();
            this.T15 = ((Jayrock.Json.JsonNumber)load["t15"]).ToSingle();
        }
    }
}

