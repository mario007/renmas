using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace RenEditors
{
    public class PyObject
    {
        private string _id;

        public PyObject(string id)
        {
            this._id = id;
        }

        public string ID
        {
            get { return this._id; }
        }
        protected int get_int(string name)
        {
            return int.Parse(Base.GetProp(this._id, name, "int"));
        }

        protected IntPtr get_pointer(string name)
        {
            long adr = long.Parse(Base.GetProp(this._id, name, "int"));
            return new IntPtr(adr);
        }

        ~PyObject()
        {
            Base.Free(this._id);
        }
    }
}
