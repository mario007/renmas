using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.ComponentModel;

namespace RenmasWPF2
{
    public class Options : INotifyPropertyChanged
    {
        Renmas renmas;
        public Options(Renmas renmas)
        {
            this.renmas = renmas;
        }

        public uint Threads
        {
            get { return System.Convert.ToUInt32(this.renmas.GetProp("misc", "threads")); }
            set
            {
                this.renmas.SetProp("misc", "threads", value.ToString());
                this.OnPropertyChanged("Threads");
            }
        }
        public uint Spp
        {
            get { return System.Convert.ToUInt32(this.renmas.GetProp("misc", "spp")); }
            set
            {
                this.renmas.SetProp("misc", "spp", value.ToString());
                this.OnPropertyChanged("Spp");
            }
        }
        public float PixelSize
        {
            get { return System.Convert.ToSingle(this.renmas.GetProp("misc", "pixel_size")); }
            set
            {
                this.renmas.SetProp("misc", "pixel_size", value.ToString());
                this.OnPropertyChanged("PixelSize");
            }
        }

        public bool Asm
        {
            get { return System.Convert.ToBoolean(this.renmas.GetProp("misc", "asm")); }
            set
            {
                this.renmas.SetProp("misc", "asm", value.ToString());
                this.OnPropertyChanged("Asm");
            }
        }
        public bool Spectral
        {
            get { return System.Convert.ToBoolean(this.renmas.GetProp("misc", "spectral")); }
            set
            {
                this.renmas.SetProp("misc", "spectral", value.ToString());
                this.OnPropertyChanged("Spectral");
            }
        }
        public uint Width
        {
            get { return get_value("Width");  }
            set
            {
                set_value("Width", value);
                this.OnPropertyChanged("Width");
            }
        }
        public uint Height
        {
            get { return get_value("Height"); }
            set
            {
                set_value("Height", value);
                this.OnPropertyChanged("Height");
            }
        }
        private uint get_value(string prop)
        {
            string value = this.renmas.GetProp("misc", "resolution");
            string[] words = value.Split(',');
            if (prop == "Width")
            {
                return System.Convert.ToUInt32(words[0]);
            }
            else if (prop == "Height")
            {
                return System.Convert.ToUInt32(words[1]);
            }
            return 200;
        }

        private void set_value(string prop, uint value)
        {
            string resolution = this.renmas.GetProp("misc", "resolution");
            string[] words = resolution.Split(',');
            if (prop == "Width")
            {
                resolution = value.ToString() + "," + words[1];
            }
            else if (prop == "Height")
            {
                resolution = words[0] + "," + value.ToString();
            }
            this.renmas.SetProp("misc", "resolution", resolution);
        }
        public void Refresh()
        {
            this.OnPropertyChanged("Threads");
            this.OnPropertyChanged("Spp");
            this.OnPropertyChanged("PixelSize");
            this.OnPropertyChanged("Asm");
            this.OnPropertyChanged("Spectral");
            this.OnPropertyChanged("Width");
            this.OnPropertyChanged("Height");
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
