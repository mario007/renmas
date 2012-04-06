using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.ComponentModel;

namespace RenmasWPF2
{
    public class Materials : INotifyPropertyChanged
    {
        Renmas renmas;
        string _selected_material = "";
        string _selected_component = "";
        string _selected_lambda = "";

        public event EventHandler MaterialComponentChanged;

        public Materials(Renmas renmas)
        {
            this.renmas = renmas;
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

        public string SelectedMaterial
        {
            get { return this._selected_material; }
            set
            {
                this._selected_material = value;
                this.OnPropertyChanged("Components");
                string[] tmp2 = this.Components;
                if (tmp2.Length > 0)
                {
                    this._selected_component = tmp2[0];
                }
                this.OnPropertyChanged("SelectedMaterial");
                this.OnPropertyChanged("SelectedComponent");
                if (this.MaterialComponentChanged != null)
                    this.MaterialComponentChanged(this, new EventArgs());
            }
        }

        public bool Spectral
        {
            get { return System.Convert.ToBoolean(this.renmas.GetProp("misc", "spectral")); }
        }

        public string[] Lambdas
        {
            get
            {
                if (this.Spectral == false)
                {
                    return "RED,GREEN,BLUE".Split(',');
                }
                else
                {
                    string s = this.renmas.GetProp("misc", "lambdas");
                    string[] words = s.Split(',');
                    return words;
                }
            }
        }

        public string SelectedLambda
        {
            get { return this._selected_lambda; }
            set
            {
                this._selected_lambda = value;
                this.OnPropertyChanged("Reflectance");
            }
        }

        public float Reflectance
        {
            get
            {
                if (this._selected_component == "") return 0.0f;
                string[] lam = this.Lambdas;
                int idx = 0;
                for (int i = 0; i < lam.Length; i++)
                {
                    if (this._selected_lambda == lam[i])
                    {
                        idx = i;
                        break;
                    }
                }
                string s = this.renmas.GetProp("material_params", this._selected_material + "," + this._selected_component + "," + "reflectance");
                if (s == "") return 0.0f;
                string[] words = s.Split(',');
                return Convert.ToSingle(words[idx]);
            }
            set
            {
                this.renmas.SetProp("material_params", this._selected_material + "," + this._selected_component + ",reflectance"  , this._selected_lambda + "," + value.ToString());
                this.OnPropertyChanged("Reflectance");
            }
        }

        public string[] Components
        {
            get 
            {
                string comps = this.renmas.GetProp("material_components", this._selected_material);
                return comps.Split(',');
            }
        }

        public string ComponentType
        {
            get
            {
                
                return this.renmas.GetProp("component_type", this._selected_material + "," + this._selected_component);
            }
        }

        public string SelectedComponent
        {
            get
            {
                return this._selected_component;
            }
            set
            {
                this._selected_component = value;
                this.OnPropertyChanged("SelectedComponent");
                if (this.MaterialComponentChanged != null)
                    this.MaterialComponentChanged(this, new EventArgs());
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
            string[] tmp = this.MaterialNames;
            if (tmp.Length > 0)
            {
                this._selected_material = tmp[0];
                string[] tmp2 = this.Components;
                if (tmp2.Length > 0)
                {
                    this._selected_component = tmp2[0];
                }
            }
            
            this.OnPropertyChanged("MaterialNames");
            this.OnPropertyChanged("Components");
            this.OnPropertyChanged("SelectedMaterial");
            this.OnPropertyChanged("SelectedComponent");
        }
    }
}
