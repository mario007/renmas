using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
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
    }
}
