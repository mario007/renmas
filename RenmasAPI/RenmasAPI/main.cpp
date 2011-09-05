#include <windows.h>
#include <Python.h>
#include <stdio.h>

PyObject *cmds = NULL;

extern "C" __declspec(dllexport) int __cdecl Init()
{
	Py_Initialize();  
	int result;
	//result = PyRun_SimpleString("import x86\n");  
	result = PyRun_SimpleString("import renmas\nimport renmas.interface.gui_cmds as cmds\n");
	cmds = PyImport_ImportModule("renmas.interface.gui_cmds");
	//wchar_t *path = Py_GetPath();
	//wprintf(L"%s", path);
	return result;  
}

extern "C" __declspec(dllexport) void __cdecl ShutDown()
{
	//Py_Finalize();

}

extern "C" __declspec(dllexport) int __cdecl RunScript(const char *filename)
{
	FILE *f = fopen(filename, "r");
	if (f == NULL) return -1;
	int result = PyRun_SimpleFile(f, filename);
	if(result == -1) PyErr_Clear();
	fclose(f);
	return result;
}

extern "C" __declspec(dllexport) long __cdecl WidthImage()
{
	PyObject *result = NULL;
	result = PyObject_CallMethod(cmds, "width_image", "");
	long width = -1;
	if (result != NULL) 
	{
		width = PyLong_AsLong(result);
		Py_DECREF(result);
	}
	else
	{
		PyErr_Print();
	}
	return width;
}

extern "C" __declspec(dllexport) long __cdecl HeightImage()
{
	PyObject *result = NULL;
	result = PyObject_CallMethod(cmds, "height_image", "");
	long height = -1;
	if (result != NULL) 
	{
		height = PyLong_AsLong(result);
		Py_DECREF(result);
	}
	else
	{
		PyErr_Print();
	}
	return height;
}

extern "C" __declspec(dllexport) unsigned int __cdecl PtrImage()
{
	PyObject *result = NULL;
	result = PyObject_CallMethod(cmds, "ptr_image", "");
	unsigned int ptr_image = -1;
	if (result != NULL) 
	{
		ptr_image = PyLong_AsUnsignedLong(result);
		Py_DECREF(result);
	}
	else
	{
		PyErr_Print();
	}
	return ptr_image;
}

extern "C" __declspec(dllexport) long __cdecl PitchImage()
{
	PyObject *result = NULL;
	result = PyObject_CallMethod(cmds, "pitch_image", "");
	long pitch = -1;
	if (result != NULL) 
	{
		pitch = PyLong_AsLong(result);
		Py_DECREF(result);
	}
	else
	{
		PyErr_Print();
	}
	return pitch;
}

extern "C" __declspec(dllexport) long __cdecl Render()
{
	PyObject *result = NULL;
	result = PyObject_CallMethod(cmds, "render", "");
	long finished = -1;
	if (result != NULL) 
	{
		finished = PyLong_AsLong(result);
		Py_DECREF(result);
	}
	else
	{
		PyErr_Print();
	}
	return finished;
}

extern "C" __declspec(dllexport) long __cdecl PrepareScene()
{
	PyObject *result = NULL;
	result = PyObject_CallMethod(cmds, "prepare_scene", "");
	long prepared = 0;
	if (result != NULL) 
	{
		prepared = PyLong_AsLong(result);
		Py_DECREF(result);
	}
	else
	{
		prepared = 25;
		PyErr_Print();
	}
	return prepared;
}

extern "C" __declspec(dllexport) const char* __cdecl GetProperty(const char*category, const char *name)
{
	PyObject *result = NULL;
	result = PyObject_CallMethod(cmds, "get_property", "ss", category, name);
	wchar_t *text = NULL;
	static char *text_buffer = NULL;
	if (text_buffer != NULL)
	{
		free(text_buffer);
		text_buffer = NULL;
	}

	if (result != NULL) 
	{
		text = PyUnicode_AsWideCharString(result, NULL);
		size_t size = (size_t)PyUnicode_GET_SIZE(result);
		text_buffer = (char *)malloc(size);
		wcstombs(text_buffer, text, -1);

		PyMem_Free(text);
		Py_DECREF(result);
	}
	else
	{
		PyErr_Print();
	}
	return (const char *)text_buffer;
}
extern "C" __declspec(dllexport) long __cdecl SetProperty(const char*category, const char *name, const char *value)
{
	PyObject *result = NULL;
	result = PyObject_CallMethod(cmds, "set_property", "sss", category, name, value);
	long res;
	if (result != NULL) 
	{
		res = PyLong_AsLong(result);
		Py_DECREF(result);
	}
	else
	{
		PyErr_Print(); 
	}
	return res;
}

int
main(int argc, char *argv[])
{
  Init();
  /*PyRun_SimpleString("import renmas \nfrom time import time,ctime\n"
                     "print('Today is', ctime(time()))\n");*/

  RunScript("G:\\renmas_scripts\\sphere.py");
  printf("Sirina slike je %d\n", WidthImage());
  long r = SetProperty("camera", "eye", "22.2,44.4,55.5");
  const char * text = GetProperty("camera", "eye");
  
  ShutDown();
  return 0;
}
