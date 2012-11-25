#define _CRT_SECURE_NO_WARNINGS
#include <windows.h>
#include <Python.h>
#include <stdio.h>

PyObject *renmas3 = NULL;
PyObject *iface = NULL;

extern "C" __declspec(dllexport) int __cdecl Init()
{
	//Py_SetPath(L".\\DistPython\\Lib;I:\\GitTDASM;I:\\GitRENMAS");
	//Py_SetPath(L".\\DistPython\\Lib;G:\\GitTDASM\\tdasm;G:\\GitRENMAS\\renmas"); // laptop
	//Py_SetPath(L".\\DistPython\\Lib;.\\GitTDASM;.\\GitRENMAS"); // distribution

	Py_Initialize();  
	renmas3 = PyImport_ImportModule("renmas3");
	if (renmas3 == NULL) 
		return -1;
	
	iface = PyImport_ImportModule("renmas3.interface.iface");
	if (iface == NULL) 
		return -1;
	return 0;
}

extern "C" __declspec(dllexport) void __cdecl ShutDown()
{
	Py_Finalize();
}


extern "C" __declspec(dllexport) long __cdecl ExecuteFunction(const char *name, const char *args, wchar_t **value)
{
	PyObject *result = PyObject_CallMethod(iface, "exec_func", "ss", name, args);
	static wchar_t *text = NULL;
	if (text != NULL)
	{
		PyMem_Free(text);
		text = NULL;
	}

	if (result != NULL) 
	{
		text = PyUnicode_AsWideCharString(result, NULL);
		*value = (wchar_t *) text;
		Py_DECREF(result);
		return 0;
	}
	else
	{
		PyErr_Print();
		return -1;
	}

}

extern "C" __declspec(dllexport) long __cdecl GetProperty(const char *id_obj, const char *name, const char *type, wchar_t **value)
{
	PyObject *result = PyObject_CallMethod(iface, "get_prop", "sss", id_obj, name, type);
	static wchar_t *text = NULL;
	if (text != NULL)
	{
		PyMem_Free(text);
		text = NULL;
	}

	if (result != NULL) 
	{
		text = PyUnicode_AsWideCharString(result, NULL);
		*value = (wchar_t *) text;
		Py_DECREF(result);
		return 0;
	}
	else
	{
		PyErr_Print();
		return -1;
	}

}

extern "C" __declspec(dllexport) long __cdecl FreeObject(const char *id_obj)
{
	PyObject *result = PyObject_CallMethod(iface, "free_obj", "s", id_obj);
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

int main(int argc, char *argv[])
{
  int result = Init();
  printf("Rezultat je %i\n", result);
  wchar_t *value;
  long ret = ExecuteFunction("create_image", "RGBA,100,200", &value);
  char id_obj[32];
  sprintf(id_obj, "%ls", value);
  
  ret = GetProperty(id_obj, "height", "int", &value); 
  printf("Rezultat je %ls  %i\n", value, ret);

  ret = FreeObject(id_obj);
  printf("Uspjesno izbrisan objekt %i\n", ret);

}