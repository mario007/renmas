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
using System.IO;
using System.Windows.Markup;

namespace RenmasWPF
{
    /// <summary>
    /// Interaction logic for Window1.xaml
    /// </summary>
    public partial class Window1 : Window
    {
        Renmas renmas;
        bool rendering = false;

        // -------------GUI MenuItems --------------------------
        private MenuItem file_exit, file_export_image;
        private MenuItem tools_run_script, tools_render, tools_stop;

        // ------------- GUI TextBoxes ------------------------
        private TextBox camera_eye_x, camera_eye_y, camera_eye_z;
        private TextBox camera_lookat_x, camera_lookat_y, camera_lookat_z;
        private TextBox camera_distance;
       
        // -------------- GUI Control for represent FrameBuffer
        private Image frame_buffer_control;

        // -------------- Logger
        private TextBox log_output;

        // ------------ Global Settings
        private TextBox resolution_x, resolution_y, pixel_size, samples_per_pixel;
        private ComboBox cb_algorithm;
        
        public Window1()
        {
            InitializeComponent();
            try
            {
                renmas = new Renmas();
                LoadGUI();
            }
            catch (Exception e)
            {
                MessageBox.Show(e.Message);
            }
        }

        private void LoadGUI()
        { 
            string filename = this.GuiPath();
            if (filename == "") return;
            try {
                FileStream s = new FileStream(filename, FileMode.Open);
                DependencyObject rootElement = (DependencyObject)XamlReader.Load(s);
                this.Content = rootElement;
                this.Width = 800;
                this.Height = 600;
                  
                SolidColorBrush mySolidColorBrush = new SolidColorBrush();
                mySolidColorBrush.Color = Color.FromArgb(255, 47, 47, 47);
                this.Background = mySolidColorBrush;
                this.BindGui(rootElement);
            }
            catch (Exception e) {
                throw new Exception(e.Message);
            }
        }
        private string GuiPath()
        {
            if (File.Exists(".\\GUI\\MainWindow.xaml")) {
                return ".\\GUI\\MainWindow.xaml";
            }
            else {
                Microsoft.Win32.OpenFileDialog dlg = new Microsoft.Win32.OpenFileDialog();
                dlg.FileName = "Document"; // Default file name
                dlg.DefaultExt = ".xaml"; // Default file extension
                dlg.Filter = "GUI XAML (.xaml)|*.xaml"; // Filter files by extension  
                Nullable<bool> result = dlg.ShowDialog();
                if (result == true) {
                    return dlg.FileName;
                }
                else {
                    return "";
                }
            }
        }
        private void BindGui(DependencyObject el)
        {
            this.BindCameraGUI(el);
            this.get_camera();
            this.BindMenuGUI(el);
            
            this.frame_buffer_control = (Image)LogicalTreeHelper.FindLogicalNode(el, "render_window");
            this.log_output = (TextBox)LogicalTreeHelper.FindLogicalNode(el, "log_output");
            this.BindGlobalSettingsGUI(el);
            this.get_global_settings();
        }
        private void camera_enter_pressed(object sender, KeyEventArgs e)
        {
            if (e.Key == Key.Return) this.update_camera();   
        }
        private void camera_lost_focus(object sender, RoutedEventArgs e)
        {
            this.update_camera();
        }

        private void BindCameraGUI(DependencyObject element)
        {
            this.camera_eye_x = (TextBox)LogicalTreeHelper.FindLogicalNode(element, "camera_eye_x");
            this.camera_eye_y = (TextBox)LogicalTreeHelper.FindLogicalNode(element, "camera_eye_y");
            this.camera_eye_z = (TextBox)LogicalTreeHelper.FindLogicalNode(element, "camera_eye_z");
            this.camera_lookat_x = (TextBox)LogicalTreeHelper.FindLogicalNode(element, "camera_lookat_x");
            this.camera_lookat_y = (TextBox)LogicalTreeHelper.FindLogicalNode(element, "camera_lookat_y");
            this.camera_lookat_z = (TextBox)LogicalTreeHelper.FindLogicalNode(element, "camera_lookat_z");
            this.camera_distance = (TextBox)LogicalTreeHelper.FindLogicalNode(element, "camera_distance");

            this.camera_eye_x.LostFocus += camera_lost_focus;
            this.camera_eye_y.LostFocus += camera_lost_focus;
            this.camera_eye_z.LostFocus += camera_lost_focus;
            this.camera_lookat_x.LostFocus += camera_lost_focus;
            this.camera_lookat_y.LostFocus += camera_lost_focus;
            this.camera_lookat_z.LostFocus += camera_lost_focus;
            this.camera_distance.LostFocus += camera_lost_focus;

            this.camera_eye_x.KeyDown += camera_enter_pressed;
            this.camera_eye_y.KeyDown += camera_enter_pressed;
            this.camera_eye_z.KeyDown += camera_enter_pressed;
            this.camera_lookat_x.KeyDown += camera_enter_pressed;
            this.camera_lookat_y.KeyDown += camera_enter_pressed;
            this.camera_lookat_z.KeyDown += camera_enter_pressed;
            this.camera_distance.KeyDown += camera_enter_pressed;
        }

        private void BindGlobalSettingsGUI(DependencyObject element)
        {
            this.resolution_x = (TextBox)LogicalTreeHelper.FindLogicalNode(element, "output_resolution_x");
            this.resolution_y = (TextBox)LogicalTreeHelper.FindLogicalNode(element, "output_resolution_y");
            this.pixel_size = (TextBox)LogicalTreeHelper.FindLogicalNode(element, "output_pixelsize");
            this.samples_per_pixel = (TextBox)LogicalTreeHelper.FindLogicalNode(element, "output_samples");

            this.resolution_x.LostFocus += global_settings_lost_focus;
            this.resolution_y.LostFocus += global_settings_lost_focus;
            this.samples_per_pixel.LostFocus += global_settings_lost_focus;
            this.pixel_size.LostFocus += global_settings_lost_focus;

            this.resolution_x.KeyDown += global_settings_enter_pressed;
            this.resolution_y.KeyDown += global_settings_enter_pressed;
            this.samples_per_pixel.KeyDown += global_settings_enter_pressed;
            this.pixel_size.KeyDown += global_settings_enter_pressed;

            this.cb_algorithm = (ComboBox)LogicalTreeHelper.FindLogicalNode(element, "cb_algorithm");
        }

        private void global_settings_enter_pressed(object sender, KeyEventArgs e)
        {
            if (e.Key == Key.Return) this.update_global_settings();
        }

        private void global_settings_lost_focus(object sender, RoutedEventArgs e)
        {
            this.update_global_settings();
        }

        private void BindMenuGUI(DependencyObject element)
        {
            this.file_exit = (MenuItem)LogicalTreeHelper.FindLogicalNode(element, "file_exit");
            if (this.file_exit != null) this.file_exit.Click += menu_file_exit;
            this.tools_run_script = (MenuItem)LogicalTreeHelper.FindLogicalNode(element, "tools_run_script");
            if (this.tools_run_script != null) this.tools_run_script.Click += menu_run_script;
            this.tools_render = (MenuItem)LogicalTreeHelper.FindLogicalNode(element, "tools_render");
            if (this.tools_render != null) this.tools_render.Click += menu_tools_render;
            this.tools_stop = (MenuItem)LogicalTreeHelper.FindLogicalNode(element, "tools_stop");
            if (this.tools_stop != null) this.tools_stop.Click += menu_tools_stop;
            this.file_export_image = (MenuItem)LogicalTreeHelper.FindLogicalNode(element, "file_save_image");
            if (this.file_export_image != null) this.file_export_image.Click += menu_file_save_image;
        }

        private void logger(string text)
        {
            if (this.log_output != null) this.log_output.Text = text + this.log_output.Text;
        }
        private void menu_file_exit(object sender, RoutedEventArgs e)
        {
            this.Close();
        }

        private void save_jpg(string filename, int quality, BitmapSource bmp)
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
        private void save_png(string filename, BitmapSource bmp)
        {
            PngBitmapEncoder encoder = new PngBitmapEncoder();
            BitmapFrame outputFrame = BitmapFrame.Create(bmp);
            encoder.Frames.Add(outputFrame);
            using (FileStream file = File.OpenWrite(filename))
            {
                encoder.Save(file);
            }
        }
        private void menu_file_save_image(object sender, RoutedEventArgs e)
        {
            Microsoft.Win32.SaveFileDialog dlg = new Microsoft.Win32.SaveFileDialog();
            dlg.FileName = "picture"; // Default file name
            dlg.DefaultExt = ".png"; // Default file extension
            dlg.Filter = "PNG (.png)|*.png"; // Filter files by extension

            Nullable<bool> result = dlg.ShowDialog();
            if (result == true)
            {
                string filename = dlg.FileName;
                //this.save_jpg(filename, 100, this.FrameSource());
                this.save_png(filename, this.renmas.BufferSource());
            }
        }
        private void select_algorithm_evt(object sender, RoutedEventArgs e)
        {
            string text = (string)this.cb_algorithm.SelectedItem;
            this.renmas.SetProp("global_settings", "algorithm", text);
        }
        private void menu_run_script(object sender, RoutedEventArgs e)
        {
            Microsoft.Win32.OpenFileDialog dlg = new Microsoft.Win32.OpenFileDialog();
            dlg.FileName = "Script"; // Default file name
            dlg.DefaultExt = ".py"; // Default file extension
            dlg.Filter = "Python py (.py)|*.py"; // Filter files by extension
            Nullable<bool> result = dlg.ShowDialog();
            if (result == true)
            {
                string filename = dlg.FileName;
                int result2 = this.renmas.RunFile(filename);
                if (result2 == -1)
                {
                    // alert user about failure
                    return;
                }
                //this.update_camera();
                //this.update_global_settings();
            }
            
        }
        
        private void menu_tools_render(object sender, RoutedEventArgs e)
        {
            this.renmas.Prepare();
            //string text = renmas.GetProp("log", "");
            //this.logger(text);
            this.rendering = true;
            DateTime start = DateTime.Now;
            while (true)
            {
                int res = renmas.RenderTile();
                this.renmas.BltBuffer();
                this.frame_buffer_control.Source = this.renmas.BufferSource();
                if (res == 0) break;
                if (!rendering) break;
                this.DoEvents();
            }
            this.rendering = false;
            DateTime end = DateTime.Now;
            long interval = end.Ticks - start.Ticks;
            TimeSpan tm = new TimeSpan(interval);
        }
        private void menu_tools_stop(object sender, RoutedEventArgs e)
        {
            this.rendering = false;
        }

        private void update_global_settings()
        {
            string value;
            value = this.resolution_x.Text + "," + this.resolution_y.Text;
            this.renmas.SetProp("misc", "resolution", value);
            this.renmas.SetProp("misc", "spp", this.samples_per_pixel.Text);
            this.renmas.SetProp("misc", "pixel_size", this.pixel_size.Text);
            this.get_global_settings();
        }
        private void get_global_settings()
        {
            string value = this.renmas.GetProp("misc", "resolution");
            string[] words = value.Split(',');
            this.resolution_x.Text = words[0];
            this.resolution_y.Text = words[1];
            this.samples_per_pixel.Text = this.renmas.GetProp("misc", "spp");
            this.pixel_size.Text = this.renmas.GetProp("misc", "pixel_size");
        }
        private void get_camera()
        {
            string value = this.renmas.GetProp("camera", "eye");
            string[] words = value.Split(',');
            this.camera_eye_x.Text = words[0];
            this.camera_eye_y.Text = words[1];
            this.camera_eye_z.Text = words[2];

            value = this.renmas.GetProp("camera", "lookat");
            words = value.Split(',');
            this.camera_lookat_x.Text = words[0];
            this.camera_lookat_y.Text = words[1];
            this.camera_lookat_z.Text = words[2];
            value = renmas.GetProp("camera", "distance");
            this.camera_distance.Text = value;  
        }
        private void update_camera()
        {
            string value;
            value = this.camera_eye_x.Text + "," + this.camera_eye_y.Text + "," + this.camera_eye_z.Text;
            this.renmas.SetProp("camera", "eye", value);
            value = this.camera_lookat_x.Text + "," + this.camera_lookat_y.Text + "," + this.camera_lookat_z.Text;
            this.renmas.SetProp("camera", "lookat", value);
            value = this.camera_distance.Text;
            this.renmas.SetProp("camera", "distance", value);
            this.get_camera();
        }

        private void update_global_settings_old()
        {
            
            this.cb_algorithm.Items.Clear();
            this.cb_algorithm.Items.Add("raycast_py");
            this.cb_algorithm.Items.Add("raycast_asm");
            this.cb_algorithm.Items.Add("pathtracer_py");
            this.cb_algorithm.Items.Add("pathtracer_asm");
            this.cb_algorithm.SelectedIndex = 3;

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
