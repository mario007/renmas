
#include<windows.h>
#include <Python.h>


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

const char g_szClassName[] = "__WindowClass__";
HDC		__ghDC;                      // Device context.
HWND	__ghWnd;
int nWindows = 0; // terminate loop when nWindow drops to 0

static PyObject *py_mw = NULL; // python object that act in real time

class FrameBuffer
{
public:
	BITMAPINFO  pBitmapInfo;
	HBITMAP      bitmapHandle;
	HDC dc_mem;
	HWND hwnd;
	void *pixels;
	int width, height;
	PyObject *py_obj; // python object that recive events

	FrameBuffer(int w, int h, HWND hwnd, HDC frontHdc)
	{
		if(w < 1) w = 1; // maybe throwing exception?
		if(h < 1) h = 1;
		this->width = w;
		this->height = h;
		this->hwnd = hwnd;
		this->py_obj = NULL;
		
		pBitmapInfo.bmiHeader.biSize           =  sizeof( BITMAPINFOHEADER );   /// BitmapInfoSizeInBytes;
		pBitmapInfo.bmiHeader.biWidth          =  long(width);
		pBitmapInfo.bmiHeader.biHeight         =  -long(height);                /// neg means top down
		pBitmapInfo.bmiHeader.biPlanes         =  1;                            /// always 1
		pBitmapInfo.bmiHeader.biBitCount       =  32;                            /// 1, 4, 8, 16, 24, 32
		pBitmapInfo.bmiHeader.biCompression    =  BI_RGB;
		pBitmapInfo.bmiHeader.biSizeImage      =  0;                            /// 0 = full size no compress
		pBitmapInfo.bmiHeader.biXPelsPerMeter  =  1;                            /// ?
		pBitmapInfo.bmiHeader.biYPelsPerMeter  =  1;                            /// ?
		pBitmapInfo.bmiHeader.biClrUsed        =  0;                            /// 0 = all possible
		pBitmapInfo.bmiHeader.biClrImportant   =  0;                            /// 0 = all
		
		bitmapHandle = CreateDIBSection(NULL, &pBitmapInfo, DIB_RGB_COLORS, &pixels, NULL, 0);
		dc_mem = CreateCompatibleDC(frontHdc);
		SelectObject(dc_mem, bitmapHandle);

	}

	void clear_buffer(int r, int g, int b)
	{
		
		unsigned int *adr = (unsigned int*)this->pixels; 
		unsigned int pixel = KRGB(r, g, b);

		for(int i=0; i< width* height; i++)
		{
			*adr = pixel;
			adr++;
		}

	}
	void set_python_object(PyObject *py)
	{
		this->py_obj = py;
	}
	void* get_pixels()
	{
		return this->pixels;
	}

	HDC get_hdc()
	{
		return this->dc_mem;
	}

	void refresh()
	{
		InvalidateRect(hwnd, NULL, FALSE);
	}

	int get_width()
	{
		return this->width;
	}

	int get_height()
	{
		return this->height;
	}
	void set_pixel(int x, int y, int r, int g, int b)
	{
		if(x < 0 || x >= this->width) return;
		if(y < 0 || y >= this->height) return;
		unsigned int pixel = KRGB(r, g, b);
		*(unsigned int *)((unsigned int*)this->pixels + y * this->width + x) = pixel;
	}
	int LeftMouseDown(int x, int y)
	{
		if(this->py_obj == NULL) return 0;
		PyObject *result = NULL;
		result = PyObject_CallMethod(this->py_obj, "l_mouse_down", "ii", x, y);
		if (result != NULL)
		{
			Py_DECREF(result);
		}
		else // failure
		{
			PyErr_Print();
			this->Destroy();
		}
		return 0;
	}

	int LeftMouseUp(int x, int y)
	{
		if(this->py_obj == NULL) return 0;
		PyObject *result = NULL;
		result = PyObject_CallMethod(this->py_obj, "l_mouse_up", "ii", x, y);
		if (result != NULL)
		{
			Py_DECREF(result);
		}
		else // failure
		{
			PyErr_Print();
			this->Destroy();
		}
		return 0;
	}
	int MouseMove(int x, int y, int key)
	{
		if(this->py_obj == NULL) return 0;
		PyObject *result = NULL;
		result = PyObject_CallMethod(this->py_obj, "mouse_move", "iii", x, y, key);
		if (result != NULL)
		{
			Py_DECREF(result);
		}
		else // failure
		{
			PyErr_Print();
			this->Destroy();
		}
		return 0;
	}
	int CharPressed(int c)
	{
		if(this->py_obj == NULL) return 0;
		PyObject *result = NULL;
		result = PyObject_CallMethod(this->py_obj, "char_pressed", "i", c);
		if (result != NULL)
		{
			Py_DECREF(result);
		}
		else // failure
		{
			PyErr_Print();
			this->Destroy();
		}
		return 0;
	}
	void Destroy()
	{
		DestroyWindow(this->hwnd);
	}
	~FrameBuffer()
	{
		DeleteObject(bitmapHandle);
	}
};


void ClientResize(HWND hWnd, int nWidth, int nHeight)
{
  RECT rcClient, rcWindow;
  POINT ptDiff;
  GetClientRect(hWnd, &rcClient);
  GetWindowRect(hWnd, &rcWindow);
  ptDiff.x = (rcWindow.right - rcWindow.left) - rcClient.right;
  ptDiff.y = (rcWindow.bottom - rcWindow.top) - rcClient.bottom;
  MoveWindow(hWnd,rcWindow.left, rcWindow.top, nWidth + ptDiff.x, nHeight + ptDiff.y, TRUE);
}

//Window Procedure
LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam)
{
    switch(msg)
    {
		case WM_CREATE:
			{
				RECT rect;
				HDC hdc = GetDC(hwnd);
				GetWindowRect(GetDesktopWindow(), &rect);
				FrameBuffer *fb = new FrameBuffer(rect.right, rect.bottom, hwnd, hdc);
				SetWindowLongPtr(hwnd, GWLP_USERDATA, (LONG_PTR)fb);
				ReleaseDC(hwnd, hdc);
			}
		break;
        case WM_CLOSE:
			DestroyWindow(hwnd); //FIXME
        break;
        case WM_DESTROY: // multiple windows fix message loop
			{
				FrameBuffer *fb = (FrameBuffer*) GetWindowLongPtr(hwnd, GWLP_USERDATA);
				delete fb;
				nWindows--;
				if(nWindows == 0)
					PostQuitMessage(0);
			}
        break;
		case WM_PAINT:
			{
				PAINTSTRUCT psPaint;
				HDC hdc = BeginPaint( hwnd, &psPaint );
				FrameBuffer *fb = (FrameBuffer*) GetWindowLongPtr(hwnd, GWLP_USERDATA);
				BitBlt(hdc, 0, 0, fb->get_width(), fb->get_height(), fb->get_hdc(), 0, 0, SRCCOPY);
				EndPaint (hwnd, &psPaint);
			}
		break;
		case WM_LBUTTONDOWN:
			{
				FrameBuffer *fb = (FrameBuffer*) GetWindowLongPtr(hwnd, GWLP_USERDATA);
				fb->LeftMouseDown(LOWORD(lParam), HIWORD(lParam));
			}
		break;
		case WM_MOUSEMOVE:
			{
				FrameBuffer *fb = (FrameBuffer*) GetWindowLongPtr(hwnd, GWLP_USERDATA);
				fb->MouseMove(LOWORD(lParam), HIWORD(lParam), (int)wParam);
			}
		break;
		case WM_SIZE:
			{
				FrameBuffer *fb = (FrameBuffer*) GetWindowLongPtr(hwnd, GWLP_USERDATA);
				int width = LOWORD(lParam);
				int height = HIWORD(lParam);
				if(width > fb->get_width())
				{
					if(height > fb->get_height()) {
						ClientResize(hwnd, fb->get_width(), fb->get_height());
					}
					else {
						ClientResize(hwnd, fb->get_width(), height);
					}
				}
				else
				{
					if(height > fb->get_height()) {
						ClientResize(hwnd, width, fb->get_height());
					} 
					else
						ClientResize(hwnd, width, height);
				}
			}
		break;
		case WM_CHAR:
			{
				FrameBuffer *fb = (FrameBuffer*) GetWindowLongPtr(hwnd, GWLP_USERDATA);
				fb->CharPressed((int)wParam);
			}
		break;
		case WM_LBUTTONUP:
		{
			FrameBuffer *fb = (FrameBuffer*) GetWindowLongPtr(hwnd, GWLP_USERDATA);
			fb->LeftMouseUp(LOWORD(lParam), HIWORD(lParam));
		}
		break;
        default:
            return DefWindowProc(hwnd, msg, wParam, lParam);
    }
    return 0;
}

int RegisterClass()
{
	WNDCLASSEX wc;

	//Registering the Window Class
    wc.cbSize        = sizeof(WNDCLASSEX);
    wc.style         = 0;
    wc.lpfnWndProc   = WndProc;
    wc.cbClsExtra    = 0;
    wc.cbWndExtra    = sizeof(LONG_PTR);
    wc.hInstance     = (HINSTANCE)GetModuleHandle(NULL);
    wc.hIcon         = LoadIcon(NULL, IDI_APPLICATION);
    wc.hCursor       = LoadCursor(NULL, IDC_ARROW);
    wc.hbrBackground = (HBRUSH)(COLOR_WINDOW+1);
    wc.lpszMenuName  = NULL;
    wc.lpszClassName = g_szClassName;
    wc.hIconSm       = LoadIcon(NULL, IDI_APPLICATION);

    if(!RegisterClassEx(&wc))
    {
        MessageBox(NULL, "Window Registration Failed!", "Error!",
            MB_ICONEXCLAMATION | MB_OK);
        return -1;
    }
	return 0;
}


void MessagePump()
{
	int run=0;
	while(TRUE)
	{
		MSG msg;
		if(run == 0)
		{
			GetMessage(&msg, NULL, 0, 0);
			TranslateMessage(&msg);
			DispatchMessage(&msg);
			// If the message is WM_QUIT, exit the while loop
			if(msg.message == WM_QUIT)
			break;

			if(msg.message == WM_USER)
			{
				run = (int)msg.wParam;
			}
		}
		else
		{
			// Check to see if any messages are waiting in the queue
			while(PeekMessage(&msg, NULL, 0, 0, PM_REMOVE))
			{
				// Translate the message and dispatch it to WindowProc()
				TranslateMessage(&msg);
				DispatchMessage(&msg);
			}
			// If the message is WM_QUIT, exit the while loop
			if(msg.message == WM_QUIT)
			break;
			
			if(msg.message == WM_USER)
			{
				run = (int)msg.wParam;
			}
			// real time
			PyObject *result = NULL;
			result = PyObject_CallMethod(py_mw, "render", "");
			if (result != NULL) Py_DECREF(result);
			else
			{
				PyErr_Print();
			}
		}
		
	}
}

HWND MakeWindow(char *name, int width, int height)
{
	// Only first time register class for window
	static int reg = 0;
	if(reg == 0)
		RegisterClass();
	reg = 1;

	// to make client area of desired size
	RECT rect;
	rect.left = 80;
	rect.right = width + 80;
	rect.top = 80;
	rect.bottom = height + 80;
	AdjustWindowRect(&rect, WS_OVERLAPPEDWINDOW, FALSE);

	HWND hwnd;
    // Creating the Window
    hwnd = CreateWindowEx(
        0,
        g_szClassName,
        name,
        WS_OVERLAPPEDWINDOW,
		//WS_POPUP,  // bordless window
		rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top,
        NULL, NULL, (HINSTANCE)GetModuleHandle(NULL), NULL);

    if(hwnd == NULL)
    {
        MessageBox(NULL, "Window Creation Failed!", "Error!",
            MB_ICONEXCLAMATION | MB_OK);
        return 0;
    }
	nWindows++;

	/*// switch off the title bar
	    DWORD dwstyle = GetWindowLong(hwnd, GWL_STYLE);
	    dwstyle &= ~WS_CAPTION;
	    SetWindowLong(hwnd, GWL_STYLE, dwstyle);

		// move the window to (0,0)
		//SetWindowPos(hwnd, 0, 300, 300, 200, 200, SWP_NOSIZE | SWP_NOZORDER);
		InvalidateRect(hwnd, 0, true);*/	
	
    ShowWindow(hwnd, SW_SHOW);
    UpdateWindow(hwnd);
	return hwnd;
}


bool Blit1(void *da, int dx, int dy, int dw, int dh, void *sa, int sx, int sy, int sw, int sh, int src_pitch)
{
	if (dx < 0 || dx > dw) return false;
	if (dy < 0 || dy > dh) return false;

	if (sw > dw - dx) sw = dw - dx;
	if (sh > dh - dy) sh = dh - dy;

	unsigned int *dest = (unsigned int *) da;
	unsigned int *src = (unsigned int *) sa;

	for(int j = dy; j<dy+sh; j++, sy++)
	{
		memcpy(dest + j * dw + dx, src + sy * src_pitch + sx, sw * 4);
	}

	return true;
}

bool TransparentBlit(void *da, int dx, int dy, int dw, int dh, void *sa, int sx, int sy, int sw, int sh, int src_pitch, unsigned int key)
{
	if (dx < 0 || dx > dw) return false;
	if (dy < 0 || dy > dh) return false;

	if (sw > dw - dx) sw = dw - dx;
	if (sh > dh - dy) sh = dh - dy;

	unsigned int *dest = (unsigned int *) da;
	unsigned int *src = (unsigned int *) sa;
	unsigned int *adr_dest, *adr_source;

	for(int j = dy; j<dy+sh; j++, sy++)
	{
		adr_dest = dest + j * dw + dx;
		adr_source = src + sy * src_pitch + sx;
		for(int i=0; i<sw; i++)
		{
			if(key != *adr_source) *adr_dest = *adr_source;
			adr_dest++;
			adr_source++;
		}
	}

	return true;
}

bool AlphaBlit(void *da, int dx, int dy, int dw, int dh, void *sa, int sx, int sy, int sw, int sh, int src_pitch)
{
	if (dx < 0 || dx > dw) return false;
	if (dy < 0 || dy > dh) return false;

	if (sw > dw - dx) sw = dw - dx;
	if (sh > dh - dy) sh = dh - dy;

	unsigned int *dest = (unsigned int *) da;
	unsigned int *src = (unsigned int *) sa;
	unsigned int *adr_dest, *adr_source;

	for(int j = dy; j<dy+sh; j++, sy++)
	{
		adr_dest = dest + j * dw + dx;
		adr_source = src + sy * src_pitch + sx;
		for(int i=0; i<sw; i++)
		{
			if((*adr_source & 0xFF000000) != 0) *adr_dest = *adr_source; //FIXME - use better formula
			adr_dest++;
			adr_source++;
		}
	}

	return true;
}

bool Blit(void *dest_adr, int dest_x, int dest_y, int dest_width, int dest_height, void *src_adr, int src_x, int src_y, int src_width, int src_height)
{
	if (dest_x < 0 || dest_x > dest_width) return false;
	if (dest_y < 0 || dest_y > dest_height) return false;
	//popravi do kraja, bitno je


	unsigned int *dest = (unsigned int *) dest_adr;
	unsigned int *src = (unsigned int *) src_adr;

	dest = dest + dest_y * dest_width + dest_x;
	src = src + src_y * src_width + src_x;

	for (int j=src_y; j< src_y + src_height; j++)
	{
		for(int i=src_x; i< src_x + src_width; i++)
		{
			*dest = *src;
			dest++;
			src++;
		}
		dest_y += 1;
		dest = (unsigned int*)dest_adr + dest_y * dest_width + dest_x;
		src = (unsigned int*)src_adr + j * src_width + src_x;
	}
	return true;
}

static PyObject *
message_pump(PyObject *self, PyObject *args)
{
	MessagePump();
	Py_RETURN_NONE;
}



static PyObject*
blitting(PyObject *self, PyObject *args)
{
	uint da, sa;
	int dx, dy, dw, dh, sx, sy, sw, sh, src_pitch;
	#ifdef BIT64
	if (! PyArg_ParseTuple(args, "KiiiiKiiiii", &da, &dx, &dy, &dw, &dh, &sa, &sx, &sy, &sw, &sh, &src_pitch)) 
        return NULL;   
	#else
	if (! PyArg_ParseTuple(args, "IiiiiIiiiii", &da, &dx, &dy, &dw, &dh, &sa, &sx, &sy, &sw, &sh, &src_pitch)) 
        return NULL;  
	#endif
	else
	{
		Blit1((void*)da, dx, dy, dw, dh, (void *)sa, sx, sy, sw, sh, src_pitch);
	}
	Py_RETURN_NONE;
}

static PyObject*
transparent_blit(PyObject *self, PyObject *args)
{
	unsigned int key;
	uint da, sa;
	int dx, dy, dw, dh, sx, sy, sw, sh, src_pitch;
	#ifdef BIT64
	if (! PyArg_ParseTuple(args, "KiiiiKiiiiiI", &da, &dx, &dy, &dw, &dh, &sa, &sx, &sy, &sw, &sh, &src_pitch, &key)) 
        return NULL;    
	#else
	if (! PyArg_ParseTuple(args, "IiiiiIiiiiiI", &da, &dx, &dy, &dw, &dh, &sa, &sx, &sy, &sw, &sh, &src_pitch, &key)) 
        return NULL;  
	#endif  
	else
	{
		TransparentBlit((void*)da, dx, dy, dw, dh, (void *)sa, sx, sy, sw, sh, src_pitch, key);
	}
	Py_RETURN_NONE;
}

static PyObject*
alpha_blit(PyObject *self, PyObject *args)
{
	uint da, sa;
	int dx, dy, dw, dh, sx, sy, sw, sh, src_pitch;
	#ifdef BIT64
	if (! PyArg_ParseTuple(args, "KiiiiKiiiii", &da, &dx, &dy, &dw, &dh, &sa, &sx, &sy, &sw, &sh, &src_pitch)) 
        return NULL;
	#else
	if (! PyArg_ParseTuple(args, "IiiiiIiiiii", &da, &dx, &dy, &dw, &dh, &sa, &sx, &sy, &sw, &sh, &src_pitch)) 
        return NULL;  
	#endif   
	else
	{
		AlphaBlit((void*)da, dx, dy, dw, dh, (void *)sa, sx, sy, sw, sh, src_pitch);
	}
	Py_RETURN_NONE;
}


static PyObject*
real_time(PyObject *self, PyObject *args)
{
	int run;
	if (! PyArg_ParseTuple(args, "iO", &run, &py_mw))  /* convert Python -> C */
        return NULL;    
	else
	{
		PostMessage(NULL, WM_USER,(WPARAM)run, NULL);
	}
	Py_RETURN_NONE;
}


/* registration table  */
static struct PyMethodDef winlib_methods[] = {
	{"MainLoop", message_pump, METH_VARARGS, "Enter in infite message loop."},
	{"Blit", blitting, METH_VARARGS, "Blit pixels."},
	{"AlphaBlit", alpha_blit, METH_VARARGS, "Blit pixels."},
	{"TransparentBlit", transparent_blit, METH_VARARGS, "Blit pixels."},
	{"RealTime", real_time, METH_VARARGS, "Set 1 for real time loop and 0 for event loop."},
    {NULL, NULL, 0, NULL}                   /* end of table marker */
};

static struct PyModuleDef winlibmodule = {
   PyModuleDef_HEAD_INIT,
   "winlib",   /* name of module */
   NULL, /* module documentation, may be NULL */
   -1,       /* size of per-interpreter state of the module,
                or -1 if the module keeps state in global variables. */
   winlib_methods
};

// implementation of python object for window
typedef struct {
  PyObject_HEAD
  FrameBuffer *fb;
} Window;

static PyObject *
mem_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
  Py_ssize_t width, height;
  PyObject *p;
  char *name;
  Window *self = (Window *) type->tp_alloc(type, 0);
  if (!self)
    return NULL;
  if (!PyArg_ParseTuple(args, "snnO", &name,  &width, &height, &p)) {
    //Py_DECREF(self); // FIXME
    return NULL;
  }

  HWND hwnd = MakeWindow(name, (int)width, (int)height);
  self->fb = (FrameBuffer*) GetWindowLongPtr(hwnd, GWLP_USERDATA);
  self->fb->set_python_object(p);
  return (PyObject *) self;
}

static void
mem_dealloc(Window *self)
{
  self->fb->Destroy();
  self->fb = NULL;
  self->ob_base.ob_type->tp_free((PyObject*)self);
  //PyObject_DEL(self);
}

static PyObject *
fb_pixels(Window *self)
{
	return PyLong_FromVoidPtr(self->fb->get_pixels());
}

static PyObject *
refresh_fb(Window *self)
{
	self->fb->refresh();
	Py_RETURN_NONE;
}

static PyObject *
destroy(Window *self)
{
	self->fb->Destroy();
	Py_RETURN_NONE;
}

static PyObject*
set_pixel(Window *self, PyObject *args)
{
	int r, g, b, x, y;
	if (! PyArg_ParseTuple(args, "iiiii", &x, &y, &r, &g, &b))  /* convert Python -> C */ 
        return NULL;    
	else
	{
		self->fb->set_pixel(x, y, r, g, b);
	}
	Py_RETURN_NONE;
}

static PyObject*
clear_fb(Window *self, PyObject *args)
{
	int r, g, b;
	if (! PyArg_ParseTuple(args, "iii", &r, &g, &b))  /* convert Python -> C */ 
        return NULL;    
	else
	{
		self->fb->clear_buffer(r, g, b);
	}
	Py_RETURN_NONE;
}

static PyObject*
getsize_fb(Window *self, PyObject *args)
{
	int width = self->fb->get_width();
	int height = self->fb->get_height();
	PyObject *p = PyTuple_New((Py_ssize_t)2);
	PyObject *m = PyLong_FromLong(width);
	PyTuple_SET_ITEM(p, 0, m);	
	PyObject *m2 = PyLong_FromLong(height);
	PyTuple_SET_ITEM(p, 1, m2);
	return p;
}

static PyMethodDef mem_methods[] = {
  {"pixels", (PyCFunction) fb_pixels, METH_NOARGS },
  {"destroy", (PyCFunction) destroy, METH_NOARGS },
  {"redraw", (PyCFunction) refresh_fb, METH_NOARGS },
  {"set_pixel", (PyCFunction) set_pixel, METH_VARARGS },
  {"clear_buffer", (PyCFunction) clear_fb, METH_VARARGS },
  {"get_size", (PyCFunction) getsize_fb, METH_NOARGS },
  {NULL}
};

static PyTypeObject WindowType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "winlib.Window",             /*tp_name*/
    sizeof(Window),	       /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor) mem_dealloc,  /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,        /*tp_flags*/
    0,                         /*tp_doc */
    0,                         /*tp_traverse */
    0,                         /*tp_clear*/
    0,                         /*tp_richcompare*/
    0,                         /*tp_weaklistoffset*/
    0,                         /*tp_iter*/
    0,                         /*tp_iternext*/
    mem_methods,               /*tp_methods*/
    0,                         /*tp_members*/
    0,                         /*tp_getset*/
    0,                         /*tp_base*/
    0,                         /*tp_dict*/
    0,                         /*tp_descr_get*/
    0,                         /*tp_descr_set*/
    0,                         /*tp_dictoffset*/
    0,                         /*tp_init*/
    0,                         /*tp_alloc*/
    mem_new,                   /*tp_new*/
};

/* module initializer */
PyMODINIT_FUNC PyInit_winlib( )                       /* called on first import */
{                                      /* name matters if loaded dynamically */
    //return PyModule_Create(&winlibmodule);

	PyObject *m;

	if (PyType_Ready(&WindowType) < 0)
    return NULL;

	m = PyModule_Create(&winlibmodule);

	Py_INCREF(&WindowType);
	PyModule_AddObject(m, "Window", (PyObject *)&WindowType);

	return m; 

}


int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine,
    int nCmdShow)
{
	

	MakeWindow("prozor", 800, 400);
	

	MessagePump();
	return 0;
}
