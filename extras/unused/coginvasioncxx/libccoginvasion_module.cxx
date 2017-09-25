
#include "dtoolbase.h"
#include "interrogate_request.h"

#undef _POSIX_C_SOURCE
#include "py_panda.h"

extern LibraryDef libccoginvasion_moddef;
extern void Dtool_libccoginvasion_RegisterTypes();
extern void Dtool_libccoginvasion_ResolveExternals();
extern void Dtool_libccoginvasion_BuildInstants(PyObject *module);

#if PY_MAJOR_VERSION >= 3
static struct PyModuleDef py_libccoginvasion_module = {
  PyModuleDef_HEAD_INIT,
  "libccoginvasion",
  NULL,
  -1,
  NULL,
  NULL, NULL, NULL, NULL
};

#ifdef _WIN32
extern "C" __declspec(dllexport) PyObject *PyInit_libccoginvasion();
#elif __GNUC__ >= 4
extern "C" __attribute__((visibility("default"))) PyObject *PyInit_libccoginvasion();
#else
extern "C" PyObject *PyInit_libccoginvasion();
#endif

PyObject *PyInit_libccoginvasion() {
  Dtool_libccoginvasion_RegisterTypes();
  Dtool_libccoginvasion_ResolveExternals();

  LibraryDef *defs[] = {&libccoginvasion_moddef, NULL};

  PyObject *module = Dtool_PyModuleInitHelper(defs, &py_libccoginvasion_module);
  if (module != NULL) {
    Dtool_libccoginvasion_BuildInstants(module);
  }
  return module;
}

#else  // Python 2 case

#ifdef _WIN32
extern "C" __declspec(dllexport) void initlibccoginvasion();
#elif __GNUC__ >= 4
extern "C" __attribute__((visibility("default"))) void initlibccoginvasion();
#else
extern "C" void initlibccoginvasion();
#endif

void initlibccoginvasion() {
  Dtool_libccoginvasion_RegisterTypes();
  Dtool_libccoginvasion_ResolveExternals();

  LibraryDef *defs[] = {&libccoginvasion_moddef, NULL};

  PyObject *module = Dtool_PyModuleInitHelper(defs, "libccoginvasion");
  if (module != NULL) {
    Dtool_libccoginvasion_BuildInstants(module);
  }
}
#endif

