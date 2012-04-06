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
using System.Windows.Shapes;

namespace RenmasWPF2
{
    /// <summary>
    /// Interaction logic for SpectrumDialog.xaml
    /// </summary>
    public partial class SpectrumDialog : Window
    {
        Spectrum spectrum;
        public SpectrumDialog(Spectrum s)
        {
            InitializeComponent();
            this.spectrum = s;
            this.build_gui();
            
        }

        private void build_gui()
        {
            SpectrumEditor cp = new SpectrumEditor(this.spectrum);

            StackPanel buttons = new StackPanel();
            buttons.Orientation = Orientation.Horizontal;
            buttons.HorizontalAlignment = System.Windows.HorizontalAlignment.Right;
            

            Button ok = new Button();
            ok.Content = "OK";
            ok.Width = 50;
            ok.Margin = new Thickness(5);

            ok.Click += new RoutedEventHandler(ok_Click);

            Button cancel = new Button();
            cancel.Content = "Cancel";
            cancel.Width = 50;
            cancel.Margin = new Thickness(5);
            cancel.Click += new RoutedEventHandler(cancel_Click);

            buttons.Children.Add(ok);
            buttons.Children.Add(cancel);

            StackPanel sp_all = new StackPanel();
            sp_all.Children.Add(cp);
            sp_all.Children.Add(buttons);

            this.Content = sp_all;
            this.Width = 350;
            this.Height = 200;
        }

        void cancel_Click(object sender, RoutedEventArgs e)
        {
            this.DialogResult = false;
            this.Close();
        }

        void ok_Click(object sender, RoutedEventArgs e)
        {
            this.DialogResult = true;
            this.Close();
        }
    }
}
