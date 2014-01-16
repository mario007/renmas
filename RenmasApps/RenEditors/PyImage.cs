using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Media;
using System.Windows.Media.Imaging;

namespace RenEditors
{

    public enum ImageType
    {
        RGBA = 0,
        BGRA = 1,
        PRGBA = 2
    }
   
    public class PyImage : PyObject
    {
        private ImageType _type;

        public PyImage(string id, ImageType type): base(id)
        {
            this._type = type;
        }

        public ImageType Type
        {
            get { return this._type; }
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
            get { return this.get_int("pitch"); }
        }

        public IntPtr Pixels
        {
            get { return this.get_pointer("pixels"); }
        }

        public PyBGRAImage convert_to_bgra()
        {
            string id = Base.ExecuteMethod("convert_to_bgra", this.ID);
            return new PyBGRAImage(id);
        }

        public static PyImage CreateImage(int width, int height, ImageType type)
        {
            string size = width.ToString() + "," + height.ToString();
            string id = "";
            switch (type)
            {
                case ImageType.RGBA:
                    id = Base.ExecuteMethod("create_image", "RGBA," + size);
                    break;
                case ImageType.BGRA:
                    id = Base.ExecuteMethod("create_image", "BGRA," + size);
                    break;
                case ImageType.PRGBA:
                    id = Base.ExecuteMethod("create_image", "PRGBA," + size);
                    break;
            }
            return new PyImage(id, type);
        }
    }

    public class PyBGRAImage : PyImage
    {
        public PyBGRAImage(string id)
            : base(id, ImageType.BGRA)
        {
        }

        public BitmapSource BufferSource
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
