#define _CRT_SECURE_NO_WARNINGS
#include <windows.h>
#include <Python.h>
#include <stdio.h>

PyObject *renmas = NULL;
PyObject *renderer = NULL;
PyObject *irender = NULL;


extern "C" __declspec(dllexport) int __cdecl Init()
{
	Py_SetPath(L".\\DistPython\\Lib;I:\\GitTDASM;I:\\GitRENMAS");
	//Py_SetPath(L".\\DistPython\\Lib;.\\GitTDASM;.\\GitRENMAS");
	Py_Initialize();  
	
	renmas = PyImport_ImportModule("renmas2");
	if (renmas == NULL) return -1;
	PyObject* pclass = PyObject_GetAttrString(renmas, "Renderer");
	PyObject* pargs = Py_BuildValue("()");
	renderer = PyObject_CallObject(pclass, pargs);

	PyObject* pargs2 = Py_BuildValue("(O)", renderer);

	pclass = PyObject_GetAttrString(renmas, "IRender");
	irender = PyObject_CallObject(pclass, pargs2);

	PyObject_SetAttrString(renmas, "renderer", renderer);
	PyObject_SetAttrString(renmas, "irender", irender);
	return 0;
}

extern "C" __declspec(dllexport) void __cdecl ShutDown()
{
	Py_Finalize();
}

extern "C" __declspec(dllexport) int __cdecl RunScript(const char *filename)
{
	FILE *f = fopen(filename, "r");
	if (f == NULL) return -1;
	PyObject *pDict = PyModule_GetDict(renmas);
	PyObject *pDict2 = PyDict_Copy(pDict);
	PyObject* ret = PyRun_File(f, filename, Py_file_input, pDict2, pDict2);
	fclose(f);
	Py_DECREF(pDict2);
	if (ret == NULL)
	{
		PyErr_Clear();
		return -1;
	}
	else
	{
		Py_DECREF(ret);
		return 0;
	}
}

extern "C" __declspec(dllexport) long __cdecl Render()
{
	PyObject *result = PyObject_CallMethod(renderer, "render", "");
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

extern "C" __declspec(dllexport) void __cdecl PrepareScene()
{
	PyObject *result = PyObject_CallMethod(renderer, "prepare", "");
	if (result != NULL) {
		Py_DECREF(result);
	}
	else {
		PyErr_Print();
	}
}

extern "C" __declspec(dllexport) void __cdecl ToneMapping()
{
	PyObject *result = PyObject_CallMethod(renderer, "tone_map", "");
	if (result != NULL) {
		Py_DECREF(result);
	}
	else {
		PyErr_Print();
	}
}


extern "C" __declspec(dllexport) long __cdecl SetProps(const char*category, const char *name, const char *value)
{
	PyObject *result = NULL;
	result = PyObject_CallMethod(irender, "set_props", "sss", category, name, value);
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

extern "C" __declspec(dllexport) long __cdecl GetProps(const char*category, const char *name, wchar_t **value)
{
	PyObject *result = NULL;
	result = PyObject_CallMethod(irender, "get_props", "ss", category, name);
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


int
main(int argc, char *argv[])
{
  int result = Init();
  //result = SetProps("camera", "eye", "3,4,5");
  wchar_t *value;
  //result = GetProps("camera", "eye", &value);
  
  RunScript("I:\\GitRENMAS\\scenes\\sphere1.py");
  PrepareScene();
  Render();
  ToneMapping();
  Render();
  result = GetProps("frame_buffer", "dummy", &value);
  

  /*PyRun_SimpleString("import renmas \nfrom time import time,ctime\n"
                     "print('Today is', ctime(time()))\n");*/

  //RunScript("G:\\renmas_scripts\\sphere.py");
  //printf("Sirina slike je %d\n", WidthImage());
  //long r = SetProperty("camera", "eye", "22.2,44.4,55.5");
  //const char * text = GetProperty("camera", "eye");
  
  //ShutDown();
  return 0;
}
