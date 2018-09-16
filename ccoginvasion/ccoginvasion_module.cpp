
#include "dtoolbase.h"
#include "interrogate_request.h"

#include "py_panda.h"

extern LibraryDef ccoginvasion_moddef;
extern void Dtool_ccoginvasion_RegisterTypes();
extern void Dtool_ccoginvasion_ResolveExternals();
extern void Dtool_ccoginvasion_BuildInstants(PyObject *module);

#if PY_MAJOR_VERSION >= 3 || !defined(NDEBUG)
#ifdef _WIN32
extern "C" __declspec(dllexport) PyObject *PyInit_ccoginvasion();
#elif __GNUC__ >= 4
extern "C" __attribute__((visibility("default"))) PyObject *PyInit_ccoginvasion();
#else
extern "C" PyObject *PyInit_ccoginvasion();
#endif
#endif
#if PY_MAJOR_VERSION < 3 || !defined(NDEBUG)
#ifdef _WIN32
extern "C" __declspec(dllexport) void initccoginvasion();
#elif __GNUC__ >= 4
extern "C" __attribute__((visibility("default"))) void initccoginvasion();
#else
extern "C" void initccoginvasion();
#endif
#endif

#if PY_MAJOR_VERSION >= 3
static struct PyModuleDef py_ccoginvasion_module = {
  PyModuleDef_HEAD_INIT,
  "ccoginvasion",
  nullptr,
  -1,
  nullptr,
  nullptr, nullptr, nullptr, nullptr
};

PyObject *PyInit_ccoginvasion() {
  PyImport_Import(PyUnicode_FromString("panda3d.core"));
  Dtool_ccoginvasion_RegisterTypes();
  Dtool_ccoginvasion_ResolveExternals();

  LibraryDef *defs[] = {&ccoginvasion_moddef, nullptr};

  PyObject *module = Dtool_PyModuleInitHelper(defs, &py_ccoginvasion_module);
  if (module != nullptr) {
    Dtool_ccoginvasion_BuildInstants(module);
  }
  return module;
}

#ifndef NDEBUG
void initccoginvasion() {
  PyErr_SetString(PyExc_ImportError, "ccoginvasion was compiled for Python " PY_VERSION ", which is incompatible with Python 2");
}
#endif
#else  // Python 2 case

void initccoginvasion() {
  PyImport_Import(PyUnicode_FromString("panda3d.core"));
  Dtool_ccoginvasion_RegisterTypes();
  Dtool_ccoginvasion_ResolveExternals();

  LibraryDef *defs[] = {&ccoginvasion_moddef, nullptr};

  PyObject *module = Dtool_PyModuleInitHelper(defs, "ccoginvasion");
  if (module != nullptr) {
    Dtool_ccoginvasion_BuildInstants(module);
  }
}

#ifndef NDEBUG
PyObject *PyInit_ccoginvasion() {
  PyErr_SetString(PyExc_ImportError, "ccoginvasion was compiled for Python " PY_VERSION ", which is incompatible with Python 3");
  return nullptr;
}
#endif
#endif

