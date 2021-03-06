﻿using System;
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

namespace RenmasWPF3
{
    /// <summary>
    /// Interaction logic for IntEditor.xaml
    /// </summary>
    public partial class IntEditor : UserControl
    {
        PyWrapper.IntProperty target;

        public IntEditor()
        {
            InitializeComponent();
        }

        public void set_target(PyWrapper.IntProperty target)
        {
            this.target = target;
            build_widgets();
        }

        private void build_widgets()
        {
            this.DataContext = this.target;

            TextBlock label = new TextBlock();
            if (this.target == null)
            {
                label.Text = "";
            }
            else
            {
                label.Text = this.target.name;
            }

            TextBox tb = new TextBox();
            Binding binder = new Binding("Value");
            binder.Source = this.target;
            tb.SetBinding(TextBox.TextProperty, binder);

            StackPanel sp = new StackPanel();
            sp.Orientation = Orientation.Horizontal;
            sp.Children.Add(label);
            sp.Children.Add(tb);

            this.Content = sp;
        }
    }
}
