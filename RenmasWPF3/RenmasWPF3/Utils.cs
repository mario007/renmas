using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Controls;
using System.Windows.Media.Imaging;

namespace RenmasWPF3
{
    class Utils
    {
        public static void save_png(string filename, BitmapSource bmp)
        {
            PngBitmapEncoder encoder = new PngBitmapEncoder();
            BitmapFrame outputFrame = BitmapFrame.Create(bmp);
            encoder.Frames.Add(outputFrame);
            using (FileStream file = File.OpenWrite(filename))
            {
                encoder.Save(file);
            }
        }

        public static void save_jpg(string filename, int quality, BitmapSource bmp)
        {
            JpegBitmapEncoder encoder = new JpegBitmapEncoder();
            BitmapFrame outputFrame = BitmapFrame.Create(bmp);
            encoder.Frames.Add(outputFrame);
            encoder.QualityLevel = quality;
            using (FileStream file = File.OpenWrite(filename))
            {
                encoder.Save(file);
            }
        }

        public static UserControl build_editor(PyWrapper.RenmasProperty property)
        {
            Type t = property.GetType();
            if (t == typeof(PyWrapper.IntProperty))
            {
                IntEditor ed = new IntEditor();
                ed.set_target((PyWrapper.IntProperty)property);
                return ed;
            }
            else if (t == typeof(PyWrapper.FloatProperty))
            {
                FloatEditor ed = new FloatEditor();
                ed.set_target((PyWrapper.FloatProperty)property);
                return ed;
            }
            else
            {
                //TODO -- better message
                string msg = "Unknown type";
                throw new Exception(msg);
            }
        }
    }
}
