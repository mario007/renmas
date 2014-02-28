using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Markup;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

namespace RenHdr
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        RenEditors.PyImage hdr_image = null;
        RenEditors.PyImage hdr_output = null;
        RenEditors.PyBGRAImage ldr_output = null;
        RenEditors.Tmo tmo = null;

        public MainWindow()
        {
            InitializeComponent();
            Thread.CurrentThread.CurrentCulture = new CultureInfo("en-US");

            using (FileStream fs = new FileStream("tema.xaml", FileMode.Open))
            {
                // Read in ResourceDictionary File
                ResourceDictionary dic =
                   (ResourceDictionary)XamlReader.Load(fs);
                // Clear any previous dictionaries loaded
                Resources.MergedDictionaries.Clear();
                // Add in newly loaded Resource Dictionary
                Resources.MergedDictionaries.Add(dic);
            }

            SolidColorBrush mySolidColorBrush = new SolidColorBrush();
            mySolidColorBrush.Color = Color.FromArgb(255, 47, 47, 47);
            this.Background = mySolidColorBrush;   


            this.tmo = RenEditors.Tmo.CreateTmo();

            RenEditors.TmoEditor tmo_ed = new RenEditors.TmoEditor();
            tmo_ed.set_target(this.tmo);

            StackPanel sp = new StackPanel();
            sp.Orientation = Orientation.Vertical;
            sp.Children.Add(tmo_ed);

            Grid.SetColumn(sp, 1);
            Grid.SetRow(sp, 1);
            this.mw_grid.Children.Add(sp);

        }

        private void MenuItem_Exit(object sender, RoutedEventArgs e)
        {
            this.Close();
        }

        private void MenuItem_ImportHdr(object sender, RoutedEventArgs e)
        {
            this.load_hdr_image();
        }

        public void load_hdr_image()
        {
            Microsoft.Win32.OpenFileDialog dlg = new Microsoft.Win32.OpenFileDialog();
            dlg.FileName = "hdr_image"; // Default file name
            dlg.DefaultExt = ".hdr"; // Default file extension
            dlg.Filter = "HDR (.hdr)|*.hdr|All Files (*.*)|*.*"; // Filter files by extension

            Nullable<bool> result = dlg.ShowDialog();
            if (result == true)
            {
                string filename = dlg.FileName;
                this.hdr_image = RenEditors.RenUtils.LoadHdrImage(filename);
                this.hdr_output = RenEditors.PyImage.CreateImage(hdr_image.Width, hdr_image.Height, RenEditors.ImageType.PRGBA);

                this.txt_filename.Text = dlg.FileName;
                this.txt_img_width.Text = this.hdr_image.Width.ToString();
                this.txt_img_height.Text = this.hdr_image.Height.ToString();

                this.tone_map();
            }
        }

        public void tone_map()
        {
            if (this.hdr_image == null)
                return;
            DateTime start = DateTime.Now;
            this.tmo.tmo(this.hdr_image, this.hdr_output);
            this.ldr_output = this.hdr_output.convert_to_bgra();
            var flippedImage = new TransformedBitmap(this.ldr_output.BufferSource, new ScaleTransform(1, -1));
            this.img_output.Source = flippedImage;
            //this.img_output.Source = this.ldr_output.BufferSource;
            TimeSpan elapsed = DateTime.Now - start;
            this.txt_elapsed_time.Text = elapsed.Milliseconds.ToString();
        }

        private void MenuItem_Save(object sender, RoutedEventArgs e)
        {
            Microsoft.Win32.SaveFileDialog dlg = new Microsoft.Win32.SaveFileDialog();
            dlg.FileName = "unknown"; // Default file name
            dlg.DefaultExt = ".jpeg"; // Default file extension
            dlg.Filter = "JPEG (.jpeg)|*.jpeg"; // Filter files by extension
            Nullable<bool> result = dlg.ShowDialog();
            if (result == true)
            {
                if (this.hdr_output == null)
                return;
                this.tmo.save_image(dlg.FileName, this.hdr_output);
            }
        }

        private void ToneMap_OnClick(object sender, RoutedEventArgs e)
        {
            this.tone_map();
        }

        private void ImportHdr_OnClick(object sender, RoutedEventArgs e)
        {
            this.load_hdr_image();
        }
    }
}
