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

namespace RenEditors
{
    /// <summary>
    /// Interaction logic for TmoEditor.xaml
    /// </summary>
    public partial class TmoEditor : UserControl
    {
        public Tmo target = null;

        public TmoEditor()
        {
            InitializeComponent();
        }

        public void set_target(Tmo target)
        {
            this.target = target;
            build_widgets();
        }

        private void build_widgets()
        {
            List<BaseProperty> props = this.target.get_props();

            StackPanel sp = new StackPanel();
            sp.Orientation = Orientation.Vertical;
            sp.VerticalAlignment = System.Windows.VerticalAlignment.Stretch;
            TextBlock title = new TextBlock();
            title.Text = "Tmo public properties";
            title.Foreground = Brushes.White;
            sp.Children.Add(title);

            foreach (BaseProperty prop in props)
            {
                UserControl editor = this.build_editor(prop);
                sp.Children.Add(editor);
            }

            StackPanel btns = new StackPanel();
            btns.Orientation = Orientation.Horizontal;

            Button btn_shader = new Button();
            btn_shader.Content = "Shader code";
            btn_shader.Foreground = Brushes.White;
            btn_shader.Width = 90;
            btn_shader.Margin = new Thickness(5);
            btn_shader.Click += btn_shader_Click;
            btns.Children.Add(btn_shader);

            Button btn_assembly = new Button();
            btn_assembly.Content = "Assembly code";
            btn_assembly.Foreground = Brushes.White;
            btn_assembly.Width = 90;
            btn_assembly.Margin = new Thickness(5);
            btn_assembly.Click += btn_assembly_Click;
            btns.Children.Add(btn_assembly);
            

            sp.Children.Add(btns);
            this.Content = sp;
        }

        void btn_assembly_Click(object sender, RoutedEventArgs e)
        {
            var wnd = new Window();
            TextBox code = new TextBox();
            code.IsReadOnly = true;
            code.Text = this.target.assembly_code();
            wnd.Content = code;
            wnd.Show();
        }

        void btn_shader_Click(object sender, RoutedEventArgs e)
        {
            var wnd = new Window();
            TextBox code = new TextBox();
            code.IsReadOnly = true;
            code.Text = this.target.shader_code();
            wnd.Content = code;
            wnd.Show();
        }

        public UserControl build_editor(BaseProperty property)
        {
            Type t = property.GetType();
            if (t == typeof(FloatProperty))
            {
                FloatEditor ed = new FloatEditor();
                ed.set_target((FloatProperty)property);
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
