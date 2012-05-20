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
using System.Diagnostics;

namespace RenmasWPF2
{
    /// <summary>
    /// Interaction logic for LightsEditor.xaml
    /// </summary>
    public partial class LightsEditor : UserControl
    {
        Lights lights;
        public LightsEditor(Lights lights)
        {
            InitializeComponent();
            this.lights = lights;
            this.build_gui();
            this.lights.LightTypeChanged += new EventHandler(lights_LightTypeChanged);
        }

        void lights_LightTypeChanged(object sender, EventArgs e)
        {
            this.build_gui();
            Expander exp = (Expander)this.Content;
            exp.IsExpanded = true;
        }

        public void build_gui()
        {
            this.DataContext = lights;

            TextBlock tb_lights = new TextBlock();
            tb_lights.Text = " Lights: ";
            ComboBox cb = new ComboBox();
            cb.Width = 150;
            cb.Foreground = Brushes.White;
            Binding bind = new Binding("LightNames");
            cb.SetBinding(ComboBox.ItemsSourceProperty, bind);

            Binding bind2 = new Binding("SelectedLight");
            cb.SetBinding(ComboBox.SelectedItemProperty, bind2);

            StackPanel sp = new StackPanel();
            sp.Orientation = Orientation.Horizontal;
            sp.Children.Add(tb_lights);
            sp.Children.Add(cb);

            StackPanel all = new StackPanel();
            all.Children.Add(sp);
            if (this.lights.SelectedLight != "")
            {
                if (this.lights.LightType == "PointLight")
                {
                    this.build_point_light(all);
                }
            }

            Expander expander = new Expander();
            expander.Header = "Lights";
            expander.Foreground = Brushes.White;
            expander.Content = all;
            this.Content = expander;
            
        }

        private void build_point_light(StackPanel sp)
        {
            TextBlock light_t = new TextBlock();
            light_t.Text = " Light Type:  " + this.lights.LightType;
            light_t.Width = 200;
            light_t.Height = 20;

            StackPanel pos = this.build_position();
            StackPanel wave = this.build_wavelength();
            StackPanel intesity = this.build_lbltxt_intesity(" Intesity: ", "Intesity");

            sp.Children.Add(light_t);
            sp.Children.Add(pos);
            sp.Children.Add(wave);
            sp.Children.Add(intesity);
        }

        private StackPanel build_wavelength()
        {
            TextBlock tb_wavelength = new TextBlock();
            tb_wavelength.Text = " Wavelength: ";
            tb_wavelength.Width = 80;
            tb_wavelength.TextAlignment = TextAlignment.Right;
            tb_wavelength.VerticalAlignment = System.Windows.VerticalAlignment.Center;
            ComboBox cb_lambdas = new ComboBox();
            Binding bind_lambdas = new Binding("Lambdas");
            cb_lambdas.SetBinding(ComboBox.ItemsSourceProperty, bind_lambdas);
            Binding bind_sel_lam = new Binding("SelectedLambda");
            cb_lambdas.SetBinding(ComboBox.SelectedItemProperty, bind_sel_lam);
            cb_lambdas.Foreground = Brushes.White;
            cb_lambdas.Width = 80;
            cb_lambdas.Height = 20;
            StackPanel sp_wave = new StackPanel();
            sp_wave.Orientation = Orientation.Horizontal;
            sp_wave.Height = 25;
            sp_wave.Children.Add(tb_wavelength);
            sp_wave.Children.Add(cb_lambdas);
            return sp_wave;
        }

        private StackPanel build_position()
        {
            StackPanel sp_x = this.build_lbltxt("  X: ", "PositionX");
            StackPanel sp_y = this.build_lbltxt("  Y: ", "PositionY");
            StackPanel sp_z = this.build_lbltxt("  Z: ", "PositionZ");
            StackPanel position1 = build_row(sp_x, sp_y, sp_z);
            TextBlock tb_pos = new TextBlock();
            tb_pos.Text = " Position:";
            tb_pos.VerticalAlignment = System.Windows.VerticalAlignment.Center;
            StackPanel position = new StackPanel();
            position.Orientation = Orientation.Horizontal;
            position.Height = 25;
            position.Children.Add(tb_pos);
            position.Children.Add(position1);
            return position;
        }

        private StackPanel build_row(StackPanel sp1, StackPanel sp2, StackPanel sp3)
        {
            StackPanel sp = new StackPanel();
            sp.Orientation = Orientation.Horizontal;
            sp.Children.Add(sp1);
            sp.Children.Add(sp2);
            sp.Children.Add(sp3);
            sp.Height = 25;
            return sp;
        }
        private StackPanel build_lbltxt(string text, string property)
        {
            TextBlock label = new TextBlock();
            label.Text = text;
            label.VerticalAlignment = System.Windows.VerticalAlignment.Center;
            TextBox tb = new TextBox();
            tb.Width = 50;
            tb.Height = 20;
            tb.Foreground = Brushes.White;
            tb.CaretBrush = Brushes.White;

            StackPanel sp = new StackPanel();
            sp.Orientation = Orientation.Horizontal;
            sp.Children.Add(label);
            sp.Children.Add(tb);

            Binding binder = new Binding(property);
            binder.Source = lights;
            tb.SetBinding(TextBox.TextProperty, binder);
            sp.Height = 25;
            return sp;
        }

        private StackPanel build_lbltxt_intesity(string text, string property)
        {
            TextBlock label = new TextBlock();
            label.Text = text;
            label.Width = 70;
            label.TextAlignment = TextAlignment.Right;
            label.VerticalAlignment = System.Windows.VerticalAlignment.Center;
            TextBox tb = new TextBox();
            tb.Width = 80;
            tb.Height = 20;
            tb.Foreground = Brushes.White;
            tb.CaretBrush = Brushes.White;

            StackPanel sp = new StackPanel();
            sp.Orientation = Orientation.Horizontal;
            sp.Children.Add(label);
            sp.Children.Add(tb);

            Binding binder = new Binding(property);
            binder.Source = lights;
            tb.SetBinding(TextBox.TextProperty, binder);
            sp.Height = 25;
            return sp;
        }
    }
}
