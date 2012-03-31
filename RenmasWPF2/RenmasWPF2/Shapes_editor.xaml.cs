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
    /// Interaction logic for Shapes_editor.xaml
    /// </summary>
    public partial class Shapes_editor : UserControl
    {
        Shapes shapes;
        public Shapes_editor(Shapes shapes)
        {
            InitializeComponent();
            this.shapes = shapes;
            this.build_gui();
        }

        private void build_gui()
        {
            this.DataContext = shapes;

            TextBlock tb_shapes = new TextBlock();
            tb_shapes.Text = " Shapes: ";
            tb_shapes.Width = 60;
            tb_shapes.Height = 20;

            ComboBox cb = new ComboBox();
            cb.Width = 210;
            cb.Height = 20;
            cb.Foreground = Brushes.White;
            Binding bind = new Binding("ShapeNames");
            cb.SetBinding(ComboBox.ItemsSourceProperty, bind);

            Binding bind2 = new Binding("SelectedShape");
            cb.SetBinding(ComboBox.SelectedItemProperty, bind2);

            StackPanel sp = new StackPanel();
            sp.Orientation = Orientation.Horizontal;
            sp.Height = 25;
            sp.Children.Add(tb_shapes);
            sp.Children.Add(cb);

            TextBlock tb_materials = new TextBlock();
            tb_materials.Text = " Materials: ";
            tb_materials.Width = 60;
            ComboBox cb_mat = new ComboBox();
            cb_mat.Width = 210;
            cb_mat.Height = 20;
            cb_mat.Foreground = Brushes.White;

            Binding bind3 = new Binding("MaterialNames");
            cb_mat.SetBinding(ComboBox.ItemsSourceProperty, bind3);
            Binding bind4 = new Binding("SelectedMaterial");
            cb_mat.SetBinding(ComboBox.SelectedItemProperty, bind4);

            StackPanel sp_mat = new StackPanel();
            sp_mat.Orientation = Orientation.Horizontal;
            sp_mat.Children.Add(tb_materials);
            sp_mat.Children.Add(cb_mat);

            StackPanel all = new StackPanel();
            all.Children.Add(sp);
            all.Children.Add(sp_mat);

            Expander expander = new Expander();
            expander.Header = " Shapes";
            expander.Foreground = Brushes.White;
            expander.Content = all;
            this.Content = expander;
        }
    }
}
