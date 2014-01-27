using System;
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

namespace RenEditors
{
    /// <summary>
    /// Interaction logic for FloatEditor.xaml
    /// </summary>
    public partial class FloatEditor : UserControl
    {
        FloatProperty target;
        uint tblock_width = 70;
        uint tbox_width = 70;

        public FloatEditor()
        {
            InitializeComponent();
        }

        public void set_target(FloatProperty target)
        {
            this.target = target;
            build_widgets();
        }

        private void build_widgets()
        {
            this.DataContext = this.target;

            TextBlock label = new TextBlock();
            label.Width = this.tblock_width;
            if (this.target == null)
            {
                label.Text = "";
            }
            else
            {
                label.Text = this.target.name;
            }

            TextBox tb = new TextBox();
            tb.Width = this.tbox_width;
            Binding binder = new Binding("Value");
            binder.Source = this.target;
            tb.SetBinding(TextBox.TextProperty, binder);

            StackPanel sp = new StackPanel();
            sp.Margin = new Thickness(2);
            sp.Orientation = Orientation.Horizontal;
            sp.Children.Add(label);
            sp.Children.Add(tb);

            this.Content = sp;
        }

    }
}
