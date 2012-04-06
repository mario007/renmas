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
    /// Interaction logic for MaterialEditor.xaml
    /// </summary>
    public partial class MaterialEditor : UserControl
    {
        Materials materials;

        public MaterialEditor(Materials materials)
        {
            InitializeComponent();
            this.materials = materials;
            this.build_gui();
            this.materials.MaterialComponentChanged += new EventHandler(materials_MaterialComponentChanged);
        }

        void materials_MaterialComponentChanged(object sender, EventArgs e)
        {
            this.build_gui();
            Expander exp = (Expander)this.Content;
            exp.IsExpanded = true;
        }

        private void build_gui()
        {
            this.DataContext = this.materials;

            StackPanel sp_materials = this.build_combo("Materials: ", "MaterialNames", "SelectedMaterial");
            StackPanel sp_components = this.build_combo("Components: ", "Components", "SelectedComponent");

            StackPanel all = new StackPanel();
            all.Children.Add(sp_materials);
            all.Children.Add(sp_components);

            if (this.materials.ComponentType == "Lambertian")
            {

                this.build_lambertian(all);

            }
            else if (this.materials.ComponentType == "PhongSpecular")
            {

                this.build_phong(all);
            }
            else
            {
            }

            Expander expander = new Expander();
            expander.Header = " Materials";
            expander.Foreground = Brushes.White;
            expander.Content = all;
            this.Content = expander;
        }

        private void build_lambertian(StackPanel sp)
        {
            TextBlock comp_type = new TextBlock();
            comp_type.Text = " ComponentType: " + this.materials.ComponentType;
            comp_type.Width = 200;
            comp_type.Height = 20;

            TextBlock tb_wavelength = new TextBlock();
            tb_wavelength.Text = " Wavelength: ";
            tb_wavelength.Width = 70;
            tb_wavelength.TextAlignment = TextAlignment.Right;
            tb_wavelength.VerticalAlignment = System.Windows.VerticalAlignment.Center;
            ComboBox cb_lambdas = new ComboBox();
            Binding bind_lambdas = new Binding("Lambdas");
            cb_lambdas.SetBinding(ComboBox.ItemsSourceProperty, bind_lambdas);
            Binding bind_sel_lam = new Binding("SelectedLambda");
            cb_lambdas.SetBinding(ComboBox.SelectedItemProperty, bind_sel_lam);
            cb_lambdas.Foreground = Brushes.White;
            cb_lambdas.Width = 80;
            StackPanel sp_wave = new StackPanel();
            sp_wave.Orientation = Orientation.Horizontal;
            sp_wave.Height = 25;
            sp_wave.Children.Add(tb_wavelength);
            sp_wave.Children.Add(cb_lambdas);

            sp.Children.Add(comp_type);
            sp.Children.Add(sp_wave);

            StackPanel refl = this.build_lbltxt("Reflectance:", "Reflectance");
            sp.Children.Add(refl);

        }

        private void build_phong(StackPanel sp)
        {
            TextBlock comp_type = new TextBlock();
            comp_type.Text = " ComponentType: " + this.materials.ComponentType;
            comp_type.Width = 200;
            comp_type.Height = 20;
            sp.Children.Add(comp_type);
        }

        private StackPanel build_combo(string label_name, string prop_names, string selected_prop)
        {
            TextBlock tb_materials = new TextBlock();
            tb_materials.Text = label_name;
            tb_materials.TextAlignment = TextAlignment.Right;
            tb_materials.Width = 80;
            tb_materials.Height = 20;

            ComboBox cb_materials = new ComboBox();
            cb_materials.Width = 190;
            cb_materials.Height = 20;
            cb_materials.Foreground = Brushes.White;
            Binding bind = new Binding(prop_names);
            cb_materials.SetBinding(ComboBox.ItemsSourceProperty, bind);

            Binding bind2 = new Binding(selected_prop);
            cb_materials.SetBinding(ComboBox.SelectedItemProperty, bind2);

            StackPanel sp_materials = new StackPanel();
            sp_materials.Orientation = Orientation.Horizontal;
            sp_materials.Height = 25;
            sp_materials.Children.Add(tb_materials);
            sp_materials.Children.Add(cb_materials);
            return sp_materials;
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
            tb.SetBinding(TextBox.TextProperty, binder);
            sp.Height = 25;
            return sp;
        }
    }
}
