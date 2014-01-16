using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;

namespace RenEditors
{
    public static class Base
    {
        [System.Runtime.InteropServices.DllImport("PyAPI.dll")]
        private static extern int Init();

        [System.Runtime.InteropServices.DllImport("PyAPI.dll")]
        private static extern int ExecuteFunction(string name, string args, ref IntPtr value);

        [System.Runtime.InteropServices.DllImport("PyAPI.dll")]
        private static extern int ExecuteObjFunction(string id_obj, string name, string args, ref IntPtr value);

        [System.Runtime.InteropServices.DllImport("PyAPI.dll")]
        private static extern int GetProperty(string id, string name, string type, ref IntPtr value);

        [System.Runtime.InteropServices.DllImport("PyAPI.dll")]
        private static extern int FreeObject(string id);

        static Base()
        {
            int ret = Init();
            if (ret != 0) 
                throw new Exception("Python virtual machine cannot be initialized.");
        }

        public static string ExectueObjMethod(string id_obj, string name, string args)
        {
            IntPtr ptr = IntPtr.Zero;
            int ret = ExecuteObjFunction(id_obj, name, args, ref ptr);
            if (ret == -1)
            {
                string exc_txt = Marshal.PtrToStringUni(ptr);
                throw new Exception(exc_txt);
            }
            string s = Marshal.PtrToStringUni(ptr);
            return s;
        }

        public static string ExecuteMethod(string name, string args)
        {
            IntPtr ptr = IntPtr.Zero;
            int ret = ExecuteFunction(name, args, ref ptr);
            if (ret == -1)
            { 
                string exc_txt = Marshal.PtrToStringUni(ptr);
                throw new Exception(exc_txt);
            }
            string s = Marshal.PtrToStringUni(ptr);
            return s;
        }

        public static string GetProp(string id, string name, string type)
        {
            IntPtr ptr = IntPtr.Zero;
            int ret = GetProperty(id, name, type, ref ptr);
            if (ret == -1)
            {
                string exc_txt = Marshal.PtrToStringUni(ptr);
                throw new Exception(exc_txt);
            }
            string s = Marshal.PtrToStringUni(ptr);
            return s;
        }

        public static void Free(string id)
        {
            int ret = FreeObject(id);
            if (ret == -1)
                throw new Exception("Cannot free object, object doesn't exist ID = " + id);
        }
    }
}
