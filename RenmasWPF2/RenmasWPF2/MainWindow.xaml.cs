using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;
using System.Security.Permissions;
using System.Windows.Threading;
using System.Threading;
using System.Globalization;

namespace RenmasWPF2
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        Renmas renmas;
        bool rendering = false;
        Camera_editor cam_editor;
        Options_editor op_editor;
        LightsEditor lights_editor;
        Shapes_editor shapes_editor;
        public MainWindow()
        {
            InitializeComponent();
            Thread.CurrentThread.CurrentCulture = new CultureInfo("en-US");
            renmas = new Renmas();
            cam_editor = new Camera_editor(renmas.camera);
            op_editor = new Options_editor(renmas.options);
            lights_editor = new LightsEditor(renmas.lights);
            shapes_editor = new Shapes_editor(renmas.shapes);
            //this.main_grid.Children.Add(cam_editor);
            //this.output_image.SetValue(Grid.ColumnProperty, 1);

            // Expander --
            StackPanel sp = new StackPanel();
            
            Grid.SetColumn(sp, 1);
            Grid.SetRow(sp, 1);
            sp.Children.Add(cam_editor);
            sp.Children.Add(op_editor);
            sp.Children.Add(lights_editor);
            sp.Children.Add(shapes_editor);
            this.main_grid.Children.Add(sp);

            SolidColorBrush mySolidColorBrush = new SolidColorBrush();
            mySolidColorBrush.Color = Color.FromArgb(255, 47, 47, 47);
            this.Background = mySolidColorBrush;
            
            

        }

        private void MenuItem_Exit(object sender, RoutedEventArgs e)
        {
            // TODO -- Maybe ask user to save project
            this.Close();
        }

        private void MenuItem_ExportImage(object sender, RoutedEventArgs e)
        {
            Microsoft.Win32.SaveFileDialog dlg = new Microsoft.Win32.SaveFileDialog();
            dlg.FileName = "picture"; // Default file name
            dlg.DefaultExt = ".png"; // Default file extension
            dlg.Filter = "PNG (.png)|*.png"; // Filter files by extension

            Nullable<bool> result = dlg.ShowDialog();
            if (result == true)
            {
                string filename = dlg.FileName;
                //Utils.save_jpg(filename, 100, this.renmas.FrameSource());
                Utils.save_png(filename, this.renmas.BufferSource());
            }
        }

        private void MenuItem_Stop(object sender, RoutedEventArgs e)
        {
            this.rendering = false;
        }

        private void MenuItem_Render(object sender, RoutedEventArgs e)
        {
            //refresh GUI --- Lost Focus Problem -- TODO
            this.txt_output_window.Focus(); // -- intersting solution for focus problem
            this.renmas.Prepare();
            this.txt_output_window.Text = this.renmas.Log();
            this.rendering = true;
            DateTime start = DateTime.Now;
            // TODO -- get resolution from data model not from buffer source
            BitmapSource bmp = this.renmas.BufferSource();
            this.output_image.Width = bmp.Width;
            this.output_image.Height = bmp.Height;

            while (true)
            {
                int res = renmas.RenderTile();
                this.renmas.BltBuffer();
                this.output_image.Source = this.renmas.BufferSource();
                if (res == 0) break;
                if (!rendering) break;
                this.DoEvents();
            }
            this.rendering = false;
            DateTime end = DateTime.Now;
            long interval = end.Ticks - start.Ticks;
            TimeSpan tm = new TimeSpan(interval);
            this.txt_output_window.Text += "Rendering took " + tm.TotalMinutes.ToString() + " minutes.";
        }

        private void MenuItem_RunScript(object sender, RoutedEventArgs e)
        {
            Microsoft.Win32.OpenFileDialog dlg = new Microsoft.Win32.OpenFileDialog();
            dlg.FileName = "Script"; // Default file name
            dlg.DefaultExt = ".py"; // Default file extension
            dlg.Filter = "Python py (.py)|*.py"; // Filter files by extension
            Nullable<bool> result = dlg.ShowDialog();
            if (result == true)
            {
                string filename = dlg.FileName;
                // TODO -- disable GUI and report user that scirpt is running
                int result2 = this.renmas.RunFile(filename);
                if (result2 == -1)
                {
                    MessageBox.Show("Script not finish sucesfully.");
                    return;
                }
                this.renmas.Refresh();
                this.txt_output_window.Text = this.renmas.Log();
            }
        }

        [SecurityPermissionAttribute(SecurityAction.Demand, Flags = SecurityPermissionFlag.UnmanagedCode)]
        public void DoEvents()
        {
            DispatcherFrame frame = new DispatcherFrame();
            Dispatcher.CurrentDispatcher.BeginInvoke(DispatcherPriority.Background,
                new DispatcherOperationCallback(ExitFrame), frame);
            Dispatcher.PushFrame(frame);
        }

        public object ExitFrame(object f)
        {
            ((DispatcherFrame)f).Continue = false;

            return null;
        }
    }
}
