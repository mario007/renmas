using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Runtime.InteropServices;
using System.Windows.Media.Imaging;
using System.Windows.Media;

namespace RenmasWPF
{
    class Renmas
    {
        [System.Runtime.InteropServices.DllImport("RenmasAPI.dll")]
        public static extern int RunScript(string filename);
        [System.Runtime.InteropServices.DllImport("RenmasAPI.dll")]
        public static extern int Render();
        [System.Runtime.InteropServices.DllImport("RenmasAPI.dll")]
        public static extern int PrepareScene();
        [System.Runtime.InteropServices.DllImport("RenmasAPI.dll")]
        public static extern void ShutDown();
        [System.Runtime.InteropServices.DllImport("RenmasAPI.dll")]
        public static extern int Init();
        [System.Runtime.InteropServices.DllImport("RenmasAPI.dll")]
        public static extern int GetProps(string category, string name, ref IntPtr value);
        [System.Runtime.InteropServices.DllImport("RenmasAPI.dll")]
        public static extern int SetProps(string category, string name, string value);
        [System.Runtime.InteropServices.DllImport("RenmasAPI.dll")]
        public static extern void BltBackBuffer();

        public Renmas()
        {
            int ret = Init();//throw exception if error ocured!!!
            if (ret != 0) throw new Exception("Interface to renmas if failed to create.");
        }

        public string GetProp(string category, string name)
        {
            IntPtr ptr = IntPtr.Zero;
            int res = GetProps(category, name, ref ptr);
            string s = Marshal.PtrToStringUni(ptr);
            return s;
        }

        public int SetProp(string category, string name, string value)
        {
            return SetProps(category, name, value);
        }

        public int RunFile(string filename)
        {
            return RunScript(filename);  
        }
        
        public int RenderTile()
        {
            return Render();
        }
        public void Prepare()
        {
            PrepareScene();
        }

        public void BltBuffer()
        {
            BltBackBuffer();
        }
        public BitmapSource BufferSource()
        {
            string value = this.GetProp("frame_buffer", "dummy");
            string[] words = value.Split(',');
            int width = Convert.ToInt32(words[0]);
            int height = Convert.ToInt32(words[1]);
            int pitch = Convert.ToInt32(words[2]);
            uint addr = Convert.ToUInt32(words[3]); /// 64-Bit !!!!!!!!!!!
                     
            PixelFormat pixformat = PixelFormats.Bgra32;
            IntPtr ptr = new IntPtr(addr);

            BitmapSource image = BitmapSource.Create(width, height,
                96, 96, pixformat, null, ptr, height * pitch, pitch);
            return image;

        }

        ~Renmas()
        {
            ShutDown();
        }
    }
}
