using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Media;
using System.Windows.Media.Imaging;

namespace PyWrapper
{
    public class Renmas : PyObject
    {
        public Renmas(string id) : base(id)
        {
            
        }

        public static Renmas create()
        {
            string id = PyUtils.ExecuteMethod("create_renderer", "");
            return new Renmas(id);
        }

        public void import_scene(string filename)
        {
            // TODO check if file exists or null raise exception
            PyUtils.ExectueObjMethod(this.ID, "parse_scene_file",  filename);
        }

        public void open_project(string filename)
        {
            // TODO check if file exists or null raise exception
            PyUtils.ExectueObjMethod(this.ID, "open_project", filename);
        }

        public void save_project(string filename)
        {
            // TODO check if file exists or null raise exception
            PyUtils.ExectueObjMethod(this.ID, "save_project", filename);
        }

        public bool render()
        {
            string ret = PyUtils.ExectueObjMethod(this.ID, "render", "");
            if (ret == "True")
            {
                return true;
            }
            else if (ret == "False")
            {
                return false;
            }
            else
            {
                throw new Exception("True or False is expeted to be returned from render function!");
            }
        }

        public BitmapSource output_image()
        {
            // NOTE bgra format is expected
            // "width, height, pixels, pitch"
            string ret = PyUtils.ExectueObjMethod(this.ID, "output_image", "");
            string[] tokens = ret.Split(',');
            int width = int.Parse(tokens[0]);
            int height = int.Parse(tokens[1]);
            int pitch = int.Parse(tokens[3]);
            long adr = long.Parse(tokens[2]);
            IntPtr pixels = new IntPtr(adr);
            
            PixelFormat pixformat = PixelFormats.Bgra32;
            BitmapSource image = BitmapSource.Create(width, height, 96, 96, pixformat,
                            null, pixels, height * pitch, pitch);
            return image;
        }

    }
}
