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

namespace RenmasWPF2
{
    /// <summary>
    /// Interaction logic for ToneMappingEditor.xaml
    /// </summary>
    public partial class ToneMappingEditor : UserControl
    {
        ToneMappingOperators tm_operators;
        public ToneMappingEditor(ToneMappingOperators tone_mapping_operators)
        {
            InitializeComponent();
            this.tm_operators = tone_mapping_operators;
            this.build_gui();
            this.tm_operators.OperatorTypeChanged += new EventHandler(operator_OperatorTypeChanged);
        }

        void operator_OperatorTypeChanged(object sender, EventArgs e)
        {
            this.build_gui();
            Expander exp = (Expander)this.Content;
            exp.IsExpanded = true;
            
        }

        private void build_gui()
        {
            this.DataContext = tm_operators;

            TextBlock tb_operators = new TextBlock();
            tb_operators.Text = " Operators: ";
            tb_operators.Width = 60;
            tb_operators.Height = 20;

            ComboBox cb = new ComboBox();
            cb.Width = 210;
            cb.Height = 20;
            cb.Foreground = Brushes.White;
            Binding bind = new Binding("OperatorNames");
            cb.SetBinding(ComboBox.ItemsSourceProperty, bind);

            Binding bind2 = new Binding("SelectedOperator");
            cb.SetBinding(ComboBox.SelectedItemProperty, bind2);

            StackPanel sp = new StackPanel();
            sp.Orientation = Orientation.Horizontal;
            sp.Height = 25;
            sp.Children.Add(tb_operators);
            sp.Children.Add(cb);

            StackPanel tonemap_sp = this.build_lblcb(" Tone Mapping: ", "ToneMapping");

            StackPanel sp_operator = new StackPanel();
            if (tm_operators.SelectedOperator == "Reinhard")
            {
                this.build_reinhard(sp_operator);
            }
            else if (tm_operators.SelectedOperator == "Photoreceptor")
            {
                this.build_photoreceptor(sp_operator);
            }
            else
            {
            }
            

            StackPanel all = new StackPanel();
            all.Children.Add(tonemap_sp);
            all.Children.Add(sp);
            all.Children.Add(sp_operator);

            Expander expander = new Expander();
            expander.Header = " Tone mapping";
            expander.Foreground = Brushes.White;
            expander.Content = all;
            this.Content = expander;
        }

        private StackPanel build_lblcb(string text, string property)
        {
            TextBlock tb = new TextBlock();
            tb.Text = text;
            tb.TextAlignment = TextAlignment.Right;
            tb.VerticalAlignment = System.Windows.VerticalAlignment.Center;
            tb.Width = 85;
            StackPanel sp = new StackPanel();
            sp.Orientation = Orientation.Horizontal;

            CheckBox cb = new CheckBox();
            cb.VerticalAlignment = System.Windows.VerticalAlignment.Center;
            Binding bind = new Binding(property);
            cb.SetBinding(CheckBox.IsCheckedProperty, bind);
            SolidColorBrush mySolidColorBrush = new SolidColorBrush();
            mySolidColorBrush.Color = Color.FromArgb(255, 51, 51, 51);
            cb.Background = mySolidColorBrush;
            SolidColorBrush mySolidColorBrush2 = new SolidColorBrush();
            mySolidColorBrush2.Color = Color.FromArgb(255, 112, 112, 112);
            cb.BorderBrush = mySolidColorBrush2;
            //Background="#FF333333" BorderBrush="#FF707070"

            sp.Height = 25;
            sp.Children.Add(tb);
            sp.Children.Add(cb);
            return sp;
        }

        private void build_photoreceptor(StackPanel sp)
        {
            StackPanel sp_contrast = this.tb_slider("PhotoreceptorContrast", " Contrast:", 1.0f);
            StackPanel sp_adaptation = this.tb_slider("PhotoreceptorAdaptation", " Adaptation:", 1.0f);
            StackPanel sp_colornes = this.tb_slider("PhotoreceptorColornes", " Colornes:", 1.0f);
            StackPanel sp_lightnes = this.tb_slider("PhotoreceptorLightnes", " Lightnes:", 100.0f);
            sp.Children.Add(sp_contrast);
            sp.Children.Add(sp_adaptation);
            sp.Children.Add(sp_colornes);
            sp.Children.Add(sp_lightnes);

        }

        private void build_reinhard(StackPanel sp)
        {
            StackPanel sp_key = this.tb_slider("ReinhardSceneKey", " Key:", 1.5f);
            StackPanel sp_saturation = this.tb_slider("ReinhardSaturation", " Saturation:", 1.0f);
            sp.Children.Add(sp_key);
            sp.Children.Add(sp_saturation);

        }

        private StackPanel tb_slider(string property_name, string label, float max)
        {
            TextBlock tb_key = new TextBlock();
            tb_key.Text = label;
            tb_key.Height = 20;
            tb_key.Width = 65;
            tb_key.TextAlignment = TextAlignment.Right;

            Slider slider = new Slider();
            slider.Minimum = 0.0;
            slider.Maximum = max;
            slider.Width = 150;
            Binding bind_slider = new Binding(property_name);
            slider.SetBinding(Slider.ValueProperty, bind_slider);

            TextBox tbox_key = new TextBox();
            tbox_key.Width = 60;
            tbox_key.Height = 20;
            tbox_key.Foreground = Brushes.White;
            tbox_key.CaretBrush = Brushes.White;
            Binding bind_tbox_key = new Binding(property_name);
            tbox_key.SetBinding(TextBox.TextProperty, bind_tbox_key);

            StackPanel sp_key = new StackPanel();
            sp_key.Orientation = Orientation.Horizontal;
            sp_key.Height = 25;
            sp_key.Children.Add(tb_key);
            sp_key.Children.Add(slider);
            sp_key.Children.Add(tbox_key);

            return sp_key;
        }
    }
}
