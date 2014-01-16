using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace RenEditors
{
    public class IntProperty : BaseProperty
    {
        public readonly string name = null;

        public IntProperty(string name, string object_id, string key): base(object_id, key)
        {
            this.name = name;
        }

        public int Value
        {
            get
            {
                return int.Parse(Base.ExectueObjMethod(this.object_id, "get_prop", this.key));
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
