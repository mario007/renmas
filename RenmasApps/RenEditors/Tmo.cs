using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace RenEditors
{
    
    public class Tmo : PyObject
    {
        public Tmo(string id): base(id)
        {
            
        }

        public static Tmo CreateTmo()
        {
            string id = Base.ExecuteMethod("create_tmo", "");
            return new Tmo(id);
        }

        public void tmo(PyImage input, PyImage output)
        {
            string args = input.ID + ',' + output.ID;
            Base.ExectueObjMethod(this.ID, "tmo", args);
            
        }

        public List<BaseProperty> get_props()
        {
            List<BaseProperty> props = new List<BaseProperty>();

            string text = Base.ExectueObjMethod(this.ID, "get_public_props", "");
            if (text == "")
                return props;

            string[] words = text.Split(',');

            for (int i = 0; i < words.Length; i = i + 2)
            {
                if (words[i + 1] == "float")
                {
                    props.Add(new FloatProperty(words[i], this.ID, words[i]));
                }
            }
            return props;
        }

        public void save_image(string filename, PyImage image)
        {
            string args = filename + ',' + image.ID;
            Base.ExectueObjMethod(this.ID, "save_image", args);
        }

        public string shader_code()
        {
            string code = Base.ExectueObjMethod(this.ID, "shader_code", "");
            return code;
        }

        public string assembly_code()
        {
            string code = Base.ExectueObjMethod(this.ID, "assembly_code", "");
            return code;
        }
    }
}
