using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PyWrapper
{
    public enum PropType
    {
        Light = 0,
        Material = 1,
        Camera = 2,
        Sampler = 3,
        ToneMapping = 4,
        Options = 5,
        Custom = 6
    }

    public struct PropDesc
    {
        public readonly string type;
        public readonly string name;

        public PropDesc(string type, string name)
        {
            this.type = type;
            this.name = name;
        }
    }

    public class RenmasProperty : INotifyPropertyChanged
    {
        public readonly string parent_id;
        public readonly PropType type;
        public readonly string name;
        public readonly string group;
        

        public RenmasProperty(string parent_id, string name, PropType type, string group)
        {
            this.parent_id = parent_id;
            this.type = type;
            this.name = name;
            this.group = group;
        }

        public string type_name()
        {
            switch (type)
            {
                case PropType.Light:
                    return "light";
                case PropType.Material:
                    return "material";
                case PropType.Camera:
                    return "camera";
                case PropType.Sampler:
                    return "sampler";
                case PropType.Options:
                    return "options";
                case PropType.ToneMapping:
                    return "tone";
                default:
                    return "undefined";
            }
            
        }

        public event PropertyChangedEventHandler PropertyChanged;
        protected void OnPropertyChanged(string property_name)
        {
            if (PropertyChanged != null)
            {
                PropertyChanged(this, new PropertyChangedEventArgs(property_name));
            }
        }

    }

    public class IntProperty : RenmasProperty
    {
        public IntProperty(string parent_id, string name, PropType type, string group) : base(parent_id, name, type, group)
        {
            
        }

        public int Value
        {
            get 
            {
                string args = type_name() + "," + name + "," + group;  
                return int.Parse(PyUtils.ExectueObjMethod(this.parent_id, "get_prop", args));
            }
            set
            {
                string args = type_name() + "," + name + "," + group + "," + value.ToString();
                PyUtils.ExectueObjMethod(this.parent_id, "set_prop", args);
                this.OnPropertyChanged("Value");
            }
        }

 
    }

    public class FloatProperty : RenmasProperty
    {
        public FloatProperty(string parent_id, string name, PropType type, string group)
            : base(parent_id, name, type, group)
        {

        }

        public float Value
        {
            get
            {
                string args = type_name() + "," + name + "," + group;
                return float.Parse(PyUtils.ExectueObjMethod(this.parent_id, "get_prop", args));
            }
            set
            {
                string args = type_name() + "," + name + "," + group + "," + value.ToString();
                PyUtils.ExectueObjMethod(this.parent_id, "set_prop", args);
                this.OnPropertyChanged("Value");
            }
        }


    }
}
