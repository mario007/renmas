﻿using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.ComponentModel;
using System.Windows.Documents;
using System.Diagnostics;

namespace RenmasWPF2
{
    public class Lights : INotifyPropertyChanged
    {
        Renmas renmas;
        string _selected_light = "";
        public event EventHandler LightTypeChanged;
        string _selected_lambda = "";

        public Lights(Renmas renmas)
        {
            this.renmas = renmas;
        }
        
        public string [] LightNames
        {
            get
            {
                string s = this.renmas.GetProp("light", "light_names");
                string[] words = s.Split(',');
                return words;
            }
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

        public float Intesity
        {
            get { 
                if (this._selected_light == "") return 0.0f;
                string [] lam = this.Lambdas;
                int idx = 0;
                for (int i=0; i<lam.Length; i++)
                {
                    if (this._selected_lambda == lam[i]) 
                    {
                        idx = i;
                        break;
                    }
                }
                string s = this.renmas.GetProp("light_params", this.SelectedLight + ",intesity");
                if (s == "") return 0.0f;
                string[] words = s.Split(',');
                return Convert.ToSingle(words[idx]);
            }
            set
            {
                this.renmas.SetProp("light_params", this.SelectedLight + ",intesity", this._selected_lambda + "," + value.ToString());
                this.OnPropertyChanged("Intesity");
            }
        }

        public string SelectedLambda
        {
            get { return this._selected_lambda;  }
            set
            {
                this._selected_lambda = value;
                this.OnPropertyChanged("Intesity");
            }
        }


        public string SelectedLight
        {
            get { return this._selected_light;  }
            set
            {
                // TODO check if light value exist!!!
                string type1 = this.renmas.GetProp("light_type", value);
                string type2 = this.renmas.GetProp("light_type", this._selected_light);
                this._selected_light = value;
                if (type1 != type2)
                {
                    if (this.LightTypeChanged != null)
                        this.LightTypeChanged(this, new EventArgs());
                }
                this.OnPropertyChanged("SelectedLight");
                this.OnPropertyChanged("PositionX");
                this.OnPropertyChanged("PositionY");
                this.OnPropertyChanged("PositionZ");
                this.OnPropertyChanged("Spectrum");
                this.OnPropertyChanged("Intesity");
                this.OnPropertyChanged("IntesityScale");
            }
        }

        public string LightType
        {
            get { return this.renmas.GetProp("light_type", this.SelectedLight);  }
        }

        public float PositionX
        {
            get { return get_position("X"); }
            set
            {
                set_position("X", value);
                this.OnPropertyChanged("PositionX");
            }
        }
        public float PositionY
        {
            get { return get_position("Y"); }
            set
            {
                set_position("Y", value);
                this.OnPropertyChanged("PositionY");
            }
        }
        public float PositionZ
        {
            get { return get_position("Z"); }
            set
            {
                set_position("Z", value);
                this.OnPropertyChanged("PositionZ");
            }
        }

        public float IntesityScale
        {
            get 
            {
                string val = this.renmas.GetProp("light_params", this.SelectedLight + ",intesity_scale");
                if (val == "") return 1.0f;
                return Convert.ToSingle(val); 
            }
            set
            {
                this.renmas.SetProp("light_params", this.SelectedLight + ",intesity_scale", value.ToString());
                this.OnPropertyChanged("IntesityScale");
            }

        }
        public bool Spectral
        {
            get { return System.Convert.ToBoolean(this.renmas.GetProp("misc", "spectral")); }
        }

        public void scale_spectrum(float scaler)
        {
            this.renmas.SetProp("light_spectrum_scale", this.SelectedLight, scaler.ToString());
            this.OnPropertyChanged("Intesity");
        }

        private float get_position(string prop)
        {
            string value = this.renmas.GetProp("light_params", this.SelectedLight + ",position");
            if (value == "") return 0.0f;
            string[] words = value.Split(',');
            if (prop == "X")
            {
                return System.Convert.ToSingle(words[0]);
            }
            else if (prop == "Y")
            {
                return System.Convert.ToSingle(words[1]);
            }
            else if (prop == "Z")
            {
                return System.Convert.ToSingle(words[2]);
            }
            return 0.0f;
        }

        private void set_position(string prop, float value)
        {
            string position = this.renmas.GetProp("light_params", this.SelectedLight + ",position");
            if (position == "") return;
            string[] words = position.Split(',');
            if (prop == "X")
            {
                position = value.ToString() + "," + words[1] + "," + words[2];
            }
            else if (prop == "Y")
            {
                position = words[0] + "," + value.ToString() + "," + words[2];
            }
            else if (prop == "Z")
            {
                position = words[0] + "," + words[1] + "," + value.ToString();
            }
            this.renmas.SetProp("light_params", this.SelectedLight + ",position", position);
        }
        public void Refresh()
        {
            string[] tmp = this.LightNames;
            if (tmp.Length > 0) { this.SelectedLight = tmp[0]; }
            tmp = this.Lambdas;
            if (tmp.Length > 0) { this.SelectedLambda = tmp[0]; }
            this.LightTypeChanged(this, new EventArgs());
            this.OnPropertyChanged("LightNames");
            this.OnPropertyChanged("SelectedLight");
            this.OnPropertyChanged("PositionX");
            this.OnPropertyChanged("PositionY");
            this.OnPropertyChanged("PositionZ");
            this.OnPropertyChanged("Intesity");
            this.OnPropertyChanged("IntesityScale");
            
        }
        public event PropertyChangedEventHandler PropertyChanged;
        private void OnPropertyChanged(string property_name)
        {
            if (PropertyChanged != null)
            {
                PropertyChanged(this, new PropertyChangedEventArgs(property_name));
            }
        }
    }
}
