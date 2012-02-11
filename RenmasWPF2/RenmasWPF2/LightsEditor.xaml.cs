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
        TextBox txt_scaler;
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
        }

        public void build_gui()
        {
            this.DataContext = lights;

            TextBlock tb_lights = new TextBlock();
            tb_lights.Text = "Lights: ";
            ComboBox cb = new ComboBox();
            Binding bind = new Binding("LightNames");
            cb.SetBinding(ComboBox.ItemsSourceProperty, bind);

            Binding bind2 = new Binding("SelectedLight");
            cb.SetBinding(ComboBox.SelectedItemProperty, bind2);

            StackPanel sp = new StackPanel();
            sp.Orientation = Orientation.Horizontal;
            sp.Children.Add(tb_lights);
            sp.Children.Add(cb);

            if (this.lights.SelectedLight != "")
            {
                StackPanel sp_x = this.build_lbltxt("X: ", "PositionX");
                StackPanel sp_y = this.build_lbltxt("Y: ", "PositionY");
                StackPanel sp_z = this.build_lbltxt("Z: ", "PositionZ");
                StackPanel position = build_row(sp_x, sp_y, sp_z);

                TextBlock light_t = new TextBlock();
                light_t.Text = "Light Type:  ";
                TextBlock light_type = new TextBlock();
                light_type.Text = this.lights.LightType;
                StackPanel sp_type = new StackPanel();
                sp_type.Orientation = Orientation.Horizontal;
                sp_type.Children.Add(light_t);
                sp_type.Children.Add(light_type);

                TextBlock scale = new TextBlock();
                scale.Text = "Scaler";
                TextBox scaler_txt = new TextBox();
                scaler_txt.Width = 40;
                this.txt_scaler = scaler_txt;
                
                Button btn = new Button();
                btn.Content = "Scale";
                btn.Click += new RoutedEventHandler(btn_Click);

                StackPanel scaler_sp = new StackPanel();
                scaler_sp.Orientation = Orientation.Horizontal;
                scaler_sp.Children.Add(scale);
                scaler_sp.Children.Add(scaler_txt);
                scaler_sp.Children.Add(btn);

                ComboBox cb_lambdas = new ComboBox();
                Binding bind_lambdas = new Binding("Lambdas");
                cb_lambdas.SetBinding(ComboBox.ItemsSourceProperty, bind_lambdas);
                Binding bind_sel_lam = new Binding("SelectedLambda");
                cb_lambdas.SetBinding(ComboBox.SelectedItemProperty, bind_sel_lam);
                TextBox txt_intesity = new TextBox();
                Binding bind_intesity = new Binding("Intesity");
                txt_intesity.SetBinding(TextBox.TextProperty, bind_intesity);

                StackPanel sp_new = new StackPanel();
                sp_new.Children.Add(sp);
                sp_new.Children.Add(sp_type);
                sp_new.Children.Add(position);
                sp_new.Children.Add(cb_lambdas);
                sp_new.Children.Add(txt_intesity);
                sp_new.Children.Add(scaler_sp);
                this.Content = sp_new;

            }
            else
            {
                this.Content = sp;
            }
        }

        void btn_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                float t = System.Convert.ToSingle(this.txt_scaler.Text);
                this.lights.scale_spectrum(t);
            }
            catch (Exception)
            {
            }
           
        }

        private StackPanel build_row(StackPanel sp1, StackPanel sp2, StackPanel sp3)
        {
            StackPanel sp = new StackPanel();
            sp.Orientation = Orientation.Horizontal;
            sp.Children.Add(sp1);
            sp.Children.Add(sp2);
            sp.Children.Add(sp3);
            return sp;
        }
        private StackPanel build_lbltxt(string text, string property)
        {
            TextBlock label = new TextBlock();
            label.Text = text;
            TextBox tb = new TextBox();
            tb.Width = 40;

            StackPanel sp = new StackPanel();
            sp.Orientation = Orientation.Horizontal;
            sp.Children.Add(label);
            sp.Children.Add(tb);

            Binding binder = new Binding(property);
            binder.Source = lights;
            tb.SetBinding(TextBox.TextProperty, binder);
            sp.Height = 20;
            return sp;
        }
    }
}
