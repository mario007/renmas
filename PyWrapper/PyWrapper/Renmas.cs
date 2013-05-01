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
        List<RenmasProperty> option_props;

        public Renmas(string id) : base(id)
        {
            option_props = new List<RenmasProperty>();
            this.create_options_props();
        }

        public List<RenmasProperty> OptionsProps
        {
            get { return this.option_props;  }
        }

        private void create_options_props()
        {
            this.option_props.Clear();
            List<PyWrapper.PropDesc> descs = this.get_props_descs(PropType.Options);
            foreach (PyWrapper.PropDesc desc in descs)
            {
                RenmasProperty prop = this.create_property(desc, PropType.Options);
                this.option_props.Add(prop);
            }

        }

        public List<RenmasProperty> ToneProps
        {
            get
            {
                List<RenmasProperty> tone_props = new List<RenmasProperty>();
                List<PyWrapper.PropDesc> descs = this.get_props_descs(PropType.ToneMapping);
                foreach (PyWrapper.PropDesc desc in descs)
                {
                    RenmasProperty prop = this.create_property(desc, PropType.ToneMapping);
                    tone_props.Add(prop);
                }
                return tone_props;
            }
        }

        private RenmasProperty create_property(PropDesc desc, PropType type)
        {
            if (desc.type == "int")
            {
                return new PyWrapper.IntProperty(this.ID, desc.name, type, "");
            }
            else if (desc.type == "float")
            {
                return new PyWrapper.FloatProperty(this.ID, desc.name, type, "");
            }
            else
            {
                throw new Exception("Unknown property type");
            }
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

        public List<PropDesc> get_props_descs(PropType prop_type, string group="")
        {
            List<PropDesc> descs = new List<PropDesc>();
            string result = "";
            string args = "";
            switch (prop_type)
            {
                case PropType.Options:
                    args = "options," + group;
                    result = PyUtils.ExectueObjMethod(this.ID, "get_props_descs", args);
                    break;
                case PropType.ToneMapping:
                    args = "tone," + group;
                    result = PyUtils.ExectueObjMethod(this.ID, "get_props_descs", args);
                    break;
                default:
                    result = "";
                    break;
            }

            string[] words = result.Split(',');
            for (int i = 0; i < words.Length; i = i + 2)
            {
                descs.Add(new PropDesc(words[i], words[i + 1]));
            }
            return descs;
        }
    }
}
