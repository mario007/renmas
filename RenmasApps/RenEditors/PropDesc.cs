using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace RenEditors
{
    public struct PropDesc
    {
        public readonly string name;
        public readonly string type;

        public PropDesc(string name, string type)
        {
            this.name = name;
            this.type = type;
        }
    }
}
