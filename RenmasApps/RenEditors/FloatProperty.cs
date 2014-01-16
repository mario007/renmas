using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace RenEditors
{
   
    public class FloatProperty : BaseProperty
    {
        public readonly string name = null;

        public FloatProperty(string name, string object_id, string key)
            : base(object_id, key)
        {
            this.name = name;
        }

        public float Value
        {
            get
            {
                return float.Parse(Base.ExectueObjMethod(this.object_id, "get_prop", this.key));
            }
            set
            {
                string args = this.key + ',' + value.ToString();
                Base.ExectueObjMethod(this.object_id, "set_prop", args);
                this.OnPropertyChanged("Value");
            }
        }

    }
}
