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
        private MenuItem file_exit;
        private MenuItem tools_run_script, tools_render;

        // ------------- GUI TextBoxes ------------------------
        private TextBox camera_eye_x, camera_eye_y, camera_eye_z;
        private TextBox camera_lookat_x, camera_lookat_y, camera_lookat_z;
        private TextBox camera_distance;

        // -------------- GUI Image for represent FrameBuffer
        private Image frame_buffer_control;
        
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
                    this.Content = rootElement;
                    this.Width = 640;
                    this.Height = 480;
                  
                    SolidColorBrush mySolidColorBrush = new SolidColorBrush();
                    mySolidColorBrush.Color = Color.FromArgb(255, 69, 69, 69);
                    this.Background = mySolidColorBrush;

                    this.BindGuiEvents(rootElement);
                }
                catch (Exception e)
                {
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

            // TEXTBOX 
            this.camera_eye_x = (TextBox)LogicalTreeHelper.FindLogicalNode(element, "camera_eye_x");
            if (this.camera_eye_x != null) this.camera_eye_x.TextChanged += camera_changed;
            this.camera_eye_y = (TextBox)LogicalTreeHelper.FindLogicalNode(element, "camera_eye_y");
            if (this.camera_eye_y != null) this.camera_eye_y.TextChanged += camera_changed;
            this.camera_eye_z = (TextBox)LogicalTreeHelper.FindLogicalNode(element, "camera_eye_z");
            if (this.camera_eye_z != null) this.camera_eye_z.TextChanged += camera_changed;
            this.camera_lookat_x = (TextBox)LogicalTreeHelper.FindLogicalNode(element, "camera_lookat_x");
            this.camera_lookat_y = (TextBox)LogicalTreeHelper.FindLogicalNode(element, "camera_lookat_y");
            this.camera_lookat_z = (TextBox)LogicalTreeHelper.FindLogicalNode(element, "camera_lookat_z");
            this.camera_distance = (TextBox)LogicalTreeHelper.FindLogicalNode(element, "camera_distance");

            this.frame_buffer_control = (Image)LogicalTreeHelper.FindLogicalNode(element, "render_window");
            
        }
        private void menu_file_exit(object sender, RoutedEventArgs e)
        {
            this.Close();
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
                ren.PrepareForRendering();
                this.update_camera();
            }
            
        }
        private void camera_changed(object sender, RoutedEventArgs e)
        {
            string eyex = this.camera_eye_x.Text;
            string eyey = this.camera_eye_y.Text;
            string eyez = this.camera_eye_z.Text;
            string value = eyex + "," + eyey + "," + eyez;
            //this.ren.SetProp("camera", "eye", value);
        }

        private void menu_tools_render(object sender, RoutedEventArgs e)
        {
            this.rendering = true;
            while (true)
            {
                ren.RenderTile();
                this.frame_buffer_control.Source = this.FrameSource();
                int res = ren.IsRenderingFinished();
                if (res != 0) break;
                if (!rendering) break;
                this.DoEvents();
            }
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
        private void button1_Click(object sender, RoutedEventArgs e)
        {
            this.image1.Source = this.FrameSource();
        }

        private void button2_Click(object sender, RoutedEventArgs e)
        {
            this.rendering = true;
            DateTime start = DateTime.Now;
            while (true)
            {
                ren.RenderTile();
                this.image1.Source = this.FrameSource();
                int res = ren.IsRenderingFinished();
                if (res != 0) break;
                if (!rendering) break;
                this.DoEvents();
            }
            this.rendering = false;
            DateTime end = DateTime.Now;
            long interval = end.Ticks - start.Ticks;
            TimeSpan tm = new TimeSpan(interval);
            this.rendering = false;
        }

        private void button3_Click(object sender, RoutedEventArgs e)
        {
            ren.PrepareForRendering();
        }

        private void button4_Click(object sender, RoutedEventArgs e)
        {
            this.rendering = false;
        }
    }
}
