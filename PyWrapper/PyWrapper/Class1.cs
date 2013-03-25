using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Media;
using System.Windows.Media.Imaging;

namespace PyWrapper
{
    public enum ImageType
    {
        RGBA = 0,
        BGRA = 1,
        PRGBA = 2
    }
    
    public static class PyUtils
    {
        [System.Runtime.InteropServices.DllImport("PyAPI.dll")]
        private static extern int Init();

        [System.Runtime.InteropServices.DllImport("PyAPI.dll")]
        private static extern int ExecuteFunction(string name, string args, ref IntPtr value);

        [System.Runtime.InteropServices.DllImport("PyAPI.dll")]
        private static extern int ExecuteObjFunction(string id_obj, string name, string args, ref IntPtr value);

        [System.Runtime.InteropServices.DllImport("PyAPI.dll")]
        private static extern int GetProperty(string id, string name, string type, ref IntPtr value);

        [System.Runtime.InteropServices.DllImport("PyAPI.dll")]
        private static extern int FreeObject(string id);

        static PyUtils()
        {
            int ret = Init();
            if (ret != 0) 
                throw new Exception("Python virtual machine cannot be initialized.");
        }

        public static string ExectueObjMethod(string id_obj, string name, string args)
        {
            // TODO Add support to extract StackTrace and put that message for exception
            IntPtr ptr = IntPtr.Zero;
            int ret = ExecuteObjFunction(id_obj, name, args, ref ptr);
            if (ret == -1)
                throw new Exception("Cannot exectue method, some exception ocured!");
            string s = Marshal.PtrToStringUni(ptr);
            return s;
        }
        public static string ExecuteMethod(string name, string args)
        {
            // TODO Add support to extract StackTrace and put that message for exception
            IntPtr ptr = IntPtr.Zero;
            int ret = ExecuteFunction(name, args, ref ptr);
            if (ret == -1)
                throw new Exception("Cannot exectue method, some exception ocured!");
            string s = Marshal.PtrToStringUni(ptr);
            return s;
        }

        public static string GetProp(string id, string name, string type)
        {
            // TODO Add support to extract StackTrace and put that message for exception
            IntPtr ptr = IntPtr.Zero;
            int ret = GetProperty(id, name, type, ref ptr);
            if (ret == -1)
                throw new Exception("Cannot get property, some exception ocured!");
            string s = Marshal.PtrToStringUni(ptr);
            return s;
        }

        public static void Free(string id)
        {
            int ret = FreeObject(id);
            if (ret == -1)
                throw new Exception("Cannot free object, object doesn't exist");
        }

        public static PyImage CreateImage(int width , int height, ImageType type)
        {
            string size = width.ToString() + "," + height.ToString();
            string id = "";
            switch (type)
            {
                case ImageType.RGBA:
                    id = PyUtils.ExecuteMethod("create_image", "RGBA," + size);
                    break;
                case ImageType.BGRA:
                    id = PyUtils.ExecuteMethod("create_image", "BGRA," + size);
                    break;
                case ImageType.PRGBA:
                    id = PyUtils.ExecuteMethod("create_image", "PRGBA," + size);
                    break;
            }
            return new PyImage(id, type);
        }
    }

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
            return int.Parse(PyUtils.GetProp(this._id, name, "int"));
        }

        protected IntPtr get_pointer(string name)
        {
            long adr = long.Parse(PyUtils.GetProp(this._id, name, "int"));
            return new IntPtr(adr);
        }
        ~PyObject()
        {
            PyUtils.Free(this._id);
        }
    }

    public class PyImage : PyObject
    {
        private ImageType _type;

        public PyImage(string id, ImageType type) : base(id)
        {
            this._type = type;
        }

        public int Width
        {
            get { return this.get_int("width"); }
        }

        public int Height
        {
            get { return this.get_int("height"); }
        }

        public int Pitch
        {
            get { return this.get_int("pitch");  }
        }

        public IntPtr Pixels
        {
            get { return this.get_pointer("pixels");  }
        }
        public ImageType Type
        {
            get { return this._type;  }
        }

        public PyBGRAImage convert_to_bgra()
        {
            string id = PyUtils.ExecuteMethod("conv_to_bgra", this.ID);
            return new PyBGRAImage(id);
        }
    }

    public class PyBGRAImage : PyImage
    {
        public PyBGRAImage(string id)
            : base(id, ImageType.BGRA)
        {
        }

        public BitmapSource BufferSouce
        {
            get
            {
                PixelFormat pixformat = PixelFormats.Bgra32;
                BitmapSource image = BitmapSource.Create(this.Width, this.Height, 96, 96, pixformat,
                            null, this.Pixels, this.Height * this.Pitch, this.Pitch);
                return image;
            }
        }
    }
}
