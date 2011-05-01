#include<windows.h>
#include <gdiplus.h>
#include <Python.h>

using namespace Gdiplus;

typedef unsigned int uint32;
typedef unsigned long long uint64;


#ifdef BIT64
typedef uint64 uint;
#else
typedef uint32 uint;
#endif

/* Macro used to pack RGBA color
*/
#define  SRGB(r, g, b) (255 << 24) | ((b & 0xFF) << 16) | ((g & 0xFF) << 8) | (r & 0xFF)
#define  SRGBA(r, g, b, a) ((a & 0xFF) << 24) | ((b & 0xFF) << 16) | ((g & 0xFF) << 8) | (r & 0xFF)
#define  KRGB(r, g, b) (255 << 24) | ((r & 0xFF) << 16) | ((g & 0xFF) << 8) | (b & 0xFF)
#define  KRGBA(r, g, b, a) ((a & 0xFF) << 24) | ((r & 0xFF) << 16) | ((g & 0xFF) << 8) | (b & 0xFF)



// 
int GetEncoderClsid(const WCHAR* format, CLSID* pClsid)
{
   UINT  num = 0;          // number of image encoders
   UINT  size = 0;         // size of the image encoder array in bytes

   ImageCodecInfo* pImageCodecInfo = NULL;

   GetImageEncodersSize(&num, &size);
   if(size == 0)
      return -1;  // Failure

   pImageCodecInfo = (ImageCodecInfo*)(malloc(size));
   if(pImageCodecInfo == NULL)
      return -1;  // Failure

   GetImageEncoders(num, size, pImageCodecInfo);

   for(UINT j = 0; j < num; ++j)
   {
      if( wcscmp(pImageCodecInfo[j].MimeType, format) == 0 )
      {
         *pClsid = pImageCodecInfo[j].Clsid;
         free(pImageCodecInfo);
         return j;  // Success
      }    
   }

   free(pImageCodecInfo);
   return -1;  // Failure
}

bool SaveImageToPng(char *name, void *address, int width, int height)
{
	Bitmap *image = new Bitmap(width, height, PixelFormat32bppARGB);
	unsigned int *dest = (unsigned int *) address;
	Color pixCol;
	
	unsigned int pixel;

	BYTE a = 0xFF;
	BYTE r = 0x80;
	BYTE g = 0x80;
	BYTE b = 0xFF;

	ARGB argb;
	for(int y=0; y<height; y++)
	{
		for(int x=0; x<width; x++)
		{
			pixel = *dest;
			a =  (BYTE)((pixel >> 24) & 0xFF);
			b = (BYTE)(pixel & 0xFF);
			g = (BYTE)((pixel >> 8)  & 0xFF);
			r = (BYTE)((pixel >> 16) & 0xFF);

			argb = Color::MakeARGB(a, r, g, b);
			pixCol.SetValue(argb);
			image->SetPixel(x, y, pixCol);

			dest++;
		}
	}

	WCHAR fname[1024];
	MultiByteToWideChar(CP_ACP, 0, name, strlen(name)+1, fname, 1024);
	CLSID pngClsid;
	GetEncoderClsid(L"image/png", &pngClsid);
	image->Save(fname, &pngClsid);
	return true;
}

bool SaveRGBAToPng(char *name, void *address, int width, int height)
{
	GdiplusStartupInput gdiplusStartupInput;
	ULONG_PTR           gdiplusToken;

	// Initialize GDI+.
	GdiplusStartup(&gdiplusToken, &gdiplusStartupInput, NULL);
	bool result;
	result = SaveImageToPng(name, address, width, height);
	if(!result) return false;
    GdiplusShutdown(gdiplusToken);
    return true;
}

bool QueryImageInternal(char *name, int *width, int *height)
{
	WCHAR fname[1024];
	MultiByteToWideChar(CP_ACP, 0, name, strlen(name)+1, fname, 1024);
	Bitmap picture(fname);
	*width = picture.GetWidth();
	*height = picture.GetHeight();
	return true;
}

bool QueryImage(char *name, int *width, int *height)
{
	
	GdiplusStartupInput gdiplusStartupInput;
	ULONG_PTR           gdiplusToken;

	// Initialize GDI+.
	
	GdiplusStartup(&gdiplusToken, &gdiplusStartupInput, NULL);
   
   QueryImageInternal(name, width, height);
   
   GdiplusShutdown(gdiplusToken);
   return true;
}

bool GetImageInternal(char *name, void *address, int width, int height)
{
	WCHAR fname[1024];
	MultiByteToWideChar(CP_ACP, 0, name, strlen(name)+1, fname, 1024);
	Bitmap picture(fname);
	Color pixCol;
	int r,g,b,a;
	unsigned int pixel;
	unsigned int *dest = (unsigned int *) address;

	for(int y=0; y<height; y++)
	  {
		  for(int x=0; x<width; x++)
		  {

			//picture.GetPixel(x, height - y, &pixCol); //for flipping
			picture.GetPixel(x, y, &pixCol);
			r = pixCol.GetRed();
			g = pixCol.GetGreen();
			b = pixCol.GetBlue();
			a = pixCol.GetAlpha();
			pixel = KRGBA(r, g, b, a);
			*dest = pixel;
			dest++;
		  }
	  }
	return true;
}

bool GetImage(char *name, void *address, int width, int height)
{
	GdiplusStartupInput gdiplusStartupInput;
	ULONG_PTR           gdiplusToken;

	// Initialize GDI+.
	
	GdiplusStartup(&gdiplusToken, &gdiplusStartupInput, NULL);
   
   GetImageInternal(name, address, width, height);
   
   GdiplusShutdown(gdiplusToken);
   return true;
}

static PyObject*
query_image(PyObject *self, PyObject *args)
{
	int width, height;
	char *name;
	if (! PyArg_ParseTuple(args, "s", &name))  /* convert Python -> C */
        return NULL;    
	else
	{
		QueryImage(name, &width, &height);
		return Py_BuildValue("ii", width, height);
		
	}
	Py_RETURN_NONE;
}

static PyObject*
get_image(PyObject *self, PyObject *args)
{
	int width, height;
	uint address;
	char *name;
	#ifdef BIT64
	if (! PyArg_ParseTuple(args, "sKii", &name, &address, &width, &height))  /* convert Python -> C */
        return NULL;
	#else
	if (! PyArg_ParseTuple(args, "sIii", &name, &address, &width, &height))  /* convert Python -> C */
        return NULL;
	#endif  
	else
	{
		GetImage(name, (void *)address, width, height);
		Py_RETURN_NONE;
	}
	Py_RETURN_NONE;
}

static PyObject*
save_image(PyObject *self, PyObject *args)
{
	int width, height;
	uint address;
	char *name;
	#ifdef BIT64
	if (! PyArg_ParseTuple(args, "sKii", &name, &address, &width, &height))  /* convert Python -> C */
        return NULL;
	#else
	if (! PyArg_ParseTuple(args, "sIii", &name, &address, &width, &height))  /* convert Python -> C */
        return NULL;
	#endif     
	else
	{
		SaveRGBAToPng(name, (void *)address, width, height);
		Py_RETURN_NONE;
	}
	Py_RETURN_NONE;
}

/* registration table  */
static struct PyMethodDef imload_methods[] = {
	{"QueryImage", query_image, METH_VARARGS,"Get dimensions of picture."},
	{"GetImage", get_image, METH_VARARGS, "Get Image From File"},
	{"SaveRGBAToPNG", save_image, METH_VARARGS, "Save RGBA color buffer to png image."},
    {NULL, NULL, 0, NULL}                   /* end of table marker */
};

static struct PyModuleDef imloadmodule = {
   PyModuleDef_HEAD_INIT,
   "imload",   /* name of module */
   NULL, /* module documentation, may be NULL */
   -1,       /* size of per-interpreter state of the module,
                or -1 if the module keeps state in global variables. */
   imload_methods
};

/* module initializer */
PyMODINIT_FUNC PyInit_imload( )                       /* called on first import */
{                                      /* name matters if loaded dynamically */
    return PyModule_Create(&imloadmodule);
}
