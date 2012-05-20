using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Runtime.InteropServices;
using System.Windows.Media.Imaging;
using System.Windows.Media;
using System.Windows.Controls;

namespace RenmasWPF2
{
    public class Renmas
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
        public static extern void ToneMapping();

        public Camera camera;
        public Options options;
        public Lights lights;
        public Shapes shapes;
        public ToneMappingOperators tone_mapping_operators;
        public Materials materials;
        public Image output_image;
        public Renmas(Image output_image)
        {
            int ret = Init();//throw exception if error ocured!!!
            if (ret != 0) throw new Exception("Interface to renmas if failed to create.");
            this.camera = new Camera(this);
            this.options = new Options(this);
            this.lights = new Lights(this);
            this.shapes = new Shapes(this);
            this.output_image = output_image;
            this.tone_mapping_operators = new ToneMappingOperators(this);
            this.materials = new Materials(this);

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

        public void Refresh()
        {
            this.camera.Refresh();
            this.options.Refresh();
            this.lights.Refresh();
            this.shapes.Refresh();
            this.tone_mapping_operators.Refresh();
            this.materials.Refresh();
        }
        public int RenderTile()
        {
            int ret = Render();
            this.ToneMap();
            this.RefreshImage();
            return ret;
        }

        public void RefreshImage()
        {
            this.output_image.Source = this.BufferSource();
        }

        public void Prepare()
        {
            PrepareScene();
        }

        public void ToneMap()
        {
            ToneMapping();
        }

        public string SaveProject(string path)
        {
            SetProp("misc", "project_save", path);
            return this.GetProp("misc", "log");
        }

        public string LoadProject(string path)
        {
            SetProp("misc", "project_load", path);
            this.Refresh();
            return this.GetProp("misc", "log");
        }

        public string Log()
        {
            return this.GetProp("misc", "log");
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
