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
    /// Interaction logic for SpectrumEditor.xaml
    /// </summary>
    public partial class SpectrumEditor : UserControl
    {
        Spectrum spectrum;
        public SpectrumEditor(Spectrum spectrum)
        {
            InitializeComponent();
            this.spectrum = spectrum;
            this.build_gui();
        }

        private void build_gui()
        {
            this.DataContext = spectrum;

            Rectangle rect1 = new Rectangle();
            rect1.Width = 70;
            rect1.Height = 70;
            Binding bind_brush = new Binding("SpectrumBrush");
            rect1.SetBinding(Rectangle.FillProperty, bind_brush);

            StackPanel sp = new StackPanel();
            StackPanel sp1 = this.tb_slider("R", "Red:");
            StackPanel sp2 = this.tb_slider("G", "Green:");
            StackPanel sp3 = this.tb_slider("B", "Blue:");

            sp.Children.Add(sp1);
            sp.Children.Add(sp2);
            sp.Children.Add(sp3);

            Slider rainbow_slider = new Slider();
            rainbow_slider.Width = 300;
            rainbow_slider.Minimum = 0.0;
            rainbow_slider.Maximum = 1.0;
            rainbow_slider.Background = this.spectrum.rainbow_brush(new Point(0.0, 0.5), new Point(1.0, 0.5));
            Binding bind_rainbow = new Binding("RainbowValue");
            rainbow_slider.SetBinding(Slider.ValueProperty, bind_rainbow);
            

            StackPanel sp_color = new StackPanel();
            sp_color.Orientation = Orientation.Horizontal;
            sp_color.Height = 80;
            sp_color.Children.Add(rect1);
            sp_color.Children.Add(sp);

            StackPanel all = new StackPanel();
            all.Children.Add(sp_color);
            all.Children.Add(rainbow_slider);
            all.Height = 120;
            all.Width = 300;
            this.Content = all;

        }

        private StackPanel tb_slider(string property_name, string label)
        {
            TextBlock tb_key = new TextBlock();
            tb_key.Text = label;
            tb_key.Height = 20;
            tb_key.Width = 45;
            tb_key.TextAlignment = TextAlignment.Right;

            Slider slider = new Slider();
            slider.Minimum = 0;
            slider.Maximum = 255;
            slider.Width = 150;
            Binding bind_slider = new Binding(property_name);
            slider.SetBinding(Slider.ValueProperty, bind_slider);

            TextBox tbox_key = new TextBox();
            tbox_key.Width = 35;
            tbox_key.Height = 20;
            //tbox_key.Foreground = Brushes.White;
            //tbox_key.CaretBrush = Brushes.White;
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
