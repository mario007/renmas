using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.ComponentModel;
using System.Windows.Media;
using System.Windows;

namespace RenmasWPF2
{
    public class Spectrum : INotifyPropertyChanged
    {
        Byte _r, _g, _b;
        SolidColorBrush _brush;
        public Spectrum(Byte R, Byte G, Byte B)
        {
            this._r = R;
            this._g = G;
            this._b = B;
            Color c = Color.FromRgb(R, G, B);
            this._brush = new SolidColorBrush(c);
        }

        public Byte R
        {
            get
            {
                return this._r;
            }
            set
            {
                this._r = value;
                this.OnPropertyChanged("R");
                this._brush = new SolidColorBrush(Color.FromRgb(this._r, this._g, this._b));
                this.OnPropertyChanged("RainbowValue");
                this.OnPropertyChanged("SpectrumBrush");
            }
        }
        public Byte G
        {
            get
            {
                return this._g;
            }
            set
            {
                this._g = value;
                this.OnPropertyChanged("G");
                this._brush = new SolidColorBrush(Color.FromRgb(this._r, this._g, this._b));
                this.OnPropertyChanged("RainbowValue");
                this.OnPropertyChanged("SpectrumBrush");
            }
        }

        public Byte B
        {
            get
            {
                return this._b;
            }
            set
            {
                this._b = value;
                this.OnPropertyChanged("B");
                this._brush = new SolidColorBrush(Color.FromRgb(this._r, this._g, this._b));
                this.OnPropertyChanged("RainbowValue");
                this.OnPropertyChanged("SpectrumBrush");
            }
        }

        public SolidColorBrush SpectrumBrush
        {
            get
            {
                return this._brush;
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

        // Return a rainbow brush.
        // The calling code should dispose of the brush.
        public LinearGradientBrush rainbow_brush(Point point1, Point point2)
        {
            LinearGradientBrush rainbow_brush = new LinearGradientBrush();
            rainbow_brush.StartPoint = point1;
            rainbow_brush.EndPoint = point2;
            rainbow_brush.GradientStops.Add(new GradientStop(Colors.Red, 0.0));
            rainbow_brush.GradientStops.Add(new GradientStop(Colors.Yellow, 0.16666));
            rainbow_brush.GradientStops.Add(new GradientStop(Colors.Lime, 0.3333));
            rainbow_brush.GradientStops.Add(new GradientStop(Colors.Aqua, 0.5));
            rainbow_brush.GradientStops.Add(new GradientStop(Colors.Blue, 0.66666));
            rainbow_brush.GradientStops.Add(new GradientStop(Colors.Fuchsia, 0.833333));
            rainbow_brush.GradientStops.Add(new GradientStop(Colors.Red, 1.0));

            return rainbow_brush;
        }

        public float RainbowValue
        {
            get
            {
                return this.from_rgb_to_rainbow_value();
            }
            set
            {
                this.from_rainbow_to_rgb(value);
                this._brush = new SolidColorBrush(Color.FromRgb(this._r, this._g, this._b));
                this.OnPropertyChanged("RainbowValue");
                this.OnPropertyChanged("R");
                this.OnPropertyChanged("G");
                this.OnPropertyChanged("B");
                this.OnPropertyChanged("SpectrumBrush");
            }
        }
        // Map a color to a rainbow number between 0 and 1 on the
        // Red-Yellow-Green-Aqua-Blue-Fuchsia-Red rainbow.
        private float from_rgb_to_rainbow_value()
        {
            // See which color is weakest.
            int r = (int)this._r;
            int g = (int)this._g;
            int b = (int)this._b;

            if ((r <= g) && (r <= b))
            {
                // Red is weakest. It's mostly blue and green.
                g -= r;
                b -= r;
                if (g + b == 0) return 0;
                return (2 / 6f * g + 4 / 6f * b) / (g + b);
            }
            else if ((g <= r) && (g <= b))
            {
                // Green is weakest. It's mostly red and blue.
                r -= g;
                b -= g;
                if (r + b == 0) return 0;
                return (1f * r + 4 / 6f * b) / (r + b);
            }
            else
            {
                // Blue is weakest. It's mostly red and green.
                r -= b;
                g -= b;
                if (r + g == 0) return 0;
                return (0f * r + 2 / 6f * g) / (r + g);
            }
        }

        // Map a rainbow number between 0 and 1 to a color on the
        // Red-Yellow-Green-Aqua-Blue-Fuchsia-Red rainbow.
        public void from_rainbow_to_rgb(float number)
        {
            byte r = 0, g = 0, b = 0;
            if (number < 1 / 6f)
            {
                // Mostly red with some green.
                r = 255;
                g = (byte)(r * (number - 0) / (2 / 6f - number));
                this._r = r;
                this._g = g;
            }
            else if (number < 2 / 6f)
            {
                // Mostly green with some red.
                g = 255;
                r = (byte)(g * (2 / 6f - number) / (number - 0));
                this._g = g;
                this._r = r;
            }
            else if (number < 3 / 6f)
            {
                // Mostly green with some blue.
                g = 255;
                b = (byte)(g * (2 / 6f - number) / (number - 4 / 6f));
                this._g = g;
                this._b = b;
            }
            else if (number < 4 / 6f)
            {
                // Mostly blue with some green.
                b = 255;
                g = (byte)(b * (number - 4 / 6f) / (2 / 6f - number));
                this._b = b;
                this._g = g;
            }
            else if (number < 5 / 6f)
            {
                // Mostly blue with some red.
                b = 255;
                r = (byte)(b * (4 / 6f - number) / (number - 1f));
                this._b = b;
                this._r = r;
            }
            else
            {
                // Mostly red with some blue.
                r = 255;
                b = (byte)(r * (number - 1f) / (4 / 6f - number));
                this._r = r;
                this._b = b;
            }
        }

    }
}
