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
    /// Interaction logic for ToneMappingEditor.xaml
    /// </summary>
    public partial class ToneMappingEditor : UserControl
    {
        PyWrapper.Renmas renmas;

        public ToneMappingEditor(PyWrapper.Renmas renmas)
        {
            InitializeComponent();
            this.renmas = renmas;
            build_widgets();
        }

        private void build_widgets()
        {
            StackPanel sp = new StackPanel();
            sp.Orientation = Orientation.Vertical;

            foreach (PyWrapper.RenmasProperty prop in this.renmas.ToneProps)
            {
                UserControl editor = Utils.build_editor(prop);
                sp.Children.Add(editor);
            }
            Button btn = new Button();
            btn.Content = "Tone map";
            sp.Children.Add(btn);
            this.Content = sp;
        }
    }
}
