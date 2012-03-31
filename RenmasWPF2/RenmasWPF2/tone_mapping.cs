using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.ComponentModel;

namespace RenmasWPF2
{
    public class ToneMappingOperators : INotifyPropertyChanged
    {
        Renmas renmas;
        public event EventHandler OperatorTypeChanged;

        public ToneMappingOperators(Renmas renmas)
        {
            this.renmas = renmas;
        }

        public string[] OperatorNames
        {
            get
            {
                string s = this.renmas.GetProp("misc", "tone_mapping_operators");
                string[] words = s.Split(',');
                return words;
            }
        }

        public float ReinhardSceneKey
        {
            get
            {
                string selected =  this.renmas.GetProp("misc", "selected_operator");
                if (selected == "Reinhard")
                {
                    return System.Convert.ToSingle(this.renmas.GetProp("ReinhardOperator", "scene_key"));
                }
                return 0.0f;
            }
            set
            {
                string selected = this.renmas.GetProp("misc", "selected_operator");
                if (selected == "Reinhard")
                {
                    this.renmas.SetProp("ReinhardOperator", "scene_key", value.ToString());
                    this._refresh_property("ReinhardSceneKey");
                }
            }
        }

        public float ReinhardSaturation
        {
            get
            {
                string selected = this.renmas.GetProp("misc", "selected_operator");
                if (selected == "Reinhard")
                {
                    return System.Convert.ToSingle(this.renmas.GetProp("ReinhardOperator", "saturation"));
                }
                return 0.0f;
            }
            set
            {
                string selected = this.renmas.GetProp("misc", "selected_operator");
                if (selected == "Reinhard")
                {
                    this.renmas.SetProp("ReinhardOperator", "saturation", value.ToString());
                    this._refresh_property("ReinhardSaturation");
                }
            }
        }

        public float PhotoreceptorContrast
        {
            get
            {
                string selected = this.renmas.GetProp("misc", "selected_operator");
                if (selected == "Photoreceptor")
                {
                    return System.Convert.ToSingle(this.renmas.GetProp("PhotoreceptorOperator", "contrast"));
                }
                return 0.0f;
            }
            set
            {
                string selected = this.renmas.GetProp("misc", "selected_operator");
                if (selected == "Photoreceptor")
                {
                    this.renmas.SetProp("PhotoreceptorOperator", "contrast", value.ToString());
                    this._refresh_property("PhotoreceptorContrast");
                }
            }
        }

        public float PhotoreceptorAdaptation
        {
            get
            {
                string selected = this.renmas.GetProp("misc", "selected_operator");
                if (selected == "Photoreceptor")
                {
                    return System.Convert.ToSingle(this.renmas.GetProp("PhotoreceptorOperator", "adaptation"));
                }
                return 0.0f;
            }
            set
            {
                string selected = this.renmas.GetProp("misc", "selected_operator");
                if (selected == "Photoreceptor")
                {
                    this.renmas.SetProp("PhotoreceptorOperator", "adaptation", value.ToString());
                    this._refresh_property("PhotoreceptorAdaptation");
                }
            }
        }

        public float PhotoreceptorColornes
        {
            get
            {
                string selected = this.renmas.GetProp("misc", "selected_operator");
                if (selected == "Photoreceptor")
                {
                    return System.Convert.ToSingle(this.renmas.GetProp("PhotoreceptorOperator", "colornes"));
                }
                return 0.0f;
            }
            set
            {
                string selected = this.renmas.GetProp("misc", "selected_operator");
                if (selected == "Photoreceptor")
                {
                    this.renmas.SetProp("PhotoreceptorOperator", "colornes", value.ToString());
                    this._refresh_property("PhotoreceptorColornes");
                }
            }
        }

        public float PhotoreceptorLightnes
        {
            get
            {
                string selected = this.renmas.GetProp("misc", "selected_operator");
                if (selected == "Photoreceptor")
                {
                    return System.Convert.ToSingle(this.renmas.GetProp("PhotoreceptorOperator", "lightnes"));
                }
                return 0.0f;
            }
            set
            {
                string selected = this.renmas.GetProp("misc", "selected_operator");
                if (selected == "Photoreceptor")
                {
                    this.renmas.SetProp("PhotoreceptorOperator", "lightnes", value.ToString());
                    this._refresh_property("PhotoreceptorLightnes");
                }
            }
        }

        private void _refresh_property(string name)
        {
            this.renmas.ToneMap();
            this.renmas.RefreshImage();
            this.OnPropertyChanged(name);
        }

        public string SelectedOperator
        {
            get 
            { 
                return this.renmas.GetProp("misc", "selected_operator");
            }
            set
            {
                string type1 = this.renmas.GetProp("misc", "selected_operator");
                this.renmas.SetProp("misc", "selected_operator", value);
                if (type1 != value)
                {
                    if (this.OperatorTypeChanged != null)
                        this.OperatorTypeChanged(this, new EventArgs());
                }
                this.renmas.RefreshImage();
                this.OnPropertyChanged("SelectedOperator");
            }
        }

        public bool ToneMapping
        {
            get
            {
                return System.Convert.ToBoolean(this.renmas.GetProp("misc", "tone_mapping"));
            }
            set
            {
                this.renmas.SetProp("misc", "tone_mapping", value.ToString());
                this.renmas.RefreshImage();
                this.OnPropertyChanged("ToneMapping");
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
            this.OnPropertyChanged("SelectedOperator");
        }
    }
}
