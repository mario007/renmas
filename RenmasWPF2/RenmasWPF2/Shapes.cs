using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.ComponentModel;

namespace RenmasWPF2
{
    public class Shapes : INotifyPropertyChanged
    {
        Renmas renmas;
        string _selected_shape = "";
        public Shapes(Renmas renmas)
        {
            this.renmas = renmas;
        }

        public string [] ShapeNames
        {
            get
            {
                string s = this.renmas.GetProp("misc", "shapes");
                string[] words = s.Split(',');
                return words;
            }
        }

        public string[] MaterialNames
        {
            get
            {
                string s = this.renmas.GetProp("misc", "materials");
                string[] words = s.Split(',');
                return words;
            }
        }

        public string SelectedShape
        {
            get { return this._selected_shape;  }
            set
            {
                this._selected_shape = value;
                this.OnPropertyChanged("SelectedShape");
                this.OnPropertyChanged("SelectedMaterial");
            }
        }
        public string SelectedMaterial
        {
            get 
            {
                return this.renmas.GetProp("material_name", this._selected_shape);
            }
            set
            {
                this.renmas.SetProp("material_assign", this._selected_shape, value);
                this.OnPropertyChanged("SelectedMaterial");
            }
        }

        public event PropertyChangedEventHandler PropertyChanged;
        private void OnPropertyChanged(string property_name)
        {
            if (PropertyChanged != null)
            {
                PropertyChanged(this, new PropertyChangedEventArgs(property_name));
            }
        }

        public void Refresh()
        {
            string[] tmp = this.ShapeNames;
            if (tmp.Length > 0) { 
                this.SelectedShape = tmp[0];
            }

            this.OnPropertyChanged("MaterialNames");
            this.OnPropertyChanged("ShapeNames");
            this.OnPropertyChanged("SelectedShape");
            this.OnPropertyChanged("SelectedMaterial");

        }
       
    }
}
