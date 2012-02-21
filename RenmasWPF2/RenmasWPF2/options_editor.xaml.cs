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
    /// Interaction logic for options_editor.xaml
    /// </summary>
    public partial class Options_editor : UserControl
    {
        Options options;
        public Options_editor(Options options)
        {
            InitializeComponent();
            this.options = options;
            this.build_gui();
        }

        private void build_gui()
        {
            this.DataContext = options;

            StackPanel threads = this.build_lbltxt(" Threads: ", "Threads");
            StackPanel spp1 = this.build_lbltxt(" SPP: ", "Spp");
            StackPanel pixel_size = this.build_lbltxt(" Pixel size: ", "PixelSize");
            StackPanel asm = this.build_lblcb(" Asm: ", "Asm");
            StackPanel spectral = this.build_lblcb(" Spectral: ", "Spectral");
            StackPanel width = this.build_lbltxt(" Width: ", "Width");
            StackPanel height = this.build_lbltxt(" Height: ", "Height");

            StackPanel sp = new StackPanel();
            sp.Children.Add(threads);
            sp.Children.Add(spp1);
            sp.Children.Add(pixel_size);
            sp.Children.Add(asm);
            sp.Children.Add(spectral);
            sp.Children.Add(width);
            sp.Children.Add(height);

            Expander expander = new Expander();
            expander.Header = "Options";
            expander.Foreground = Brushes.White;
            expander.Content = sp;
            this.Content = expander;
        }

        private StackPanel build_lblcb(string text, string property)
        {
            TextBlock tb = new TextBlock();
            tb.Text = text;
            tb.TextAlignment = TextAlignment.Right;
            tb.VerticalAlignment = System.Windows.VerticalAlignment.Center;
            tb.Width = 55;
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

        private StackPanel build_lbltxt(string text, string property)
        {
            TextBlock label = new TextBlock();
            label.Text = text;
            label.TextAlignment = TextAlignment.Right;
            label.Width = 55;
            label.VerticalAlignment = System.Windows.VerticalAlignment.Center;
            TextBox tb = new TextBox();
            tb.Width = 40;
            tb.Height = 20;
            tb.Foreground = Brushes.White;
            tb.CaretBrush = Brushes.White;

            StackPanel sp = new StackPanel();
            sp.Orientation = Orientation.Horizontal;
            sp.Children.Add(label);
            sp.Children.Add(tb);

            Binding binder = new Binding(property);
            binder.Source = options;
            tb.SetBinding(TextBox.TextProperty, binder);
            sp.Height = 25;
            return sp;
        }
    }
}
