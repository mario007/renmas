using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.ComponentModel;
using System.Windows.Media;

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
                this.OnPropertyChanged("SelectedLambda");
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
                if (value > 0.0f && value < 1.0f)
                {
                    this.renmas.SetProp("material_params", this._selected_material + "," + this._selected_component + ",reflectance", this._selected_lambda + "," + value.ToString());
                    this.OnPropertyChanged("Reflectance");
                    this.OnPropertyChanged("RGBReflectanceBrush");
                }
            }
        }

        public float Scaler
        {
            get
            {
                string s = this.renmas.GetProp("material_params", this._selected_material + "," + this._selected_component + "," + "scaler");
                if (s == "") return 0.0f;
                return Convert.ToSingle(s);
            }
            set
            {
                if (value > 0.0f)
                {
                    this.renmas.SetProp("material_params", this._selected_material + "," + this._selected_component + ",scaler", value.ToString());
                    this.OnPropertyChanged("Scaler");
                }
            }
        }

        public float Shinines
        {
            get
            {
                string s = this.renmas.GetProp("material_params", this._selected_material + "," + this._selected_component + "," + "shinines");
                if (s == "") return 0.0f;
                return Convert.ToSingle(s);
            }
            set
            {
                if (value > 0.0f)
                {
                    this.renmas.SetProp("material_params", this._selected_material + "," + this._selected_component + ",shinines", value.ToString());
                    this.OnPropertyChanged("Shinines");
                }
            }
        }

        public float Alpha
        {
            get
            {
                string s = this.renmas.GetProp("material_params", this._selected_material + "," + this._selected_component + "," + "alpha");
                if (s == "") return 0.0f;
                return Convert.ToSingle(s);
            }
            set
            {
                if (value > 0.0f)
                {
                    this.renmas.SetProp("material_params", this._selected_material + "," + this._selected_component + ",alpha", value.ToString());
                    this.OnPropertyChanged("Alpha");
                }
            }
        }

        public float Beta
        {
            get
            {
                string s = this.renmas.GetProp("material_params", this._selected_material + "," + this._selected_component + "," + "beta");
                if (s == "") return 0.0f;
                return Convert.ToSingle(s);
            }
            set
            {
                if (value > 0.0f)
                {
                    this.renmas.SetProp("material_params", this._selected_material + "," + this._selected_component + ",beta", value.ToString());
                    this.OnPropertyChanged("Beta");
                }
            }
        }

        public float SimpleIOR
        {
            get
            {
                string s = this.renmas.GetProp("material_params", this._selected_material + "," + this._selected_component + "," + "simple_ior");
                if (s == "") return 0.0f;
                return Convert.ToSingle(s);
            }
            set
            {
                if (value > 0.0f)
                {
                    this.renmas.SetProp("material_params", this._selected_material + "," + this._selected_component + ",simple_ior", value.ToString());
                    this.OnPropertyChanged("SimpleIOR");
                }
            }
        }

        public float Roughness
        {
            get
            {
                string s = this.renmas.GetProp("material_params", this._selected_material + "," + this._selected_component + "," + "roughness");
                if (s == "") return 0.0f;
                return Convert.ToSingle(s);
            }
            set
            {
                if (value > 0.0f)
                {
                    this.renmas.SetProp("material_params", this._selected_material + "," + this._selected_component + ",roughness", value.ToString());
                    this.OnPropertyChanged("Roughness");
                }
            }
        }
        public SolidColorBrush RGBReflectanceBrush
        {
            get
            {
                if (this._selected_component == "") return new SolidColorBrush(Color.FromRgb(0,0,0));
                string s = this.renmas.GetProp("material_params", this._selected_material + "," + this._selected_component + "," + "rgb_reflectance");
                if (s == "") return new SolidColorBrush(Color.FromRgb(0, 0, 0));
                string[] rgb = s.Split(',');
                byte r = Convert.ToByte(rgb[0]);
                byte g = Convert.ToByte(rgb[1]);
                byte b = Convert.ToByte(rgb[2]);
                return new SolidColorBrush(Color.FromRgb(r, g, b));
            }
        }

        public string get_rgb_reflectance()
        {
            if (this._selected_component == "") return "0,0,0";
            string s = this.renmas.GetProp("material_params", this._selected_material + "," + this._selected_component + "," + "rgb_reflectance");
            if (s == "") return "0,0,0";
            return s;
        }

        public void set_rgb_reflectance(string rgb)
        {
            if (this._selected_component == "") return;
            this.renmas.SetProp("material_params", this._selected_material + "," + this._selected_component + ",rgb_reflectance", rgb);
            this.OnPropertyChanged("Reflectance");
            this.OnPropertyChanged("RGBReflectanceBrush");
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
            this.OnPropertyChanged("Lambdas");
            this.SelectedLambda = this.Lambdas[0];
            this.OnPropertyChanged("Scaler");
            this.OnPropertyChanged("RGBReflectanceBrush");
    
        }
    }
}
