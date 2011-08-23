using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace RenmasWPF
{
    class Renmas
    {
        [System.Runtime.InteropServices.DllImport("RenmasAPI.dll")]
        public static extern int Init();
        [System.Runtime.InteropServices.DllImport("RenmasAPI.dll")]
        public static extern void ShutDown();
        [System.Runtime.InteropServices.DllImport("RenmasAPI.dll")]
        public static extern int RunScript(string filename);
        [System.Runtime.InteropServices.DllImport("RenmasAPI.dll")]
        public static extern int WidthImage();
        [System.Runtime.InteropServices.DllImport("RenmasAPI.dll")]
        public static extern int HeightImage();
        [System.Runtime.InteropServices.DllImport("RenmasAPI.dll")]
        public static extern int PitchImage();
        [System.Runtime.InteropServices.DllImport("RenmasAPI.dll")]
        public static extern uint PtrImage();
        [System.Runtime.InteropServices.DllImport("RenmasAPI.dll")]
        public static extern int Render();
        [System.Runtime.InteropServices.DllImport("RenmasAPI.dll")]
        public static extern int IsFinished();
        [System.Runtime.InteropServices.DllImport("RenmasAPI.dll")]
        public static extern void PrepareScene();
        [System.Runtime.InteropServices.DllImport("RenmasAPI.dll")]
        public static extern uint GetProperty(string category, string name);
        [System.Runtime.InteropServices.DllImport("RenmasAPI.dll")]
        public static extern int SetProperty(string category, string name, string value);
        public Renmas()
        {
            Init();
        }

        public int RunFile(string filename)
        {
            return RunScript(filename);  
        }
        public int WidthFrameBuffer()
        {
            return WidthImage();
        }
        public int HeightFrameBuffer()
        {
            return HeightImage();
        }
        public int PitchFrameBuffer() 
        {
            return PitchImage();
        }
        public uint AddrFrameBuffer()
        {
            return PtrImage();
        }
        public int RenderTile()
        {
            return Render();
        }
        public void PrepareForRendering()
        {
            PrepareScene();
        }
        public int IsRenderingFinished()
        {
            return IsFinished();
        }
        public string GetProp(string category, string name)
        {
            uint ptr_text = GetProperty(category, name);
            if (ptr_text == 0) return null;
            unsafe
            {
                string text = new System.String((sbyte*)ptr_text);
                return text;
            }
            
        }

        public int SetProp(string category, string name, string value)
        {
            return SetProperty(category, name, value);
        }

        ~Renmas()
        {
            ShutDown();
        }
    }
}
