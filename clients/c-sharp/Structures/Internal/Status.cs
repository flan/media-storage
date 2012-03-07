// 
//  Status.cs
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
    public class Status{
        public StatusProcess Process;
        public StatusSystem System;

        internal Status(System.Collections.Generic.IDictionary<string, object> status){
            this.Process = new StatusProcess((System.Collections.Generic.IDictionary<string, object>)status["process"]);
            this.System = new StatusSystem((System.Collections.Generic.IDictionary<string, object>)status["system"]);
        }
    }

    public class StatusProcess{
        public StatusProcessCpu Cpu;
        public StatusProcessMemory Memory;
        public uint Threads;

        public StatusProcess(System.Collections.Generic.IDictionary<string, object> process){
            this.Cpu = new StatusProcessCpu((System.Collections.Generic.IDictionary<string, object>)process["cpu"]);
            this.Memory = new StatusProcessMemory((System.Collections.Generic.IDictionary<string, object>)process["memory"]);
            this.Threads = (uint)((Jayrock.Json.JsonNumber)process["threads"]).ToInt32();
        }
    }

    public class StatusProcessCpu{
        public float Percent;

        public StatusProcessCpu(System.Collections.Generic.IDictionary<string, object> cpu){
            this.Percent = ((Jayrock.Json.JsonNumber)cpu["percent"]).ToSingle();
        }
    }

    public class StatusProcessMemory{
        public float Percent;
        public ulong Rss;

        public StatusProcessMemory(System.Collections.Generic.IDictionary<string, object> memory){
            this.Percent = ((Jayrock.Json.JsonNumber)memory["percent"]).ToSingle();
            this.Rss = (ulong)((Jayrock.Json.JsonNumber)memory["rss"]).ToInt64();
        }
    }

    public class StatusSystem{
        public StatusSystemLoad Load;

        public StatusSystem(System.Collections.Generic.IDictionary<string, object> system){
            this.Load = new StatusSystemLoad((System.Collections.Generic.IDictionary<string, object>)system["load"]);
        }
    }

    public class StatusSystemLoad{
        public float T1;
        public float T5;
        public float T15;

        public StatusSystemLoad(System.Collections.Generic.IDictionary<string, object> load){
            this.T1 = ((Jayrock.Json.JsonNumber)load["t1"]).ToSingle();
            this.T5 = ((Jayrock.Json.JsonNumber)load["t5"]).ToSingle();
            this.T15 = ((Jayrock.Json.JsonNumber)load["t15"]).ToSingle();
        }
    }
}

