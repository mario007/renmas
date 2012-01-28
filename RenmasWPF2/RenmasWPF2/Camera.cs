using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.ComponentModel;

namespace RenmasWPF2
{
    public class Camera : INotifyPropertyChanged
    {
        Renmas renmas;
        public Camera(Renmas renmas)
        {
            this.renmas = renmas;
        }
        private float get_value(string name, string prop)
        {
            string value = this.renmas.GetProp("camera", name);
            string[] words = value.Split(',');
            if (prop == "X") {
                return System.Convert.ToSingle(words[0]);
            }
            else if (prop == "Y") {
                return System.Convert.ToSingle(words[1]);
            }
            else if (prop == "Z") {
                return System.Convert.ToSingle(words[2]);
            }
            return 0.0f;
        }
        private void set_value(string name, string prop, float value)
        {
            string cam_eye = this.renmas.GetProp("camera", name);
            string[] words = cam_eye.Split(',');
            if (prop == "X") {
                cam_eye = value.ToString() + "," + words[1] + "," + words[2];
            }
            else if (prop == "Y") {
                cam_eye = words[0] + "," + value.ToString() + "," + words[2];
            }
            else if (prop == "Z") {
                cam_eye = words[0] + "," + words[1] + "," + value.ToString();
            }
            this.renmas.SetProp("camera", name, cam_eye);
        }
        public float Eye_x
        {
            get { return get_value("eye", "X"); }
            set {
                set_value("eye", "X", value);
                this.OnPropertyChanged("Eye_x");
            }
        }
        public float Eye_y
        {
            get { return get_value("eye", "Y"); }
            set {
                set_value("eye", "Y", value);
                this.OnPropertyChanged("Eye_y");
            }
        }
        public float Eye_z
        {
            get { return get_value("eye", "Z"); }
            set {
                set_value("eye", "Z", value);
                this.OnPropertyChanged("Eye_z");
            }
        }

        public float Lookat_x
        {
            get { return get_value("lookat", "X"); }
            set {
                set_value("lookat", "X", value);
                this.OnPropertyChanged("Lookat_x");
            }
        }
        public float Lookat_y
        {
            get { return get_value("lookat", "Y"); }
            set
            {
                set_value("lookat", "Y", value);
                this.OnPropertyChanged("Lookat_y");
            }
        }
        public float Lookat_z
        {
            get { return get_value("lookat", "Z"); }
            set
            {
                set_value("lookat", "Z", value);
                this.OnPropertyChanged("Lookat_z");
            }
        }
        public float Distance
        {
            get { return System.Convert.ToSingle(renmas.GetProp("camera", "distance")); }
            set { 
                this.renmas.SetProp("camera", "distance", value.ToString());
                this.OnPropertyChanged("Distance");
            }
        }
        public void Refresh()
        {
            this.OnPropertyChanged("Eye_x");
            this.OnPropertyChanged("Eye_y");
            this.OnPropertyChanged("Eye_z");
            this.OnPropertyChanged("Lookat_x");
            this.OnPropertyChanged("Lookat_y");
            this.OnPropertyChanged("Lookat_z");
            this.OnPropertyChanged("Distance");
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
