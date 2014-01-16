#include<windows.h>
#include <Python.h>
#include "FreeImage.h"

typedef unsigned int uint32;
typedef unsigned long long uint64;


#ifdef BIT64
typedef uint64 uint;
#else
typedef uint32 uint;
#endif

void QueryImage(const char *name, unsigned *width, unsigned *height, unsigned *bpp)
{
	FREE_IMAGE_FORMAT formato = FreeImage_GetFileType(name, 0);
	FIBITMAP* image = FreeImage_Load(formato, name);

	unsigned w = FreeImage_GetWidth(image);
	unsigned h = FreeImage_GetHeight(image);
	unsigned b = FreeImage_GetBPP(image);

	*width = w;
	*height = h;
	*bpp = b;

	FreeImage_Unload(image);

}

void GetImage(const char *name, void *address, unsigned width, unsigned height, unsigned bpp)
{
	FREE_IMAGE_FORMAT formato = FreeImage_GetFileType(name, 0);
	FIBITMAP* image = FreeImage_Load(formato, name);

	if (bpp == 24)
	{
		unsigned int *dest = (unsigned int *) address;
		for(unsigned y=0; y<height; y++)
		{
			RGBQUAD color;
			for(unsigned x=0; x<width; x++)
			{
				FreeImage_GetPixelColor(image, x, y, &color);
				unsigned int pix = (255<<24) | (color.rgbBlue<<16) | (color.rgbGreen<<8) | color.rgbRed;
				*dest = pix;
				dest++;
			}
		}
	}
	else if(bpp == 32)
	{
		unsigned int *dest = (unsigned int *) address;
		for(unsigned y=0; y<height; y++)
		{
			RGBQUAD color;
			for(unsigned x=0; x<width; x++)
			{
				FreeImage_GetPixelColor(image, x, y, &color);
				unsigned int pix = (color.rgbReserved<<24) | (color.rgbBlue<<16) | (color.rgbGreen<<8) | color.rgbRed;
				//memcpy(dest, &color, 4);
				*dest = pix;
				dest++;
			}
		}
	}
	else if(bpp == 96)
	{
		float *dest = (float *) address;
		for(unsigned y=0; y<height; y++)
		{
			FIRGBF *bits = (FIRGBF *)FreeImage_GetScanLine(image, y);
			for(unsigned x=0; x<width; x++)
			{
				*dest = bits[x].red;
				dest++;
				*dest = bits[x].green;
				dest++;
				*dest = bits[x].blue;
				dest++;
				*dest = 0.999f;
				dest++;
			}
		}
	}
	else if(bpp == 128)
	{
		float *dest = (float *) address;
		for(unsigned y=0; y<height; y++)
		{
			FIRGBAF *bits = (FIRGBAF *)FreeImage_GetScanLine(image, y);
			for(unsigned x=0; x<width; x++)
			{
				*dest = bits[x].red;
				dest++;
				*dest = bits[x].green;
				dest++;
				*dest = bits[x].blue;
				dest++;
				*dest = bits[x].alpha;
				dest++;
			}
		}
	}

	FreeImage_Unload(image);
}

void SaveImage(const char *name, void *address, unsigned width, unsigned height, unsigned bpp)
{
	if (bpp == 24)
	{
		FIBITMAP *image = FreeImage_Allocate(width, height, bpp);
		unsigned int *src = (unsigned int *) address;
		unsigned int pix;
		for(unsigned y=0; y<height; y++)
		{
			RGBQUAD color;
			for(unsigned x=0; x<width; x++)
			{
				pix = *src;
				unsigned char *p = (unsigned char*)&pix;
				color.rgbRed = p[0];
				color.rgbGreen = p[1];
				color.rgbBlue = p[2];
				color.rgbReserved = 0;
				FreeImage_SetPixelColor(image, x, y, &color);
				src++;
			}
		}
		FreeImage_Save(FIF_JPEG, image, name);
		FreeImage_Unload(image);
	}
	else if(bpp == 32)
	{
		FIBITMAP *image = FreeImage_Allocate(width, height, bpp);
		unsigned int *src = (unsigned int *) address;
		unsigned int pix;
		for(unsigned y=0; y<height; y++)
		{
			RGBQUAD color;
			for(unsigned x=0; x<width; x++)
			{
				pix = *src;
				unsigned char *p = (unsigned char*)&pix;
				color.rgbRed = p[0];
				color.rgbGreen = p[1];
				color.rgbBlue = p[2];
				color.rgbReserved = p[3];
				FreeImage_SetPixelColor(image, x, y, &color);
				src++;
			}
		}
		FreeImage_Save(FIF_PNG, image, name);
		FreeImage_Unload(image);
	}
	else if(bpp == 96)
	{
		FIBITMAP *tmp = FreeImage_Allocate(width, height, 32);
		FIBITMAP *image = FreeImage_ConvertToRGBF(tmp);

		float *src = (float *) address;
		for(unsigned y=0; y<height-1; y++)
		{

			FIRGBF *bits = (FIRGBF *)FreeImage_GetScanLine(image, y);
			for(unsigned x=0; x<width-1; x++)
			{
				bits[x].red = *src;
				src++;
				bits[x].green = *src;
				src++;
				bits[x].blue = *src;
				src++;
				src++;
			}
		}
		FreeImage_Save(FIF_EXR, image, name);
		FreeImage_Unload(tmp);
		FreeImage_Unload(image);
	}
	else if(bpp == 128)
	{
		FIBITMAP *tmp = FreeImage_Allocate(width, height, 32);
		FIBITMAP *image = FreeImage_ConvertToRGBF(tmp);

		float *src = (float *) address;
		for(unsigned y=0; y<height; y++)
		{

			FIRGBF *bits = (FIRGBF *)FreeImage_GetScanLine(image, y);
			for(unsigned x=0; x<width; x++)
			{
				bits[x].red = *src;
				src++;
				bits[x].green = *src;
				src++;
				bits[x].blue = *src;
				src++;
				src++;
			}
		}
		FreeImage_Save(FIF_EXR, image, name);
		FreeImage_Unload(tmp);
		FreeImage_Unload(image);
	}
}

static PyObject*
query_image(PyObject *self, PyObject *args)
{
	unsigned width, height, bpp;
	char *name;
	if (! PyArg_ParseTuple(args, "s", &name))  /* convert Python -> C */
        return NULL;    
	else
	{
		QueryImage((const char*)name, &width, &height, &bpp);
		return Py_BuildValue("III", width, height, bpp);
		
	}
	Py_RETURN_NONE;
}

static PyObject*
get_image(PyObject *self, PyObject *args)
{
	unsigned width, height, bpp;
	uint address;
	char *name;
	#ifdef BIT64
	if (! PyArg_ParseTuple(args, "sKIII", &name, &address, &width, &height, &bpp))  /* convert Python -> C */
        return NULL;
	#else
	if (! PyArg_ParseTuple(args, "sIIII", &name, &address, &width, &height, &bpp))  /* convert Python -> C */
        return NULL;
	#endif  
	else
	{
		GetImage((const char*)name, (void *)address, width, height, bpp);
		Py_RETURN_NONE;
	}
	Py_RETURN_NONE;
}

static PyObject*
save_image(PyObject *self, PyObject *args)
{
	unsigned width, height, bpp;
	uint address;
	char *name;
	#ifdef BIT64
	if (! PyArg_ParseTuple(args, "sKIII", &name, &address, &width, &height, &bpp))  /* convert Python -> C */
        return NULL;
	#else
	if (! PyArg_ParseTuple(args, "sIIII", &name, &address, &width, &height, &bpp))  /* convert Python -> C */
        return NULL;
	#endif  
	else
	{
		SaveImage((const char*)name, (void *)address, width, height, bpp);
		Py_RETURN_NONE;
	}
	Py_RETURN_NONE;
}

/* registration table  */
static struct PyMethodDef freeimgldr_methods[] = {
	{"QueryImage", query_image, METH_VARARGS,"Get dimensions of image."},
	{"GetImage", get_image, METH_VARARGS, "Get image from file"},
	{"SaveImage", save_image, METH_VARARGS, "Save image to file"},
    {NULL, NULL, 0, NULL}                   /* end of table marker */
};

static struct PyModuleDef freeimgldrmodule = {
   PyModuleDef_HEAD_INIT,
   "freeimgldr",   /* name of module */
   NULL, /* module documentation, may be NULL */
   -1,       /* size of per-interpreter state of the module,
                or -1 if the module keeps state in global variables. */
   freeimgldr_methods
};

/* module initializer */
PyMODINIT_FUNC PyInit_freeimgldr( )                       /* called on first import */
{                                      /* name matters if loaded dynamically */
    return PyModule_Create(&freeimgldrmodule);
}
