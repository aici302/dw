# -*- coding: utf-8 -*-

'''
This Source Code Form is subject to the terms of the Mozilla
Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.
'''

import json
import agent
import ctypes
import signal
import os
import platform
import time
import re
import subprocess
import stat
import utils

##### TO FIX 22/09/2021
try:
    TMP_bytes_to_str=utils.bytes_to_str
    TMP_str_to_bytes=utils.str_to_bytes
except:
    TMP_bytes_to_str=lambda b, enc="ascii": b.decode(enc, errors="replace")
    TMP_str_to_bytes=lambda s, enc="ascii": s.encode(enc, errors="replace")
try:    
    import sys
    if sys.version_info[0]==2:        
        if utils.path_exists(os.path.dirname(__file__) + os.sep + "__pycache__"):
            utils.path_remove(os.path.dirname(__file__) + os.sep + "__pycache__")
except: 
    None
##### TO FIX 22/09/2021


class Resource():

    def __init__(self, agent_main):
        self._agent_main=agent_main
        self._osnative = None
        if agent.is_windows():
            self._osnative = NativeWindows(self._agent_main)
        elif agent.is_linux():
            self._osnative = NativeLinux()
        elif agent.is_mac():
            self._osnative = NativeMac()
        
        
    def destroy(self,bforce):
        if self._osnative is not None:
            self._osnative.destroy()
            self._osnative = None
        return True
    
    def has_permission(self,cinfo):
        return self._agent_main.has_app_permission(cinfo,"resource"); 
    
    def req_systeminfo(self, cinfo ,params):
        ret = self._osnative.get_system_info()
        return json.dumps(ret)
        
    def req_listdiskpartition(self, cinfo ,params):
        ret = self._osnative.get_diskpartition_info()
        return json.dumps({"items": ret})
        
    def req_performanceinfo(self, cinfo ,params):
        ret = self._osnative.get_performance_info()
        return json.dumps(ret)

    def req_listtask(self, cinfo ,params):
        ret = self._osnative.get_task_list()
        #ORDINA PER NOME
        ret = sorted(ret, key=lambda k: k['Name'].lower()) 
        return json.dumps({"items":ret})
    
    def req_killtask(self, cinfo ,params):
        pid = agent.get_prop(params,"pid", None)
        bok = self._osnative.task_kill(int(pid));
        ret = json.dumps({"ok":bok})
        return ret
    
    def req_listservice(self, cinfo ,params):
        ret = self._osnative.get_service_list()
        #ORDINA PER NOME
        ret = sorted(ret, key=lambda k: k['Name'].lower()) 
        return json.dumps({"items":ret})
        
    def req_startservice(self, cinfo ,params):
        name = agent.get_prop(params,"name", None)
        bok = self._osnative.service_start(name);
        ret = json.dumps({"ok":bok})
        return ret
    
    def req_stopservice(self, cinfo ,params):
        name = agent.get_prop(params,"name", None)
        bok = self._osnative.service_stop(name);
        ret = json.dumps({"ok":bok})
        return ret

class NativeWindows:
    
    def __init__(self,agent_main):
        self._agent_main=agent_main
        self._osmodule = self._agent_main.load_lib("osutil")

    def destroy(self):
        self._agent_main.unload_lib("osutil")
        self._osmodule=None;
    
    def get_system_info(self):
            
        ##### TO FIX 22/09/2021
        if hasattr(self._osmodule, "DWAOSUtilGetSystemInfo"):
            wcp = ctypes.c_wchar_p()
            sz=self._osmodule.DWAOSUtilGetSystemInfo(ctypes.byref(wcp))
            if sz>0:
                s = ctypes.wstring_at(wcp,size=sz)
            self._osmodule.freeMemory(wcp)
        else:
            pi=self._osmodule.getSystemInfo()
            s=""
            if pi:
                s = ctypes.wstring_at(pi)
                self._osmodule.freeMemory(pi)
        ##### TO FIX 22/09/2021
        
        return json.loads(s)
    
    def get_diskpartition_info(self):
        '''
        res = []
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()
        for letter in string.uppercase:
            if bitmask & 1:
                nm = letter+":\\"
                total_bytes = ctypes.c_ulonglong(0)
                free_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(nm), None, ctypes.pointer(total_bytes), ctypes.pointer(free_bytes))
                info = { "Name" : nm,  
                            "Size": total_bytes.value  , 
                            "Free": free_bytes.value 
                        }
                res.append(info)
            bitmask >>= 1
        return res
        '''
        
        ##### TO FIX 22/09/2021
        if hasattr(self._osmodule, "DWAOSUtilGetDiskInfo"):
            wcp = ctypes.c_wchar_p()
            sz=self._osmodule.DWAOSUtilGetDiskInfo(ctypes.byref(wcp))
            if sz>0:
                s = ctypes.wstring_at(wcp,size=sz)
            self._osmodule.freeMemory(wcp)
        else:
            pi=self._osmodule.getDiskInfo()
            s=""
            if pi:
                s = ctypes.wstring_at(pi)
                self._osmodule.freeMemory(pi)
        ##### TO FIX 22/09/2021
            
        return json.loads(s)
    
    def get_performance_info(self):
        
        ##### TO FIX 22/09/2021
        if hasattr(self._osmodule, "DWAOSUtilGetPerformanceInfo"):
            wcp = ctypes.c_wchar_p()
            sz=self._osmodule.DWAOSUtilGetPerformanceInfo(ctypes.byref(wcp))
            if sz>0:
                s = ctypes.wstring_at(wcp,size=sz)
            self._osmodule.freeMemory(wcp)
        else:
            pi=self._osmodule.getPerformanceInfo()
            s=""
            if pi:
                s = ctypes.wstring_at(pi)
                self._osmodule.freeMemory(pi)
        ##### TO FIX 22/09/2021
        
        return json.loads(s)  
        
    def get_task_list(self):
        
        ##### TO FIX 22/09/2021
        if hasattr(self._osmodule, "DWAOSUtilGetTaskList"):
            wcp = ctypes.c_wchar_p()
            sz=self._osmodule.DWAOSUtilGetTaskList(ctypes.byref(wcp))
            if sz>0:
                s = ctypes.wstring_at(wcp,size=sz)
            self._osmodule.freeMemory(wcp)
        else:
            pi=self._osmodule.getTaskList()
            s=""
            if pi:
                s = ctypes.wstring_at(pi)
                self._osmodule.freeMemory(pi)
        ##### TO FIX 22/09/2021
        
        return json.loads(s)
    
    def task_kill(self, pid):
        bret = self._osmodule.taskKill(pid)
        return bret==1
    
    def get_service_list(self):
        
        ##### TO FIX 22/09/2021
        if hasattr(self._osmodule, "DWAOSUtilGetServiceList"):
            wcp = ctypes.c_wchar_p()
            sz=self._osmodule.DWAOSUtilGetServiceList(ctypes.byref(wcp))
            if sz>0:
                s = ctypes.wstring_at(wcp,size=sz)
            self._osmodule.freeMemory(wcp)
        else:
            pi=self._osmodule.getServiceList()
            s=""
            if pi:
                s = ctypes.wstring_at(pi)
                self._osmodule.freeMemory(pi)
        ##### TO FIX 22/09/2021
                
        return json.loads(s)
    
    def service_start(self,name):
        bret = self._osmodule.startService(name)
        return bret==1
    
    def service_stop(self,name):
        bret = self._osmodule.stopService(name)
        return bret==1

class NativeLinux:
    def __init__(self):
        self._PAGESIZE = os.sysconf("SC_PAGE_SIZE")
        self._oldcputime=None
    
    def _read_cpu_raw(self):
        try:
            with open('/proc/stat', 'r') as f:
                for line in f:
                    if line.startswith('cpu '):
                        fields = [float(x) for x in line.split()[1:]]
    
                        # 0: user, 1: nice, 2: system, 3: idle, 4: iowait, 5: irq, 6: softirq, 7: steal
                        if len(fields) < 8:
                            return 0.0, 0.0
                        
                        idle = fields[3] + fields[4]
                        non_idle = fields[0] + fields[1] + fields[2] + fields[5] + fields[6] + fields[7]
                        total = idle + non_idle
    
                        return idle, sum(fields)
        except Exception as e:
            None
        return 0.0, 0.0
    
    def destroy(self):
        None
   
    def get_system_info(self):
        hmcpu={}
        f = utils.file_open("/proc/cpuinfo", "r", encoding="utf8", errors='replace')
        try:
            for line in f:
                if line.startswith("model name"):
                    ar = line.split(":")
                    n = ar[1].strip()
                    if n not in hmcpu:
                        hmcpu[n]=1
                    else:
                        hmcpu[n]=hmcpu[n]+1
        finally:
            f.close()
        cpuName=""
        for k in hmcpu:
            if cpuName!="":
                cpuName+= ", " 
            cpuName+=k
        return  {"osName":platform.platform(),  "osUpdate":"", "osBuild":platform.version(), "pcName":platform.node() , "cpuName":cpuName,  "cpuArchitecture":platform.machine()}
    
    def get_diskpartition_info(self):
        arret = []
        phydevs = []
        f = utils.file_open("/proc/filesystems", "r", encoding="utf8", errors='replace')
        try:
            for line in f:
                if not line.startswith("nodev"):
                    phydevs.append(line.strip())
        finally:
            f.close()
        
        if self._which("mount"):
            p = subprocess.Popen(["mount"], stdout=subprocess.PIPE)
            (po, pe) = p.communicate()
            p.wait()
            if po is not None and len(po)>0:
                po=TMP_bytes_to_str(po,"utf8")
                appar = po.split("\n")
                for appln in appar:
                    parts = appln.split()
                    if len(parts) >= 5:
                        dv = parts[0]
                        nm = parts[2]
                        tp = parts[4]
                        if tp in phydevs: 
                            path=nm
                            st = os.statvfs(path)
                            free = (st.f_bavail * st.f_frsize)
                            size = (st.f_blocks * st.f_frsize)
                            arret.append({"Name":nm, "Size":size, "Free":free})
        else:
            f = utils.file_open("/etc/fstab", "r", encoding="utf8", errors='replace')
            try:
                for line in f:
                    line=line.strip()
                    if not line.strip().startswith("#"):
                        line=line.replace('\t',' ')
                        ar=[]
                        arapp = line.split(" ")
                        for a in arapp:
                            if a.strip()!="":
                                ar.append(a.strip())
                        if len(ar)>=3:
                            nm = ar[1]
                            tp = ar[2]
                            if tp in phydevs:
                                path=nm
                                st = os.statvfs(path)
                                free = (st.f_bavail * st.f_frsize)
                                size = (st.f_blocks * st.f_frsize)
                                arret.append({"Name":nm, "Size":size, "Free":free})
            finally:
                f.close()
        return arret    
    
    def get_performance_info(self):
        ret  = {}
        
        #cpu
        cpuUsagePerc=0
        curr_cpu_idle, curr_cpu_total = self._read_cpu_raw()
        if self._oldcputime is not None:
            delta_cpu_total = curr_cpu_total - self._oldcputime["prev_cpu_total"]
            delta_cpu_idle = curr_cpu_idle - self._oldcputime["prev_cpu_idle"]
            cpuUsagePerc = (1.0 - (delta_cpu_idle / delta_cpu_total)) * 100 if delta_cpu_total > 0 else 0.0
        else:
            self._oldcputime={}
        self._oldcputime["prev_cpu_idle"]=curr_cpu_idle
        self._oldcputime["prev_cpu_total"]=curr_cpu_total             
        ret["cpuUsagePerc"]=cpuUsagePerc
        
        
        #memory
        f = utils.file_open('/proc/meminfo', 'rb', encoding="utf8", errors='replace')
        memoryPhysicalTotal=0
        memoryPhysicalAvailable=-1
        memoryFree=0
        memoryVirtualTotal=0
        memoryVirtualAvailable=0
        try:
            for line in f:
                if line.startswith("MemTotal:"):
                    memoryPhysicalTotal = int(line.split()[1]) * 1024
                elif line.startswith("MemFree:"):
                    memoryFree = int(line.split()[1]) * 1024
                elif line.startswith("MemAvailable:"):
                    memoryPhysicalAvailable = int(line.split()[1]) * 1024
                elif line.startswith("SwapTotal:"):
                    memoryVirtualTotal = int(line.split()[1]) * 1024
                elif line.startswith("SwapFree:"):
                    memoryVirtualAvailable = int(line.split()[1]) * 1024
        finally:
            f.close()
        
        ret["memoryPhysicalTotal"]=memoryPhysicalTotal
        if memoryPhysicalAvailable==-1:
            memoryPhysicalAvailable=memoryFree
        ret["memoryPhysicalAvailable"]=memoryPhysicalAvailable
        ret["memoryVirtualTotal"]=memoryVirtualTotal
        ret["memoryVirtualAvailable"]=memoryVirtualAvailable
        ret["memoryTotal"]=ret["memoryPhysicalTotal"]+ret["memoryVirtualTotal"]
        ret["memoryAvailable"]=ret["memoryPhysicalAvailable"]+ret["memoryVirtualAvailable"]
        return ret        
        
    def get_task_list(self):
        import pwd
        ret = []
        for x in utils.path_list('/proc') :
            if x.isdigit():
                try:
                    itm={}
                    #PID
                    itm["PID"]=int(x)
                    #Name
                    f = utils.file_open("/proc/%s/stat" % x, encoding="utf8", errors='replace')
                    try:
                        itm["Name"] = f.read().split(' ')[1].replace('(', '').replace(')', '')
                    finally:
                        f.close()
                    #Memory
                    f = utils.file_open("/proc/%s/statm" % x, encoding="utf8", errors='replace')
                    try:
                        vms, rss = f.readline().split()[:2]
                        itm["Memory"] = int(rss) * int(self._PAGESIZE)
                        #int(vms) * _PAGESIZE)
                    finally:
                        f.close()
                    #Owner
                    f = utils.file_open("/proc/%s/status" % x, encoding="utf8", errors='replace')
                    try:
                        for line in f:
                            if line.startswith('Uid:'):
                                    r = line.split()
                                    itm["Owner"] = pwd.getpwuid(int(r[1])).pw_name
                                    break
                    finally:
                        f.close()
                    ret.append(itm)
                except:
                    None
        return ret
    
    def task_kill(self, pid):
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError as e:
            return False
        return True
    
    def _which(self, name):
        p = subprocess.Popen(["which", name], stdout=subprocess.PIPE)
        (po, pe) = p.communicate()
        p.wait()
        return len(po) > 0        
    
    def _get_status_from_output(self, po):
        st = 999
        if "running" in po.lower() or "started" in po.lower() or ("active" in po.lower() and not "inactive" in po.lower()):
            st = 4
        elif "not running" in po.lower() or "not started" in po.lower() or "stopped" in po.lower() or "inactive" in po.lower() or "dead" in po.lower() or "failed" in po.lower():
            st = 1
        return st
    
    def get_service_list(self):
        ret=[]
        if self._which("systemctl"):
            p = subprocess.Popen(["systemctl","--all","--full","list-units"], stdout=subprocess.PIPE)
            (po, pe) = p.communicate()
            p.wait()
            if po is not None and len(po)>0:
                po=TMP_bytes_to_str(po,"utf8")
                appar = po.split("\n")
                for appln in appar:
                    if ".service" in appln:
                        sv = ""
                        stcnt = -1
                        stapp = ""
                        ar = appln.split(" ")
                        for k in ar:
                            if len(k)>0:
                                if stcnt == -1:
                                    if k.endswith(".service"):
                                        sv+=k[0:len(k)-8]
                                        stcnt+=1
                                    else:
                                        sv+=k
                                else:
                                    stcnt+=1
                                    if stcnt==3:
                                        stapp=k
                        if stcnt != -1:
                            if  stapp == "running":
                                st = 4
                            else:
                                st = 1
                            ret.append({"Name":sv,"Label":"","Status":st})
        else:
            #SYSVINIT O OPENRC
            bopenrc=self._which("openrc") and self._which("rc-service")
            for x in utils.path_list('/etc/init.d'):
                if x.lower()!="rc" and x.lower()!="rcs" and x.lower()!="halt" and x.lower()!="reboot" and x.lower()!="single":
                    po=None
                    if bopenrc:
                        p = subprocess.Popen(["rc-service", x, "status"], stdout=subprocess.PIPE)
                        (po, _) = p.communicate()
                        p.wait()
                    else:
                        xp = "/etc/init.d/" + x
                        st = utils.path_stat(xp)
                        if bool(st.st_mode & stat.S_IXUSR) or bool(st.st_mode & stat.S_IXGRP) or bool(st.st_mode & stat.S_IXOTH):                                                
                            p = subprocess.Popen(["/etc/init.d/" + x, "status"], stdout=subprocess.PIPE)
                            (po, _) = p.communicate()
                            p.wait()
                    if po is not None and len(po)>0:
                        po=TMP_bytes_to_str(po,"utf8")
                        st = self._get_status_from_output(po)
                        ret.append({"Name":x,"Label":"","Status":st})
        return ret
    
    def _is_valid_name(self, name):
        ar=self.get_service_list()
        for itm in ar:
            if name==itm["Name"]:
                return True
        return False
    
    def service_start(self, name):
        if not self._is_valid_name(name):
            return False
        if self._which("systemctl"):
            #SYSTEMD
            p = subprocess.Popen(["systemctl","start", name + ".service"], stdout=subprocess.PIPE)
            (po, pe) = p.communicate()
            p.wait()
            return (po is None or len(po)==0) and (pe is None or len(pe)==0)
        else:
            #SYSVINIT O OPENRC
            bopenrc=self._which("openrc") and self._which("rc-service")            
            if bopenrc:
                p = subprocess.Popen(["rc-service", name, "start"], stdout=subprocess.PIPE)
                (po, pe) = p.communicate()
                p.wait()
                p = subprocess.Popen(["rc-service", name, "status"], stdout=subprocess.PIPE)
                (po, pe) = p.communicate()
                p.wait()
            else:
                p = subprocess.Popen(["/etc/init.d/" + name, "start"], stdout=subprocess.PIPE)
                (po, pe) = p.communicate()
                p.wait()
                p = subprocess.Popen(["/etc/init.d/" + name, "status"], stdout=subprocess.PIPE)
                (po, pe) = p.communicate()
                p.wait()
            if po is not None and len(po)>0:
                po=TMP_bytes_to_str(po,"utf8")
                return self._get_status_from_output(po)==4 #STARTES
            else:
                return False
        
    
    def service_stop(self, name):
        if not self._is_valid_name(name):
            return False
        if self._which("systemctl"):
            #SYSTEMD
            p = subprocess.Popen(["systemctl","stop", name + ".service"], stdout=subprocess.PIPE)
            (po, pe) = p.communicate()
            p.wait()
            return (po is None or len(po)==0) and (pe is None or len(pe)==0)
        else:
            #SYSVINIT O OPENRC
            bopenrc=self._which("openrc") and self._which("rc-service")            
            if bopenrc:
                p = subprocess.Popen(["rc-service", name, "stop"], stdout=subprocess.PIPE)
                (po, pe) = p.communicate()
                p.wait()
                p = subprocess.Popen(["rc-service", name, "status"], stdout=subprocess.PIPE)
                (po, pe) = p.communicate()
                p.wait()
            else:
                p = subprocess.Popen(["/etc/init.d/" + name, "stop"], stdout=subprocess.PIPE)
                (po, pe) = p.communicate()
                p.wait()
                p = subprocess.Popen(["/etc/init.d/" + name, "status"], stdout=subprocess.PIPE)
                (po, pe) = p.communicate()
                p.wait()
            if po is not None and len(po)>0:
                po=TMP_bytes_to_str(po,"utf8")
                return self._get_status_from_output(po)==1 #STOPPED
            else:
                return False
       
class NativeMac:
    
    def __init__(self):
        self._PAGESIZE = os.sysconf("SC_PAGE_SIZE")
        
    def destroy(self):
        None
   
    def get_system_info(self):
        cpuName=""
        try:
            appout = subprocess.Popen(["sysctl", "machdep.cpu.brand_string"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate() 
            lines = TMP_bytes_to_str(appout[0]).splitlines()
            for l in lines:
                try:
                    idx = l.index(':')
                    cpuName=l[idx+1:].strip()
                    break
                except:
                    None
        except:
            None
        return  {"osName":platform.platform(),  "osUpdate":"", "osBuild":platform.version(), "pcName":platform.node() , "cpuName":cpuName,  "cpuArchitecture":platform.machine()}
    
    def _parse_plist(self, xml_text):
        
        def convert(node):
            tag = node.tag
    
            if tag == "dict":
                d = {}
                children = list(node)
                i = 0
                while i < len(children):
                    key_node = children[i]
                    val_node = children[i + 1]
                    key = key_node.text
                    d[key] = convert(val_node)
                    i += 2
                return d
    
            if tag == "array":
                return [convert(child) for child in node]
    
            if tag == "string":
                return node.text or ""
    
            if tag == "integer":
                return int(node.text or "0")
    
            if tag == "real":
                return float(node.text or "0")
    
            if tag == "true":
                return True
    
            if tag == "false":
                return False
    
            if tag == "date":
                return node.text or ""
    
            if tag == "data":
                return node.text or ""
    
            return node.text or ""
        
        import xml.etree.ElementTree as ET
        root = ET.fromstring(xml_text)
        first_child = list(root)[0]
        return convert(first_child)        
    
    def get_diskpartition_info(self):
        arret = []
        try:
            appout = subprocess.Popen(["diskutil", "list", "-plist"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            data=self._parse_plist(TMP_bytes_to_str(appout[0]))
            
            '''
            for disk in data.get("AllDisksAndPartitions", []):
                device = disk.get("DeviceIdentifier")
                if not device:
                    continue
            '''    
            '''
            appout = subprocess.Popen(["diskutil", "info", "-plist", device], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            info = self._parse_plist(TMP_bytes_to_str(appout[0]))
            
            mount = info.get("MountPoint") or ""
            if not mount:
                continue
            
            name = info.get("VolumeName") or info.get("MediaName") or device
            size = int(info.get("TotalSize", 0))                
            #free = int(info.get("FreeSpace", 0))
            try:
                st = os.statvfs(mount)
                free = st.f_bavail * st.f_frsize
            except OSError:
                free = 0
    
            arret.append({"Name": name, "Size": size, "Free": free})
            '''
            
            #for part in disk.get("Partitions", []):
            #    part_id = part.get("DeviceIdentifier")
            #    if not part_id:
            #        continue
            for part_id in data.get("AllDisks", []):
                try:
                    appout = subprocess.Popen(["diskutil", "info", "-plist", part_id], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
                    info = self._parse_plist(TMP_bytes_to_str(appout[0]))
                    
                    #fs_type = (info.get("FileSystemType") or info.get("FilesystemType") or "").upper()
                    #arret.append({"Name": part_id + " " + fs_type, "Size": 10000, "Free": 0})
                    
                    mount = info.get("MountPoint") or ""
                    if mount is not None and mount!="" and not mount.lower().startswith("/system/volumes/") and (info.get("VolumeName") or "").lower() not in {"preboot", "recovery", "vm", "update"}:
                        fs_type = (info.get("FileSystemType") or info.get("FilesystemType") or "").lower()
                        content = (info.get("Content") or "").lower()                        
                        if "apfs" in fs_type or "apfs" in content or "hfs" in fs_type or "hfs" in content:                            
                            name = info.get("VolumeName") or info.get("MediaName") or part_id
                            size = int(info.get("TotalSize", 0))
                            try:
                                st = os.statvfs(mount)
                                free = st.f_bavail * st.f_frsize                        
                            except OSError:
                                free = 0
                
                            arret.append({"Name": name, "Size": size, "Free": free})
                except:
                    None
                
        except:
            None
        return arret
    
    '''
    def get_diskpartition_info(self):
        arret = []
        try:
            appout = subprocess.Popen(["diskutil", "info", "/"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate() 
            lines = TMP_bytes_to_str(appout[0]).splitlines()
            size=0
            free=0
            for l in lines:
                if len(l.strip())>0:
                    try:
                        idx = l.index(':')
                        key=l[:idx].strip()
                        if key.lower()=="total size":
                            try:
                                iapp1 = l.index('(')
                                iapp2 = l.index(' ',iapp1)
                                size=int(l[iapp1+1:iapp2].strip())
                            except:
                                None
                        elif key.lower()=="volume free space":
                            try:
                                iapp1 = l.index('(')
                                iapp2 = l.index(' ',iapp1)
                                free=int(l[iapp1+1:iapp2].strip())
                            except:
                                None
                    except:
                        None
            arret.append({"Name":"/", "Size":size, "Free":free})
        except:
            None
        return arret
        
    '''
    
    def get_performance_info(self):
        ret  = {}
        ret["cpuUsagePerc"]=0
        ret["memoryPhysicalTotal"]=0
        ret["memoryPhysicalAvailable"]=0
        ret["memoryVirtualTotal"]=0
        ret["memoryVirtualAvailable"]=0
        
        #CPU
        try:
            appout = subprocess.Popen(["iostat", "-c", "2"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            lines = TMP_bytes_to_str(appout[0]).splitlines()
            cnt=0
            idxus=-1
            idxsy=-1 
            for l in lines:
                cnt+=1
                if cnt==2:
                    ar = l.strip().split();
                    for idx in range(len(ar)):
                        if ar[idx]=="us":
                            idxus=idx
                        elif ar[idx]=="sy":
                            idxsy=idx
                if cnt==4 and idxus!=-1 and idxsy!=-1:
                    if len(l.strip())>0:
                        ar = l.strip().split();
                        cpu = float(ar[6]) + float(ar[7]) 
                        ret["cpuUsagePerc"]=cpu
                    break    
        except Exception as e:
            None
        
        #MEMORIA
        try:
            ps = TMP_bytes_to_str(subprocess.Popen(['ps', '-caxm', '-orss,comm'], stdout=subprocess.PIPE).communicate()[0])
            vm = TMP_bytes_to_str(subprocess.Popen(['vm_stat'], stdout=subprocess.PIPE).communicate()[0])
            processLines = ps.split('\n')
            sep = re.compile('[\\s]+')
            for row in range(1,len(processLines)):
                rowText = processLines[row].strip()
                rowElements = sep.split(rowText)
                try:
                    rss = float(rowElements[0]) * 1024
                except:
                    rss = 0 
            vmLines = vm.split('\n')
            sep = re.compile(':[\\s]+')
            vmStats = {}
            for row in range(1,len(vmLines)-2):
                rowText = vmLines[row].strip()
                rowElements = sep.split(rowText)
                vmStats[(rowElements[0])] = int(rowElements[1].strip('\\.')) * 4096
            
            ret["memoryPhysicalTotal"]=vmStats["Pages wired down"]+vmStats["Pages active"]+vmStats["Pages inactive"]+vmStats["Pages free"]
            ret["memoryPhysicalAvailable"]= vmStats["Pages wired down"]+vmStats["Pages active"]+vmStats["Pages inactive"]
        except Exception as e:
            None
        
        ret["memoryTotal"]=ret["memoryPhysicalTotal"]+ret["memoryVirtualTotal"]
        ret["memoryAvailable"]=ret["memoryPhysicalAvailable"]+ret["memoryVirtualAvailable"]
        return ret        
        
    def get_task_list(self):
        ret = []
        try:
            size_pid=10;
            size_user=200;
            size_rss=50;
            size_comm=200;
            appout = subprocess.Popen(["ps", "-axc", "-o", "pid=" + ("-"*size_pid) + ",user=" + ("-"*size_user) + ",rss=" + ("-"*size_rss) + ",comm=" + ("-"*size_comm)], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate() 
            lines = TMP_bytes_to_str(appout[0]).splitlines()
            bfirst=True
            for l in lines:
                if not bfirst:
                    itm={}
                    p=0
                    try:
                        itm["PID"]=int(l[p:p+size_pid].strip())
                    except:
                        itm["PID"]=-1
                    p=p+size_pid+1
                    itm["Owner"] = l[p:p+size_user].strip()
                    p=p+size_user+1
                    try:
                        itm["Memory"] = int(l[p:p+size_rss].strip())
                    except: 
                        itm["Memory"] = 0
                    p=p+size_rss+1
                    itm["Name"] = l[p:p+size_comm].strip()
                    ret.append(itm)
                bfirst=False
            ret.remove(ret[len(ret)-1]) #ELIMINA IL COMANDO CORRENTE PS
        except:
            None
        return ret
    
    def task_kill(self, pid):
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError as e:
            return False
        return True
    
    
    def _get_service_list(self):
        ret={}
        import xml.etree.ElementTree as ET
        paths=["/System/Library/LaunchDaemons","/Library/LaunchDaemons"]
        for path in paths:
            for x in utils.path_list(path):
                try:
                    if x.endswith(".plist"):
                        bok=False
                        tree = ET.parse(path + "/" + x)
                        root = tree.getroot()
                        for ar in root:
                            if ar.tag=="dict":
                                for child in ar:
                                    if bok==True:
                                        if child.tag.lower()=="string":
                                            ret[child.text]=path + "/" + x
                                            break
                                    if child.tag.lower()=="key" and child.text.lower()=="label":
                                        bok=True
                            if bok==True:
                                break     
                except Exception as e:
                    None
        return ret
    
    '''
    def _get_service_status(self,name):
        try:
            appout = subprocess.Popen(["launchctl", "list", name], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            lines = TMP_bytes_to_str(appout[0]).splitlines()
            for l in lines:
                if "LastExitStatus" in l:
                    return 4
            return 1
        except:
            return 999
    
    
    def get_service_list(self):
        ret=[]
        hmsvc = self._get_service_list()
        for s in hmsvc:
            st=self._get_service_status(s)
            ret.append({"Name":s,"Label":"","Status":st})
        return ret

    '''
    
    def get_service_list(self):
        arstatus={}
        appout = subprocess.Popen(["launchctl", "list"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        lines = TMP_bytes_to_str(appout[0]).splitlines()    
        for line in lines:
            line = line.strip()
            if not line:
                continue
    
            if line.lower().startswith("pid") or line.lower().startswith("load"):
                continue
    
            parts = line.split(None, 2)
            if len(parts) < 3:
                continue
    
            pid_raw, status_raw, label = parts
            '''            
            running = pid_raw != "-"            
            pid = None if pid_raw == "-" else int(pid_raw)
    
            try:
                exit_status = int(status_raw)
            except ValueError:
                exit_status = None
            '''
            if pid_raw != "-": #RUNNING
                st=4;
            else:
                st=1;
            arstatus[label]=st
            
        ret=[]
        hmsvc = self._get_service_list()
        for s in hmsvc:
            if s in arstatus:
                st=arstatus[s]
            else:
                st=1
            ret.append({"Name":s,"Label":"","Status":st})
        return ret
    
    def service_start(self, name):
        try:
            hmsvc = self._get_service_list()
            if name in hmsvc:
                p = subprocess.Popen(["launchctl", "load", "-F", hmsvc[name]], stdout=subprocess.PIPE)
                (po, pe) = p.communicate()
                p.wait()
                return (po is None or len(po)==0) and (pe is None or len(pe)==0)
            return False
        except:
            return False
        
    
    def service_stop(self, name):
        try:
            hmsvc = self._get_service_list()
            if name in hmsvc:
                p = subprocess.Popen(["launchctl", "unload", hmsvc[name]], stdout=subprocess.PIPE)
                (po, pe) = p.communicate()
                p.wait()
                return (po is None or len(po)==0) and (pe is None or len(pe)==0)
            return False
        except:
            return False
