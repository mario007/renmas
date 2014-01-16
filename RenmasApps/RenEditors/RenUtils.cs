using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace RenEditors
{
    public static class RenUtils
    {
        public static PyImage LoadHdrImage(string filename)
        {
            string id = Base.ExecuteMethod("load_hdr_image", filename);
            return new PyImage(id, ImageType.PRGBA);
        }
    }

}
