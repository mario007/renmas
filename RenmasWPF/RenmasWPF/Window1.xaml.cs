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
        Renmas ren;
        bool rendering = false;

        // -------------GUI MenuItems --------------------------
        private MenuItem file_exit, file_export_image;
        private MenuItem tools_run_script, tools_render, tools_stop;

        // ------------- GUI TextBoxes ------------------------
        private TextBox camera_eye_x, camera_eye_y, camera_eye_z;
        private TextBox camera_lookat_x, camera_lookat_y, camera_lookat_z;
        private TextBox camera_distance;

        private Grid main_grid;
        private object content;
        private object sve_zivo;

        // -------------- GUI Image for represent FrameBuffer
        private Image frame_buffer_control;

        // -------------- Logger
        private TextBox log_output;

        // ------------ Global Settings
        private TextBox resolution_x, resolution_y, pixel_size, samples_per_pixel;
        private ComboBox cb_algorithm;
        
        public Window1()
        {
            InitializeComponent();
            ren = new Renmas();
            //ren.RunFile("G:\\renmas_scripts\\sphere.py");
            //ren.RunFile("G:\\renmas_scripts\\sphere.py");
            //ren.SetProp("camera", "eye", "3.3,4.4,5.5");
            //string text = ren.GetProp("camera", "eye");
            LoadGUI();
            
        }

        private void LoadGUI()
        {
            Microsoft.Win32.OpenFileDialog dlg = new Microsoft.Win32.OpenFileDialog();
            dlg.FileName = "Document"; // Default file name
            dlg.DefaultExt = ".xaml"; // Default file extension
            dlg.Filter = "GUI XAML (.xaml)|*.xaml"; // Filter files by extension

            Nullable<bool> result = dlg.ShowDialog();
            if (result == true)
            {
                string filename = dlg.FileName;
                try
                {
                    FileStream s = new FileStream(filename, FileMode.Open);
                    DependencyObject rootElement = (DependencyObject)XamlReader.Load(s);
                    this.sve_zivo = rootElement;
                    //this.main_grid = (Grid)LogicalTreeHelper.FindLogicalNode(rootElement, "LayoutRoot");
                    //Window win = (Window)LogicalTreeHelper.FindLogicalNode(rootElement, "Window");
                    

                    //this.content = win.Content;
                    //win.Content = null;
                    
                    
                    //this.Content = this.main_grid;
                    this.Content = rootElement;
                    this.Width = 800;
                    this.Height = 600;
                  
                    SolidColorBrush mySolidColorBrush = new SolidColorBrush();
                    mySolidColorBrush.Color = Color.FromArgb(255, 47, 47, 47);
                    this.Background = mySolidColorBrush;
                    
                    // Bind Events for Loaded GUI
                    this.BindGuiEvents(rootElement);

                }
                catch (Exception e)
                {
                    this.Width = 640;
                }
            }     
        }
        private void BindGuiEvents(DependencyObject element)
        {
            // MENU GUI------------
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

            // TEXTBOX 
            this.camera_eye_x = (TextBox)LogicalTreeHelper.FindLogicalNode(element, "camera_eye_x");
            this.camera_eye_y = (TextBox)LogicalTreeHelper.FindLogicalNode(element, "camera_eye_y");
            this.camera_eye_z = (TextBox)LogicalTreeHelper.FindLogicalNode(element, "camera_eye_z");
            this.camera_lookat_x = (TextBox)LogicalTreeHelper.FindLogicalNode(element, "camera_lookat_x");
            this.camera_lookat_y = (TextBox)LogicalTreeHelper.FindLogicalNode(element, "camera_lookat_y");
            this.camera_lookat_z = (TextBox)LogicalTreeHelper.FindLogicalNode(element, "camera_lookat_z");
            this.camera_distance = (TextBox)LogicalTreeHelper.FindLogicalNode(element, "camera_distance");

            this.frame_buffer_control = (Image)LogicalTreeHelper.FindLogicalNode(element, "render_window");

            this.log_output = (TextBox)LogicalTreeHelper.FindLogicalNode(element, "log_output");

            // Global Settings
            this.resolution_x = (TextBox)LogicalTreeHelper.FindLogicalNode(element, "output_resolution_x");
            this.resolution_y = (TextBox)LogicalTreeHelper.FindLogicalNode(element, "output_resolution_y");
            
            
            
            this.pixel_size = (TextBox)LogicalTreeHelper.FindLogicalNode(element, "output_pixelsize");
            this.samples_per_pixel = (TextBox)LogicalTreeHelper.FindLogicalNode(element, "output_samples");
            this.cb_algorithm = (ComboBox)LogicalTreeHelper.FindLogicalNode(element, "cb_algorithm");

            
            this.update_global_settings();
            this.update_camera();
            
            // changed events
            this.resolution_x.TextChanged += resolution_changed;
            this.resolution_y.TextChanged += resolution_changed;
            this.pixel_size.TextChanged += pixel_resize;
            this.samples_per_pixel.TextChanged += samples_per_pixel_evt;
            this.cb_algorithm.SelectionChanged += select_algorithm_evt;

            this.camera_eye_x.TextChanged += camera_eye_changed;
            this.camera_eye_y.TextChanged += camera_eye_changed;
            this.camera_eye_z.TextChanged += camera_eye_changed;
            this.camera_lookat_x.TextChanged += camera_lookat_changed;
            this.camera_lookat_y.TextChanged += camera_lookat_changed;
            this.camera_lookat_z.TextChanged += camera_lookat_changed;
            this.camera_distance.TextChanged += camera_distance_changed;
            
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
                this.save_png(filename, this.FrameSource());
            }
        }
        private void select_algorithm_evt(object sender, RoutedEventArgs e)
        {
            string text = (string)this.cb_algorithm.SelectedItem;
            this.ren.SetProp("global_settings", "algorithm", text);
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
                int result2 = this.ren.RunFile(filename);
                if (result2 == -1)
                {
                    // alert user about failure
                    return;
                }
                this.update_camera();
                this.update_global_settings();
            }
            
        }
        private void camera_eye_changed(object sender, RoutedEventArgs e)
        {
            float eyex, eyey, eyez;
            try { eyex = Convert.ToSingle(this.camera_eye_x.Text); }
            catch (Exception ex) { eyex = 10.0f; }
            try { eyey = Convert.ToSingle(this.camera_eye_y.Text); }
            catch (Exception ex) { eyey = 10.0f; }
            try { eyez = Convert.ToSingle(this.camera_eye_z.Text); }
            catch (Exception ex) { eyez = 10.0f; }

            string value = eyex.ToString() + "," + eyey.ToString() + "," + eyez.ToString();
            this.ren.SetProp("camera", "eye", value);
        }

        private void camera_distance_changed(object sender, RoutedEventArgs e)
        {
            float distance;
            try { distance = Convert.ToSingle(this.camera_distance.Text); }
            catch (Exception ex) { distance = 400.0f; }
            string value = distance.ToString();
            this.ren.SetProp("camera", "distance", value);

        }

        private void camera_lookat_changed(object sender, RoutedEventArgs e)
        {
            float lookatx, lookaty, lookatz;
            try { lookatx = Convert.ToSingle(this.camera_lookat_x.Text); }
            catch (Exception ex) { lookatx = 0.0f; }
            try { lookaty = Convert.ToSingle(this.camera_lookat_y.Text); }
            catch (Exception ex) { lookaty = 0.0f; }
            try { lookatz = Convert.ToSingle(this.camera_lookat_z.Text); }
            catch (Exception ex) { lookatz = 0.0f; }

            string value = lookatx.ToString() + "," + lookaty.ToString() + "," + lookatz.ToString();
            this.ren.SetProp("camera", "lookat", value);
        }

        private void resolution_changed(object sender, RoutedEventArgs e)
        {
            uint width, height;
            try
            {
                width = Convert.ToUInt32(this.resolution_x.Text);
            }
            catch (Exception ex) { width = 200;  }
            try
            {
                height = Convert.ToUInt32(this.resolution_y.Text);
            }
            catch (Exception ex) { height = 200; }
            
            string text = width.ToString() + "," + height.ToString();
            this.ren.SetProp("global_settings", "resolution", text);
        }

        private void pixel_resize(object sender, RoutedEventArgs e)
        {
            float pix_size;
            try
            {
                pix_size = Convert.ToSingle(this.pixel_size.Text);
            }
            catch (Exception ex) { pix_size = 1.0f; }

            string text = pix_size.ToString();
            this.ren.SetProp("global_settings", "pixel_size", text);
        }
        private void samples_per_pixel_evt(object sender, RoutedEventArgs e)
        {
            uint nsamples;
            try
            {
                nsamples = Convert.ToUInt32(this.samples_per_pixel.Text);
            }
            catch (Exception ex) { nsamples = 1; }

            string text = nsamples.ToString();
            this.ren.SetProp("global_settings", "samples_per_pixel", text);
        }

        private void menu_tools_render(object sender, RoutedEventArgs e)
        {
            int ret = ren.PrepareForRendering();
            string text = ren.GetProp("log", "");
            this.logger(text);
            if (ret == 0) return; //something is wrong, we quit rendering
            this.rendering = true;
            DateTime start = DateTime.Now;
            while (true)
            {
                int res = ren.RenderTile();
                this.frame_buffer_control.Source = this.FrameSource();
                if (res != 0) break;
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

        private void update_camera()
        {
            string value = ren.GetProp("camera", "eye");
            string[] words = value.Split(',');
            this.camera_eye_x.Text = words[0];
            this.camera_eye_y.Text = words[1];
            this.camera_eye_z.Text = words[2];
            value = ren.GetProp("camera", "lookat");
            string[] words2 = value.Split(',');
            this.camera_lookat_x.Text = words2[0];
            this.camera_lookat_y.Text = words2[1];
            this.camera_lookat_z.Text = words2[2];
            value = ren.GetProp("camera", "distance");
            this.camera_distance.Text = value;  
        }

        private void update_global_settings()
        {
            string value = ren.GetProp("global_settings", "resolution");
            string[] words = value.Split(',');
            this.resolution_x.Text = words[0];
            this.resolution_y.Text = words[1];
            value = ren.GetProp("global_settings", "pixel_size");
            this.pixel_size.Text = value;
            value = ren.GetProp("global_settings", "samples_per_pixel");
            this.samples_per_pixel.Text = value;
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

        private BitmapSource FrameSource()
        {
            int width = ren.WidthFrameBuffer();
            int height = ren.HeightFrameBuffer();
            int pitch = ren.PitchFrameBuffer();
            uint addr = ren.AddrFrameBuffer();
            //PixelFormat pixformat = PixelFormats.Rgb128Float;
            PixelFormat pixformat = PixelFormats.Bgra32;
            IntPtr ptr = new IntPtr(addr);

            BitmapSource image = BitmapSource.Create(width, height,
                96, 96, pixformat, null, ptr, height*pitch, pitch);
            return image;
            
        }
        
    }
}
