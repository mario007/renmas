using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

using PyWrapper;

namespace RenmasWPF3
{
    /// <summary>
    /// Interaction logic for ImageViewer.xaml
    /// </summary>
    public partial class ImageViewer : UserControl
    {
        BitmapSource target = null;
        public ImageViewer()
        {
            InitializeComponent();
        }

        private void Image_save_menu(object sender, RoutedEventArgs e)
        {
            Microsoft.Win32.SaveFileDialog dlg = new Microsoft.Win32.SaveFileDialog();
            dlg.FileName = "picture"; // Default file name
            dlg.DefaultExt = ".png"; // Default file extension
            dlg.Filter = "RENMAS (.png)|*.png"; // Filter files by extension

            Nullable<bool> result = dlg.ShowDialog();
            if (result == true)
            {
                string filename = dlg.FileName;
                if (target != null)
                {
                    Utils.save_png(filename, target);
                }
            }
        }

        public void set_target(BitmapSource bitmap)
        {
            this.target = bitmap;
            refresh();
        }

        public void refresh()
        {
            this.img_control.Source = target;
        }
        public BitmapSource get_target()
        {
            return target;
        }
    }
}
