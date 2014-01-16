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
    /// Interaction logic for TmoEditor.xaml
    /// </summary>
    public partial class TmoEditor : UserControl
    {
        public Tmo target = null;

        public TmoEditor()
        {
            InitializeComponent();
        }

        public void set_target(Tmo target)
        {
            this.target = target;
            build_widgets();
        }

        private void build_widgets()
        {
            List<BaseProperty> props = this.target.get_props();

            StackPanel sp = new StackPanel();
            sp.Orientation = Orientation.Vertical;

            foreach (BaseProperty prop in props)
            {
                UserControl editor = this.build_editor(prop);
                sp.Children.Add(editor);
            }

            this.Content = sp;
        }

        public UserControl build_editor(BaseProperty property)
        {
            Type t = property.GetType();
            if (t == typeof(FloatProperty))
            {
                FloatEditor ed = new FloatEditor();
                ed.set_target((FloatProperty)property);
                return ed;
            }
            else
            {
                //TODO -- better message
                string msg = "Unknown type";
                throw new Exception(msg);
            }
        }

    }
}
