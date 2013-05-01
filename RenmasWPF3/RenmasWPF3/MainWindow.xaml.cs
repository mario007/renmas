using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Security.Permissions;
using System.Text;
using System.Threading;
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
using System.Windows.Threading;

namespace RenmasWPF3
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        PyWrapper.Renmas renmas;
        ImageViewer img_viewer;
        bool stop_rendering = false;

        public MainWindow()
        {
            InitializeComponent();
            Thread.CurrentThread.CurrentCulture = new CultureInfo("en-US");
            renmas = PyWrapper.Renmas.create();
            img_viewer = new ImageViewer();

            Grid.SetColumn(img_viewer, 0);
            Grid.SetRow(img_viewer, 1);
            this.mw_grid.Children.Add(img_viewer);

            //Options op = new Options(renmas);
            ToneMappingEditor op = new ToneMappingEditor(renmas);
            Grid.SetColumn(op, 1);
            Grid.SetRow(op, 1);
            this.mw_grid.Children.Add(op);
        }

        private void MenuItem_Exit(object sender, RoutedEventArgs e)
        {
            this.Close();
        }

        private void MenuItem_save_project(object sender, RoutedEventArgs e)
        {

        }

        private void MenuItem_open_project(object sender, RoutedEventArgs e)
        {
            Microsoft.Win32.OpenFileDialog dlg = new Microsoft.Win32.OpenFileDialog();
            dlg.FileName = "scene"; // Default file name
            dlg.DefaultExt = ".proj"; // Default file extension
            dlg.Filter = "RENMAS (.proj)|*.proj"; // Filter files by extension

            Nullable<bool> result = dlg.ShowDialog();
            if (result == true)
            {
                string filename = dlg.FileName;
                this.renmas.open_project(filename);
            }
        }

        private void MenuItem_import(object sender, RoutedEventArgs e)
        {
            Microsoft.Win32.OpenFileDialog dlg = new Microsoft.Win32.OpenFileDialog();
            dlg.FileName = "project"; // Default file name
            dlg.DefaultExt = ".txt"; // Default file extension
            dlg.Filter = "RENMAS (.txt)|*.txt"; // Filter files by extension

            Nullable<bool> result = dlg.ShowDialog();
            if (result == true)
            {
                string filename = dlg.FileName;
                this.renmas.import_scene(filename);
            }
        }

        private void MenuItem_save_as_project(object sender, RoutedEventArgs e)
        {
            Microsoft.Win32.SaveFileDialog dlg = new Microsoft.Win32.SaveFileDialog();
            dlg.FileName = "project"; // Default file name
            dlg.DefaultExt = ".proj"; // Default file extension
            dlg.Filter = "RENMAS (.proj)|*.proj"; // Filter files by extension

            Nullable<bool> result = dlg.ShowDialog();
            if (result == true)
            {
                string filename = dlg.FileName;
                this.renmas.save_project(filename);
            }
        }

        private void MenuItem_new_project(object sender, RoutedEventArgs e)
        {
            this.build_editor(PyWrapper.PropType.Options);
        }

        private void MenuItem_start_rendering(object sender, RoutedEventArgs e)
        {
            this.stop_rendering = false;
            bool finished = false;

            while (true)
            {
                finished = this.renmas.render();
                BitmapSource bs = this.renmas.output_image();
                this.img_viewer.set_target(bs);

                if (finished) break;
                if (this.stop_rendering) break;
                
                this.DoEvents();

            }
        }

        private void MenuItem_stop_rendering(object sender, RoutedEventArgs e)
        {
            this.stop_rendering = true;
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

        public void build_editor(PyWrapper.PropType type)
        {
            List<PyWrapper.PropDesc> descs = this.renmas.get_props_descs(type);

            // 1. renmas.get_props(Type, active_light or active_material)
            // 2. 

            //active light  -- group
            //active material  -- group

            // list_of_props_descriptors = this.renmas.get_props(prop_type, group)
            // prop_desc {prop_type, name}

            // IntProperty(this.renmas.ID, name, prop_type, group)
        }
    }
}
