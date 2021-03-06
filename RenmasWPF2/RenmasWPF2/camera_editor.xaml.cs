﻿using System;
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
    /// Interaction logic for camera_editor.xaml
    /// </summary>
    public partial class Camera_editor : UserControl
    {
        Camera camera;
        public Camera_editor(Camera camera)
        {
            InitializeComponent();
            //this.camera = camera;
            this.camera = camera;
            this.build_gui();
        }

        private void build_gui()
        {
            this.DataContext = camera;

            StackPanel sp_x = this.build_lbltxt("  X: ", "Eye_x");
            StackPanel sp_y = this.build_lbltxt("  Y: ", "Eye_y");
            StackPanel sp_z = this.build_lbltxt("  Z: ", "Eye_z");
            StackPanel row1 = build_row(" Eye :      ", sp_x, sp_y, sp_z);
            StackPanel look_x = this.build_lbltxt("  X: ", "Lookat_x");
            StackPanel look_y = this.build_lbltxt("  Y: ", "Lookat_y");
            StackPanel loop_z = this.build_lbltxt("  Z: ", "Lookat_z");
            StackPanel row2 = build_row(" LookAt : ", look_x, look_y, loop_z);

            StackPanel sp = new StackPanel();
            sp.Children.Add(row1);
            sp.Children.Add(row2);

            // Distance 
            StackPanel dist = this.build_lbltxt(" Distance: ", "Distance");

            sp.Children.Add(dist);

            Expander expand = new Expander();
            expand.Header = "Camera";
            expand.Foreground = Brushes.White;
            expand.Content = sp;
            this.Content = expand;
        }

        private StackPanel build_row(string name, StackPanel sp1, StackPanel sp2, StackPanel sp3)
        {
            StackPanel sp = new StackPanel();
            sp.Orientation = Orientation.Horizontal;
            TextBlock tb = new TextBlock();
            tb.Text = name;
            tb.VerticalAlignment = System.Windows.VerticalAlignment.Center;
            tb.Width = 50;
            sp.Children.Add(tb);
            sp.Children.Add(sp1);
            sp.Children.Add(sp2);
            sp.Children.Add(sp3);
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
            binder.Source = camera;
            tb.SetBinding(TextBox.TextProperty, binder);
            sp.Height = 25;
            return sp;
        }
    }
}
