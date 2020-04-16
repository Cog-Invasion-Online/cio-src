
#include "dtoolbase.h"
#include "interrogate_request.h"

#include "py_panda.h"

extern const struct LibraryDef ccoginvasion_moddef;
extern void Dtool_ccoginvasion_RegisterTypes();
extern void Dtool_ccoginvasion_BuildInstants(PyObject *module);

#if PY_MAJOR_VERSION >= 3
extern "C" EXPORT_CLASS PyObject *PyInit_ccoginvasion();
#else
extern "C" EXPORT_CLASS void initccoginvasion();
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

  const LibraryDef *defs[] = {&ccoginvasion_moddef, nullptr};

  PyObject *module = Dtool_PyModuleInitHelper(defs, &py_ccoginvasion_module);
  if (module != nullptr) {
    Dtool_ccoginvasion_BuildInstants(module);
  }
  return module;
}

#else  // Python 2 case

void initccoginvasion() {
  PyImport_Import(PyUnicode_FromString("panda3d.core"));
  Dtool_ccoginvasion_RegisterTypes();

  const LibraryDef *defs[] = {&ccoginvasion_moddef, nullptr};

  PyObject *module = Dtool_PyModuleInitHelper(defs, "ccoginvasion");
  if (module != nullptr) {
    Dtool_ccoginvasion_BuildInstants(module);
  }
}
#endif

#line 1 "dtool/src/interrogatedb/py_panda.cxx"
/**
 * @file py_panda.cxx
 * @author drose
 * @date 2005-07-04
 */

#include "py_panda.h"
#include "config_interrogatedb.h"
#include "executionEnvironment.h"

#ifdef HAVE_PYTHON

using std::string;

/**

 */
void DTOOL_Call_ExtractThisPointerForType(PyObject *self, Dtool_PyTypedObject *classdef, void **answer) {
  if (DtoolInstance_Check(self)) {
    *answer = DtoolInstance_UPCAST(self, *classdef);
  } else {
    *answer = nullptr;
  }
}

/**
 * This is a support function for the Python bindings: it extracts the
 * underlying C++ pointer of the given type for a given Python object.  If it
 * was of the wrong type, raises an AttributeError.
 */
bool Dtool_Call_ExtractThisPointer(PyObject *self, Dtool_PyTypedObject &classdef, void **answer) {
  if (self == nullptr || !DtoolInstance_Check(self) || DtoolInstance_VOID_PTR(self) == nullptr) {
    Dtool_Raise_TypeError("C++ object is not yet constructed, or already destructed.");
    return false;
  }

  *answer = DtoolInstance_UPCAST(self, classdef);
  return true;
}

/**
 * The same thing as Dtool_Call_ExtractThisPointer, except that it performs
 * the additional check that the pointer is a non-const pointer.  This is
 * called by function wrappers for functions of which all overloads are non-
 * const, and saves a bit of code.
 *
 * The extra method_name argument is used in formatting the error message.
 */
bool Dtool_Call_ExtractThisPointer_NonConst(PyObject *self, Dtool_PyTypedObject &classdef,
                                            void **answer, const char *method_name) {

  if (self == nullptr || !DtoolInstance_Check(self) || DtoolInstance_VOID_PTR(self) == nullptr) {
    Dtool_Raise_TypeError("C++ object is not yet constructed, or already destructed.");
    return false;
  }

  if (DtoolInstance_IS_CONST(self)) {
    // All overloads of this function are non-const.
    PyErr_Format(PyExc_TypeError,
                 "Cannot call %s() on a const object.",
                 method_name);
    return false;
  }

  *answer = DtoolInstance_UPCAST(self, classdef);
  return true;
}

/**
 * Extracts the C++ pointer for an object, given its Python wrapper object,
 * for passing as the parameter to a C++ function.
 *
 * self is the Python wrapper object in question.
 *
 * classdef is the Python class wrapper for the C++ class in which the this
 * pointer should be returned.  (This may require an upcast operation, if self
 * is not already an instance of classdef.)
 *
 * param and function_name are used for error reporting only, and describe the
 * particular function and parameter index for this parameter.
 *
 * const_ok is true if the function is declared const and can therefore be
 * called with either a const or non-const "this" pointer, or false if the
 * function is declared non-const, and can therefore be called with only a
 * non-const "this" pointer.
 *
 * The return value is the C++ pointer that was extracted, or NULL if there
 * was a problem (in which case the Python exception state will have been
 * set).
 */
void *
DTOOL_Call_GetPointerThisClass(PyObject *self, Dtool_PyTypedObject *classdef,
                               int param, const string &function_name, bool const_ok,
                               bool report_errors) {
  // if (PyErr_Occurred()) { return nullptr; }
  if (self == nullptr) {
    if (report_errors) {
      return Dtool_Raise_TypeError("self is nullptr");
    }
    return nullptr;
  }

  if (DtoolInstance_Check(self)) {
    void *result = DtoolInstance_UPCAST(self, *classdef);

    if (result != nullptr) {
      if (const_ok || !DtoolInstance_IS_CONST(self)) {
        return result;
      }

      if (report_errors) {
        return PyErr_Format(PyExc_TypeError,
                            "%s() argument %d may not be const",
                            function_name.c_str(), param);
      }
      return nullptr;
    }
  }

  if (report_errors) {
    return Dtool_Raise_ArgTypeError(self, param, function_name.c_str(), classdef->_PyType.tp_name);
  }

  return nullptr;
}

/**
 * This is similar to a PyErr_Occurred() check, except that it also checks
 * Notify to see if an assertion has occurred.  If that is the case, then it
 * raises an AssertionError.
 *
 * Returns true if there is an active exception, false otherwise.
 *
 * In the NDEBUG case, this is simply a #define to _PyErr_OCCURRED() (which is
 * an undocumented inline version of PyErr_Occurred()).
 */
bool _Dtool_CheckErrorOccurred() {
  if (_PyErr_OCCURRED()) {
    return true;
  }
  if (Notify::ptr()->has_assert_failed()) {
    Dtool_Raise_AssertionError();
    return true;
  }
  return false;
}

/**
 * Raises an AssertionError containing the last thrown assert message, and
 * clears the assertion flag.  Returns NULL.
 */
PyObject *Dtool_Raise_AssertionError() {
  Notify *notify = Notify::ptr();
#if PY_MAJOR_VERSION >= 3
  PyObject *message = PyUnicode_FromString(notify->get_assert_error_message().c_str());
#else
  PyObject *message = PyString_FromString(notify->get_assert_error_message().c_str());
#endif
  PyErr_SetObject(PyExc_AssertionError, message);
  notify->clear_assert_failed();
  return nullptr;
}

/**
 * Raises a TypeError with the given message, and returns NULL.
 */
PyObject *Dtool_Raise_TypeError(const char *message) {
  PyErr_SetString(PyExc_TypeError, message);
  return nullptr;
}

/**
 * Raises a TypeError of the form: function_name() argument n must be type,
 * not type for a given object passed to a function.
 *
 * Always returns NULL so that it can be conveniently used as a return
 * expression for wrapper functions that return a PyObject pointer.
 */
PyObject *Dtool_Raise_ArgTypeError(PyObject *obj, int param, const char *function_name, const char *type_name) {
#if PY_MAJOR_VERSION >= 3
  PyObject *message = PyUnicode_FromFormat(
#else
  PyObject *message = PyString_FromFormat(
#endif
    "%s() argument %d must be %s, not %s",
    function_name, param, type_name,
    Py_TYPE(obj)->tp_name);

  PyErr_SetObject(PyExc_TypeError, message);
  return nullptr;
}

/**
 * Raises an AttributeError of the form: 'type' has no attribute 'attr'
 *
 * Always returns NULL so that it can be conveniently used as a return
 * expression for wrapper functions that return a PyObject pointer.
 */
PyObject *Dtool_Raise_AttributeError(PyObject *obj, const char *attribute) {
#if PY_MAJOR_VERSION >= 3
  PyObject *message = PyUnicode_FromFormat(
#else
  PyObject *message = PyString_FromFormat(
#endif
    "'%.100s' object has no attribute '%.200s'",
    Py_TYPE(obj)->tp_name, attribute);

  PyErr_SetObject(PyExc_AttributeError, message);
  return nullptr;
}

/**
 * Raises a TypeError of the form: Arguments must match: <list of overloads>
 *
 * However, in release builds, this instead is defined to a function that just
 * prints out a generic message, to help reduce the amount of strings in the
 * compiled library.
 *
 * Always returns NULL so that it can be conveniently used as a return
 * expression for wrapper functions that return a PyObject pointer.
 */
PyObject *_Dtool_Raise_BadArgumentsError() {
  return Dtool_Raise_TypeError("arguments do not match any function overload");
}

/**
 * Convenience method that checks for exceptions, and if one occurred, returns
 * NULL, otherwise Py_None.
 */
PyObject *_Dtool_Return_None() {
  if (UNLIKELY(_PyErr_OCCURRED())) {
    return nullptr;
  }
#ifndef NDEBUG
  if (UNLIKELY(Notify::ptr()->has_assert_failed())) {
    return Dtool_Raise_AssertionError();
  }
#endif
  Py_INCREF(Py_None);
  return Py_None;
}

/**
 * Convenience method that checks for exceptions, and if one occurred, returns
 * NULL, otherwise the given boolean value as a PyObject *.
 */
PyObject *Dtool_Return_Bool(bool value) {
  if (UNLIKELY(_PyErr_OCCURRED())) {
    return nullptr;
  }
#ifndef NDEBUG
  if (UNLIKELY(Notify::ptr()->has_assert_failed())) {
    return Dtool_Raise_AssertionError();
  }
#endif
  PyObject *result = (value ? Py_True : Py_False);
  Py_INCREF(result);
  return result;
}

/**
 * Convenience method that checks for exceptions, and if one occurred, returns
 * NULL, otherwise the given return value.  Its reference count is not
 * increased.
 */
PyObject *_Dtool_Return(PyObject *value) {
  if (UNLIKELY(_PyErr_OCCURRED())) {
    return nullptr;
  }
#ifndef NDEBUG
  if (UNLIKELY(Notify::ptr()->has_assert_failed())) {
    return Dtool_Raise_AssertionError();
  }
#endif
  return value;
}

#if PY_VERSION_HEX < 0x03040000
/**
 * This function converts an int value to the appropriate enum instance.
 */
static PyObject *Dtool_EnumType_New(PyTypeObject *subtype, PyObject *args, PyObject *kwds) {
  PyObject *arg;
  if (!Dtool_ExtractArg(&arg, args, kwds, "value")) {
    return PyErr_Format(PyExc_TypeError,
                        "%s() missing 1 required argument: 'value'",
                        subtype->tp_name);
  }

  if (Py_TYPE(arg) == subtype) {
    Py_INCREF(arg);
    return arg;
  }

  PyObject *value2member = PyDict_GetItemString(subtype->tp_dict, "_value2member_map_");
  nassertr_always(value2member != nullptr, nullptr);

  PyObject *member = PyDict_GetItem(value2member, arg);
  if (member != nullptr) {
    Py_INCREF(member);
    return member;
  }

  PyObject *repr = PyObject_Repr(arg);
  PyErr_Format(PyExc_ValueError, "%s is not a valid %s",
#if PY_MAJOR_VERSION >= 3
               PyUnicode_AS_STRING(repr),
#else
               PyString_AS_STRING(repr),
#endif
               subtype->tp_name);
  Py_DECREF(repr);
  return nullptr;
}

static PyObject *Dtool_EnumType_Str(PyObject *self) {
  PyObject *name = PyObject_GetAttrString(self, "name");
#if PY_MAJOR_VERSION >= 3
  PyObject *repr = PyUnicode_FromFormat("%s.%s", Py_TYPE(self)->tp_name, PyString_AS_STRING(name));
#else
  PyObject *repr = PyString_FromFormat("%s.%s", Py_TYPE(self)->tp_name, PyString_AS_STRING(name));
#endif
  Py_DECREF(name);
  return repr;
}

static PyObject *Dtool_EnumType_Repr(PyObject *self) {
  PyObject *name = PyObject_GetAttrString(self, "name");
  PyObject *value = PyObject_GetAttrString(self, "value");
#if PY_MAJOR_VERSION >= 3
  PyObject *repr = PyUnicode_FromFormat("<%s.%s: %ld>", Py_TYPE(self)->tp_name, PyString_AS_STRING(name), PyLongOrInt_AS_LONG(value));
#else
  PyObject *repr = PyString_FromFormat("<%s.%s: %ld>", Py_TYPE(self)->tp_name, PyString_AS_STRING(name), PyLongOrInt_AS_LONG(value));
#endif
  Py_DECREF(name);
  Py_DECREF(value);
  return repr;
}
#endif

/**
 * Creates a Python 3.4-style enum type.  Steals reference to 'names', which
 * should be a tuple of (name, value) pairs.
 */
PyTypeObject *Dtool_EnumType_Create(const char *name, PyObject *names, const char *module) {
  static PyObject *enum_class = nullptr;
#if PY_VERSION_HEX >= 0x03040000
  static PyObject *enum_meta = nullptr;
  static PyObject *enum_create = nullptr;
  if (enum_meta == nullptr) {
    PyObject *enum_module = PyImport_ImportModule("enum");
    nassertr_always(enum_module != nullptr, nullptr);

    enum_class = PyObject_GetAttrString(enum_module, "Enum");
    enum_meta = PyObject_GetAttrString(enum_module, "EnumMeta");
    enum_create = PyObject_GetAttrString(enum_meta, "_create_");
    nassertr(enum_meta != nullptr, nullptr);
  }

  PyObject *result = PyObject_CallFunction(enum_create, (char *)"OsN", enum_class, name, names);
  nassertr(result != nullptr, nullptr);
#else
  static PyObject *name_str;
  static PyObject *name_sunder_str;
  static PyObject *value_str;
  static PyObject *value_sunder_str;
  static PyObject *value2member_map_sunder_str;
  // Emulate something vaguely like the enum module.
  if (enum_class == nullptr) {
#if PY_MAJOR_VERSION >= 3
    name_str = PyUnicode_InternFromString("name");
    value_str = PyUnicode_InternFromString("value");
    name_sunder_str = PyUnicode_InternFromString("_name_");
    value_sunder_str = PyUnicode_InternFromString("_value_");
    value2member_map_sunder_str = PyUnicode_InternFromString("_value2member_map_");
#else
    name_str = PyString_InternFromString("name");
    value_str = PyString_InternFromString("value");
    name_sunder_str = PyString_InternFromString("_name_");
    value_sunder_str = PyString_InternFromString("_value_");
    value2member_map_sunder_str = PyString_InternFromString("_value2member_map_");
#endif
    PyObject *name_value_tuple = PyTuple_New(4);
    PyTuple_SET_ITEM(name_value_tuple, 0, name_str);
    PyTuple_SET_ITEM(name_value_tuple, 1, value_str);
    PyTuple_SET_ITEM(name_value_tuple, 2, name_sunder_str);
    PyTuple_SET_ITEM(name_value_tuple, 3, value_sunder_str);
    Py_INCREF(name_str);
    Py_INCREF(value_str);

    PyObject *slots_dict = PyDict_New();
    PyDict_SetItemString(slots_dict, "__slots__", name_value_tuple);
    Py_DECREF(name_value_tuple);

    enum_class = PyObject_CallFunction((PyObject *)&PyType_Type, (char *)"s()N", "Enum", slots_dict);
    nassertr(enum_class != nullptr, nullptr);
  }

  // Create a subclass of this generic Enum class we just created.
  PyObject *value2member = PyDict_New();
  PyObject *dict = PyDict_New();
  PyDict_SetItem(dict, value2member_map_sunder_str, value2member);
  PyObject *result = PyObject_CallFunction((PyObject *)&PyType_Type, (char *)"s(O)N", name, enum_class, dict);
  nassertr(result != nullptr, nullptr);

  ((PyTypeObject *)result)->tp_new = Dtool_EnumType_New;
  ((PyTypeObject *)result)->tp_str = Dtool_EnumType_Str;
  ((PyTypeObject *)result)->tp_repr = Dtool_EnumType_Repr;

  PyObject *empty_tuple = PyTuple_New(0);

  // Copy the names as instances of the above to the class dict, and create a
  // reverse mapping in the _value2member_map_ dict.
  Py_ssize_t size = PyTuple_GET_SIZE(names);
  for (Py_ssize_t i = 0; i < size; ++i) {
    PyObject *item = PyTuple_GET_ITEM(names, i);
    PyObject *name = PyTuple_GET_ITEM(item, 0);
    PyObject *value = PyTuple_GET_ITEM(item, 1);
    PyObject *member = PyType_GenericNew((PyTypeObject *)result, empty_tuple, nullptr);
    PyObject_SetAttr(member, name_str, name);
    PyObject_SetAttr(member, name_sunder_str, name);
    PyObject_SetAttr(member, value_str, value);
    PyObject_SetAttr(member, value_sunder_str, value);
    PyObject_SetAttr(result, name, member);
    PyDict_SetItem(value2member, value, member);
    Py_DECREF(member);
  }
  Py_DECREF(names);
  Py_DECREF(value2member);
  Py_DECREF(empty_tuple);
#endif

  if (module != nullptr) {
    PyObject *modstr = PyUnicode_FromString(module);
    PyObject_SetAttrString(result, "__module__", modstr);
    Py_DECREF(modstr);
  }
  nassertr(PyType_Check(result), nullptr);
  return (PyTypeObject *)result;
}

/**

 */
PyObject *DTool_CreatePyInstanceTyped(void *local_this_in, Dtool_PyTypedObject &known_class_type, bool memory_rules, bool is_const, int type_index) {
  // We can't do the NULL check here like in DTool_CreatePyInstance, since the
  // caller will have to get the type index to pass to this function to begin
  // with.  That code probably would have crashed by now if it was really NULL
  // for whatever reason.
  nassertr(local_this_in != nullptr, nullptr);

  // IF the class is possibly a run time typed object
  if (type_index > 0) {
    // get best fit class...
    Dtool_PyTypedObject *target_class = (Dtool_PyTypedObject *)TypeHandle::from_index(type_index).get_python_type();
    if (target_class != nullptr) {
      // cast to the type...
      void *new_local_this = target_class->_Dtool_DowncastInterface(local_this_in, &known_class_type);
      if (new_local_this != nullptr) {
        // ask class to allocate an instance..
        Dtool_PyInstDef *self = (Dtool_PyInstDef *) target_class->_PyType.tp_new(&target_class->_PyType, nullptr, nullptr);
        if (self != nullptr) {
          self->_ptr_to_object = new_local_this;
          self->_memory_rules = memory_rules;
          self->_is_const = is_const;
          // self->_signature = PY_PANDA_SIGNATURE;
          self->_My_Type = target_class;
          return (PyObject *)self;
        }
      }
    }
  }

  // if we get this far .. just wrap the thing in the known type ?? better
  // than aborting...I guess....
  Dtool_PyInstDef *self = (Dtool_PyInstDef *) known_class_type._PyType.tp_new(&known_class_type._PyType, nullptr, nullptr);
  if (self != nullptr) {
    self->_ptr_to_object = local_this_in;
    self->_memory_rules = memory_rules;
    self->_is_const = is_const;
    // self->_signature = PY_PANDA_SIGNATURE;
    self->_My_Type = &known_class_type;
  }
  return (PyObject *)self;
}

// DTool_CreatePyInstance .. wrapper function to finalize the existance of a
// general dtool py instance..
PyObject *DTool_CreatePyInstance(void *local_this, Dtool_PyTypedObject &in_classdef, bool memory_rules, bool is_const) {
  if (local_this == nullptr) {
    // This is actually a very common case, so let's allow this, but return
    // Py_None consistently.  This eliminates code in the wrappers.
    Py_INCREF(Py_None);
    return Py_None;
  }

  Dtool_PyTypedObject *classdef = &in_classdef;
  Dtool_PyInstDef *self = (Dtool_PyInstDef *) classdef->_PyType.tp_new(&classdef->_PyType, nullptr, nullptr);
  if (self != nullptr) {
    self->_ptr_to_object = local_this;
    self->_memory_rules = memory_rules;
    self->_is_const = is_const;
    self->_My_Type = classdef;
  }
  return (PyObject *)self;
}

/**
 * Returns a borrowed reference to the global type dictionary.
 */
Dtool_TypeMap *Dtool_GetGlobalTypeMap() {
  PyObject *capsule = PySys_GetObject((char *)"_interrogate_types");
  if (capsule != nullptr) {
    return (Dtool_TypeMap *)PyCapsule_GetPointer(capsule, nullptr);
  } else {
    Dtool_TypeMap *type_map = new Dtool_TypeMap;
    capsule = PyCapsule_New((void *)type_map, nullptr, nullptr);
    PySys_SetObject((char *)"_interrogate_types", capsule);
    Py_DECREF(capsule);
    return type_map;
  }
}

#if PY_MAJOR_VERSION >= 3
PyObject *Dtool_PyModuleInitHelper(const LibraryDef *defs[], PyModuleDef *module_def) {
#else
PyObject *Dtool_PyModuleInitHelper(const LibraryDef *defs[], const char *modulename) {
#endif
  // Check the version so we can print a helpful error if it doesn't match.
  string version = Py_GetVersion();

  if (version[0] != '0' + PY_MAJOR_VERSION ||
      version[2] != '0' + PY_MINOR_VERSION) {
    // Raise a helpful error message.  We can safely do this because the
    // signature and behavior for PyErr_SetString has remained consistent.
    std::ostringstream errs;
    errs << "this module was compiled for Python "
         << PY_MAJOR_VERSION << "." << PY_MINOR_VERSION << ", which is "
         << "incompatible with Python " << version.substr(0, 3);
    string error = errs.str();
    PyErr_SetString(PyExc_ImportError, error.c_str());
    return nullptr;
  }

  Dtool_TypeMap *type_map = Dtool_GetGlobalTypeMap();

  // the module level function inits....
  MethodDefmap functions;
  for (size_t i = 0; defs[i] != nullptr; i++) {
    const LibraryDef &def = *defs[i];

    // Accumulate method definitions.
    for (PyMethodDef *meth = def._methods; meth->ml_name != nullptr; meth++) {
      if (functions.find(meth->ml_name) == functions.end()) {
        functions[meth->ml_name] = meth;
      }
    }

    // Define exported types.
    const Dtool_TypeDef *types = def._types;
    if (types != nullptr) {
      while (types->name != nullptr) {
        (*type_map)[std::string(types->name)] = types->type;
        ++types;
      }
    }
  }

  // Resolve external types, in a second pass.
  for (size_t i = 0; defs[i] != nullptr; i++) {
    const LibraryDef &def = *defs[i];

    Dtool_TypeDef *types = def._external_types;
    if (types != nullptr) {
      while (types->name != nullptr) {
        auto it = type_map->find(std::string(types->name));
        if (it != type_map->end()) {
          types->type = it->second;
        } else {
          return PyErr_Format(PyExc_NameError, "name '%s' is not defined", types->name);
        }
        ++types;
      }
    }
  }

  PyMethodDef *newdef = new PyMethodDef[functions.size() + 1];
  MethodDefmap::iterator mi;
  int offset = 0;
  for (mi = functions.begin(); mi != functions.end(); mi++, offset++) {
    newdef[offset] = *mi->second;
  }
  newdef[offset].ml_doc = nullptr;
  newdef[offset].ml_name = nullptr;
  newdef[offset].ml_meth = nullptr;
  newdef[offset].ml_flags = 0;

#if PY_MAJOR_VERSION >= 3
  module_def->m_methods = newdef;
  PyObject *module = PyModule_Create(module_def);
#else
  PyObject *module = Py_InitModule((char *)modulename, newdef);
#endif

  if (module == nullptr) {
#if PY_MAJOR_VERSION >= 3
    return Dtool_Raise_TypeError("PyModule_Create returned NULL");
#else
    return Dtool_Raise_TypeError("Py_InitModule returned NULL");
#endif
  }

  // MAIN_DIR needs to be set very early; this seems like a convenient place
  // to do that.  Perhaps we'll find a better place for this in the future.
  static bool initialized_main_dir = false;
  if (!initialized_main_dir) {
    if (interrogatedb_cat.is_debug()) {
      // Good opportunity to print this out once, at startup.
      interrogatedb_cat.debug()
        << "Python " << version << "\n";
    }

    if (!ExecutionEnvironment::has_environment_variable("MAIN_DIR")) {
      // Grab the __main__ module.
      PyObject *main_module = PyImport_ImportModule("__main__");
      if (main_module == NULL) {
        interrogatedb_cat.warning() << "Unable to import __main__\n";
      }
      
      // Extract the __file__ attribute, if present.
      Filename main_dir;
      PyObject *file_attr = nullptr;
      if (main_module != nullptr) {
        file_attr = PyObject_GetAttrString(main_module, "__file__");
      }
      if (file_attr == nullptr) {
        // Must be running in the interactive interpreter.  Use the CWD.
        main_dir = ExecutionEnvironment::get_cwd();
      } else {
#if PY_MAJOR_VERSION >= 3
        Py_ssize_t length;
        wchar_t *buffer = PyUnicode_AsWideCharString(file_attr, &length);
        if (buffer != nullptr) {
          main_dir = Filename::from_os_specific_w(std::wstring(buffer, length));
          main_dir.make_absolute();
          main_dir = main_dir.get_dirname();
          PyMem_Free(buffer);
        }
#else
        char *buffer;
        Py_ssize_t length;
        if (PyString_AsStringAndSize(file_attr, &buffer, &length) != -1) {
          main_dir = Filename::from_os_specific(std::string(buffer, length));
          main_dir.make_absolute();
          main_dir = main_dir.get_dirname();
        }
#endif
        else {
          interrogatedb_cat.warning() << "Invalid string for __main__.__file__\n";
        }
      }
      ExecutionEnvironment::shadow_environment_variable("MAIN_DIR", main_dir.to_os_specific());
      PyErr_Clear();
    }
    initialized_main_dir = true;

    // Also, while we are at it, initialize the thread swap hook.
#if defined(HAVE_THREADS) && defined(SIMPLE_THREADS)
    global_thread_state_swap = PyThreadState_Swap;
#endif
  }

  PyModule_AddIntConstant(module, "Dtool_PyNativeInterface", 1);
  return module;
}

// HACK.... Be careful Dtool_BorrowThisReference This function can be used to
// grab the "THIS" pointer from an object and use it Required to support
// historical inheritance in the form of "is this instance of"..
PyObject *Dtool_BorrowThisReference(PyObject *self, PyObject *args) {
  PyObject *from_in = nullptr;
  PyObject *to_in = nullptr;
  if (PyArg_UnpackTuple(args, "Dtool_BorrowThisReference", 2, 2, &to_in, &from_in)) {

    if (DtoolInstance_Check(from_in) && DtoolInstance_Check(to_in)) {
      Dtool_PyInstDef *from = (Dtool_PyInstDef *) from_in;
      Dtool_PyInstDef *to = (Dtool_PyInstDef *) to_in;

      // if (PyObject_TypeCheck(to_in, Py_TYPE(from_in))) {
      if (from->_My_Type == to->_My_Type) {
        to->_memory_rules = false;
        to->_is_const = from->_is_const;
        to->_ptr_to_object = from->_ptr_to_object;

        Py_INCREF(Py_None);
        return Py_None;
      }

      return PyErr_Format(PyExc_TypeError, "types %s and %s do not match",
                          Py_TYPE(from)->tp_name, Py_TYPE(to)->tp_name);
    } else {
      return Dtool_Raise_TypeError("One of these does not appear to be DTOOL Instance ??");
    }
  }
  return nullptr;
}

// We do expose a dictionay for dtool classes .. this should be removed at
// some point..
EXPCL_PYPANDA PyObject *
Dtool_AddToDictionary(PyObject *self1, PyObject *args) {
  PyObject *self;
  PyObject *subject;
  PyObject *key;
  if (PyArg_ParseTuple(args, "OSO", &self, &key, &subject)) {
    PyObject *dict = ((PyTypeObject *)self)->tp_dict;
    if (dict == nullptr || !PyDict_Check(dict)) {
      return Dtool_Raise_TypeError("No dictionary On Object");
    } else {
      PyDict_SetItem(dict, key, subject);
    }
  }
  if (PyErr_Occurred()) {
    return nullptr;
  }
  Py_INCREF(Py_None);
  return Py_None;
}

/**
 * This is a support function for a synthesized __copy__() method from a C++
 * make_copy() method.
 */
PyObject *copy_from_make_copy(PyObject *self, PyObject *noargs) {
  PyObject *callable = PyObject_GetAttrString(self, "make_copy");
  if (callable == nullptr) {
    return nullptr;
  }
  PyObject *result = _PyObject_CallNoArg(callable);
  Py_DECREF(callable);
  return result;
}

/**
 * This is a support function for a synthesized __copy__() method from a C++
 * copy constructor.
 */
PyObject *copy_from_copy_constructor(PyObject *self, PyObject *noargs) {
  PyObject *callable = (PyObject *)Py_TYPE(self);
  return _PyObject_FastCall(callable, &self, 1);
}

/**
 * This is a support function for a synthesized __deepcopy__() method for any
 * class that has a __copy__() method.  The sythethic method simply invokes
 * __copy__().
 */
PyObject *map_deepcopy_to_copy(PyObject *self, PyObject *args) {
  PyObject *callable = PyObject_GetAttrString(self, "__copy__");
  if (callable == nullptr) {
    return nullptr;
  }
  PyObject *result = _PyObject_CallNoArg(callable);
  Py_DECREF(callable);
  return result;
}

/**
 * A more efficient version of PyArg_ParseTupleAndKeywords for the special
 * case where there is only a single PyObject argument.
 */
bool Dtool_ExtractArg(PyObject **result, PyObject *args, PyObject *kwds,
                      const char *keyword) {

  if (PyTuple_GET_SIZE(args) == 1) {
    if (kwds == nullptr || PyDict_GET_SIZE(kwds) == 0) {
      *result = PyTuple_GET_ITEM(args, 0);
      return true;
    }
  } else if (PyTuple_GET_SIZE(args) == 0) {
    PyObject *key;
    Py_ssize_t ppos = 0;
    if (kwds != nullptr && PyDict_GET_SIZE(kwds) == 1 &&
        PyDict_Next(kwds, &ppos, &key, result)) {
      // We got the item, we just need to make sure that it had the right key.
#if PY_VERSION_HEX >= 0x03060000
      return PyUnicode_CheckExact(key) && _PyUnicode_EqualToASCIIString(key, keyword);
#elif PY_MAJOR_VERSION >= 3
      return PyUnicode_CheckExact(key) && PyUnicode_CompareWithASCIIString(key, keyword) == 0;
#else
      return PyString_CheckExact(key) && strcmp(PyString_AS_STRING(key), keyword) == 0;
#endif
    }
  }

  return false;
}

/**
 * Variant of Dtool_ExtractArg that does not accept a keyword argument.
 */
bool Dtool_ExtractArg(PyObject **result, PyObject *args, PyObject *kwds) {
  if (PyTuple_GET_SIZE(args) == 1 &&
      (kwds == nullptr || PyDict_GET_SIZE(kwds) == 0)) {
    *result = PyTuple_GET_ITEM(args, 0);
    return true;
  }
  return false;
}

/**
 * A more efficient version of PyArg_ParseTupleAndKeywords for the special
 * case where there is only a single optional PyObject argument.
 *
 * Returns true if valid (including if there were 0 items), false if there was
 * an error, such as an invalid number of parameters.
 */
bool Dtool_ExtractOptionalArg(PyObject **result, PyObject *args, PyObject *kwds,
                              const char *keyword) {

  if (PyTuple_GET_SIZE(args) == 1) {
    if (kwds == nullptr || PyDict_GET_SIZE(kwds) == 0) {
      *result = PyTuple_GET_ITEM(args, 0);
      return true;
    }
  } else if (PyTuple_GET_SIZE(args) == 0) {
    if (kwds != nullptr && PyDict_GET_SIZE(kwds) == 1) {
      PyObject *key;
      Py_ssize_t ppos = 0;
      if (!PyDict_Next(kwds, &ppos, &key, result)) {
        return true;
      }

      // We got the item, we just need to make sure that it had the right key.
#if PY_VERSION_HEX >= 0x03060000
      return PyUnicode_CheckExact(key) && _PyUnicode_EqualToASCIIString(key, keyword);
#elif PY_MAJOR_VERSION >= 3
      return PyUnicode_CheckExact(key) && PyUnicode_CompareWithASCIIString(key, keyword) == 0;
#else
      return PyString_CheckExact(key) && strcmp(PyString_AS_STRING(key), keyword) == 0;
#endif
    } else {
      return true;
    }
  }

  return false;
}

/**
 * Variant of Dtool_ExtractOptionalArg that does not accept a keyword argument.
 */
bool Dtool_ExtractOptionalArg(PyObject **result, PyObject *args, PyObject *kwds) {
  if (kwds != nullptr && PyDict_GET_SIZE(kwds) != 0) {
    return false;
  }
  if (PyTuple_GET_SIZE(args) == 1) {
    *result = PyTuple_GET_ITEM(args, 0);
    return true;
  }
  return (PyTuple_GET_SIZE(args) == 0);
}

#endif  // HAVE_PYTHON
#line 1 "dtool/src/interrogatedb/py_compat.cxx"
/**
 * @file py_compat.cxx
 * @author rdb
 * @date 2017-12-03
 */

#include "py_compat.h"
#include "py_panda.h"

#ifdef HAVE_PYTHON

#if PY_MAJOR_VERSION < 3
/**
 * Given a long or int, returns a size_t, or raises an OverflowError if it is
 * out of range.
 */
size_t PyLongOrInt_AsSize_t(PyObject *vv) {
  if (PyInt_Check(vv)) {
    long value = PyInt_AS_LONG(vv);
    if (value < 0) {
      PyErr_SetString(PyExc_OverflowError,
                      "can't convert negative value to size_t");
      return (size_t)-1;
    }
    return (size_t)value;
  }

  if (!PyLong_Check(vv)) {
    Dtool_Raise_TypeError("a long or int was expected");
    return (size_t)-1;
  }

  size_t bytes;
  int one = 1;
  int res = _PyLong_AsByteArray((PyLongObject *)vv, (unsigned char *)&bytes,
                                SIZEOF_SIZE_T, (int)*(unsigned char*)&one, 0);

  if (res < 0) {
    return (size_t)res;
  } else {
    return bytes;
  }
}
#endif

#endif  // HAVE_PYTHON
#line 1 "dtool/src/interrogatedb/py_wrappers.cxx"
/**
 * @file py_wrappers.cxx
 * @author rdb
 * @date 2017-11-26
 */

#include "py_wrappers.h"

#ifdef HAVE_PYTHON

#if PY_VERSION_HEX >= 0x03040000
#define _COLLECTIONS_ABC "_collections_abc"
#elif PY_VERSION_HEX >= 0x03030000
#define _COLLECTIONS_ABC "collections.abc"
#else
#define _COLLECTIONS_ABC "_abcoll"
#endif

static void _register_collection(PyTypeObject *type, const char *abc) {
  PyObject *sys_modules = PyImport_GetModuleDict();
  if (sys_modules != nullptr) {
    PyObject *module = PyDict_GetItemString(sys_modules, _COLLECTIONS_ABC);
    if (module != nullptr) {
      PyObject *dict = PyModule_GetDict(module);
      if (module != nullptr) {
#if PY_MAJOR_VERSION >= 3
        static PyObject *register_str = PyUnicode_InternFromString("register");
#else
        static PyObject *register_str = PyString_InternFromString("register");
#endif
        PyObject *sequence = PyDict_GetItemString(dict, abc);
        if (sequence != nullptr) {
          if (PyObject_CallMethodObjArgs(sequence, register_str, (PyObject *)type, nullptr) == nullptr) {
            PyErr_Print();
          }
        }
      }
    }
  }
}

/**
 * These classes are returned from properties that require a subscript
 * interface, ie. something.children[i] = 3.
 */
static void Dtool_WrapperBase_dealloc(PyObject *self) {
  Dtool_WrapperBase *wrap = (Dtool_WrapperBase *)self;
  nassertv(wrap);
  Py_XDECREF(wrap->_self);
  Py_TYPE(self)->tp_free(self);
}

static PyObject *Dtool_WrapperBase_repr(PyObject *self) {
  Dtool_WrapperBase *wrap = (Dtool_WrapperBase *)self;
  nassertr(wrap, nullptr);

  PyObject *repr = PyObject_Repr(wrap->_self);
  PyObject *result;
#if PY_MAJOR_VERSION >= 3
  result = PyUnicode_FromFormat("<%s[] of %s>", wrap->_name, PyUnicode_AsUTF8(repr));
#else
  result = PyString_FromFormat("<%s[] of %s>", wrap->_name, PyString_AS_STRING(repr));
#endif
  Py_DECREF(repr);
  return result;
}

static PyObject *Dtool_SequenceWrapper_repr(PyObject *self) {
  Dtool_SequenceWrapper *wrap = (Dtool_SequenceWrapper *)self;
  nassertr(wrap, nullptr);

  Py_ssize_t len = -1;
  if (wrap->_len_func != nullptr) {
    len = wrap->_len_func(wrap->_base._self);
  }

  if (len < 0) {
    PyErr_Clear();
    return Dtool_WrapperBase_repr(self);
  }

  PyObject *repr = PyObject_Repr(wrap->_base._self);
  PyObject *result;
#if PY_MAJOR_VERSION >= 3
  result = PyUnicode_FromFormat("<%s[%zd] of %s>", wrap->_base._name, len, PyUnicode_AsUTF8(repr));
#else
  result = PyString_FromFormat("<%s[%zd] of %s>", wrap->_base._name, len, PyString_AS_STRING(repr));
#endif
  Py_DECREF(repr);
  return result;
}

static Py_ssize_t Dtool_SequenceWrapper_length(PyObject *self) {
  Dtool_SequenceWrapper *wrap = (Dtool_SequenceWrapper *)self;
  nassertr(wrap, -1);
  if (wrap->_len_func != nullptr) {
    return wrap->_len_func(wrap->_base._self);
  } else {
    Dtool_Raise_TypeError("property does not support len()");
    return -1;
  }
}

static PyObject *Dtool_SequenceWrapper_getitem(PyObject *self, Py_ssize_t index) {
  Dtool_SequenceWrapper *wrap = (Dtool_SequenceWrapper *)self;
  nassertr(wrap, nullptr);
  nassertr(wrap->_getitem_func, nullptr);
  return wrap->_getitem_func(wrap->_base._self, index);
}

/**
 * Implementation of (x in property)
 */
static int Dtool_SequenceWrapper_contains(PyObject *self, PyObject *value) {
  Dtool_SequenceWrapper *wrap = (Dtool_SequenceWrapper *)self;
  nassertr(wrap, -1);
  nassertr(wrap->_len_func, -1);
  nassertr(wrap->_getitem_func, -1);

  Py_ssize_t length = wrap->_len_func(wrap->_base._self);

  // Iterate through the items, invoking the equality function for each, until
  // we have found the matching one.
  for (Py_ssize_t index = 0; index < length; ++index) {
    PyObject *item = wrap->_getitem_func(wrap->_base._self, index);
    if (item != nullptr) {
      int cmp = PyObject_RichCompareBool(item, value, Py_EQ);
      if (cmp > 0) {
        return 1;
      }
      if (cmp < 0) {
        return -1;
      }
    } else {
      return -1;
    }
  }
  return 0;
}

/**
 * Implementation of property.index(x) which returns the index of the first
 * occurrence of x in the sequence, or raises a ValueError if it isn't found.
 */
static PyObject *Dtool_SequenceWrapper_index(PyObject *self, PyObject *value) {
  Dtool_SequenceWrapper *wrap = (Dtool_SequenceWrapper *)self;
  nassertr(wrap, nullptr);
  nassertr(wrap->_len_func, nullptr);
  nassertr(wrap->_getitem_func, nullptr);

  Py_ssize_t length = wrap->_len_func(wrap->_base._self);

  // Iterate through the items, invoking the equality function for each, until
  // we have found the right one.
  for (Py_ssize_t index = 0; index < length; ++index) {
    PyObject *item = wrap->_getitem_func(wrap->_base._self, index);
    if (item != nullptr) {
      int cmp = PyObject_RichCompareBool(item, value, Py_EQ);
      if (cmp > 0) {
        return Dtool_WrapValue(index);
      }
      if (cmp < 0) {
        return nullptr;
      }
    } else {
      return nullptr;
    }
  }
  // Not found, raise ValueError.
  return PyErr_Format(PyExc_ValueError, "%s.index() did not find value", wrap->_base._name);
}

/**
 * Implementation of property.count(x) which returns the number of occurrences
 * of x in the sequence.
 */
static PyObject *Dtool_SequenceWrapper_count(PyObject *self, PyObject *value) {
  Dtool_SequenceWrapper *wrap = (Dtool_SequenceWrapper *)self;
  nassertr(wrap, nullptr);
  Py_ssize_t index = 0;
  if (wrap->_len_func != nullptr) {
    index = wrap->_len_func(wrap->_base._self);
  } else {
    return Dtool_Raise_TypeError("property does not support count()");
  }
  // Iterate through the items, invoking the == operator for each.
  long count = 0;
  nassertr(wrap->_getitem_func, nullptr);
  while (index > 0) {
    --index;
    PyObject *item = wrap->_getitem_func(wrap->_base._self, index);
    if (item == nullptr) {
      return nullptr;
    }
    int cmp = PyObject_RichCompareBool(item, value, Py_EQ);
    if (cmp > 0) {
      ++count;
    }
    if (cmp < 0) {
      return nullptr;
    }
  }
#if PY_MAJOR_VERSION >= 3
  return PyLong_FromLong(count);
#else
  return PyInt_FromLong(count);
#endif
}

/**
 * Implementation of `property[i] = x`
 */
static int Dtool_MutableSequenceWrapper_setitem(PyObject *self, Py_ssize_t index, PyObject *value) {
  Dtool_MutableSequenceWrapper *wrap = (Dtool_MutableSequenceWrapper *)self;
  nassertr(wrap, -1);
  if (wrap->_setitem_func != nullptr) {
    return wrap->_setitem_func(wrap->_base._self, index, value);
  } else {
    Dtool_Raise_TypeError("property does not support item assignment");
    return -1;
  }
}

/**
 * Implementation of property.clear() which removes all elements in the
 * sequence, starting with the last.
 */
static PyObject *Dtool_MutableSequenceWrapper_clear(PyObject *self, PyObject *) {
  Dtool_MutableSequenceWrapper *wrap = (Dtool_MutableSequenceWrapper *)self;
  nassertr(wrap, nullptr);
  Py_ssize_t index = 0;
  if (wrap->_len_func != nullptr && wrap->_setitem_func != nullptr) {
    index = wrap->_len_func(wrap->_base._self);
  } else {
    return Dtool_Raise_TypeError("property does not support clear()");
  }

  // Iterate through the items, invoking the delete function for each.  We do
  // this in reverse order, which may be more efficient.
  while (index > 0) {
    --index;
    if (wrap->_setitem_func(wrap->_base._self, index, nullptr) != 0) {
      return nullptr;
    }
  }
  Py_INCREF(Py_None);
  return Py_None;
}

/**
 * Implementation of property.remove(x) which removes the first occurrence of
 * x in the sequence, or raises a ValueError if it isn't found.
 */
static PyObject *Dtool_MutableSequenceWrapper_remove(PyObject *self, PyObject *value) {
  Dtool_MutableSequenceWrapper *wrap = (Dtool_MutableSequenceWrapper *)self;
  nassertr(wrap, nullptr);
  Py_ssize_t length = 0;
  if (wrap->_len_func != nullptr && wrap->_setitem_func != nullptr) {
    length = wrap->_len_func(wrap->_base._self);
  } else {
    return Dtool_Raise_TypeError("property does not support remove()");
  }

  // Iterate through the items, invoking the equality function for each, until
  // we have found the right one.
  nassertr(wrap->_getitem_func, nullptr);
  for (Py_ssize_t index = 0; index < length; ++index) {
    PyObject *item = wrap->_getitem_func(wrap->_base._self, index);
    if (item != nullptr) {
      int cmp = PyObject_RichCompareBool(item, value, Py_EQ);
      if (cmp > 0) {
        if (wrap->_setitem_func(wrap->_base._self, index, nullptr) == 0) {
          Py_INCREF(Py_None);
          return Py_None;
        } else {
          return nullptr;
        }
      }
      if (cmp < 0) {
        return nullptr;
      }
    } else {
      return nullptr;
    }
  }
  // Not found, raise ValueError.
  return PyErr_Format(PyExc_ValueError, "%s.remove() did not find value", wrap->_base._name);
}

/**
 * Implementation of property.pop([i=-1]) which returns and removes the
 * element at the indicated index in the sequence.  If no index is provided,
 * it removes from the end of the list.
 */
static PyObject *Dtool_MutableSequenceWrapper_pop(PyObject *self, PyObject *args) {
  Dtool_MutableSequenceWrapper *wrap = (Dtool_MutableSequenceWrapper *)self;
  nassertr(wrap, nullptr);
  if (wrap->_getitem_func == nullptr || wrap->_setitem_func == nullptr ||
      wrap->_len_func == nullptr) {
    return Dtool_Raise_TypeError("property does not support pop()");
  }

  Py_ssize_t length = wrap->_len_func(wrap->_base._self);
  Py_ssize_t index;
  switch (PyTuple_GET_SIZE(args)) {
  case 0:
    index = length - 1;
    break;
  case 1:
    index = PyNumber_AsSsize_t(PyTuple_GET_ITEM(args, 0), PyExc_IndexError);
    if (index == -1 && _PyErr_OCCURRED()) {
      return nullptr;
    }
    if (index < 0) {
      index += length;
    }
    break;
  default:
    return Dtool_Raise_TypeError("pop([i=-1]) takes 0 or 1 arguments");
  }

  if (length <= 0) {
    return PyErr_Format(PyExc_IndexError, "%s.pop() from empty sequence", wrap->_base._name);
  }

  // Index error will be caught by getitem_func.
  PyObject *value = wrap->_getitem_func(wrap->_base._self, index);
  if (value != nullptr) {
    if (wrap->_setitem_func(wrap->_base._self, index, nullptr) != 0) {
      return nullptr;
    }
    return value;
  }
  return nullptr;
}

/**
 * Implementation of property.append(x) which is an alias for
 * property.insert(len(property), x).
 */
static PyObject *Dtool_MutableSequenceWrapper_append(PyObject *self, PyObject *arg) {
  Dtool_MutableSequenceWrapper *wrap = (Dtool_MutableSequenceWrapper *)self;
  nassertr(wrap, nullptr);
  if (wrap->_insert_func == nullptr) {
    return Dtool_Raise_TypeError("property does not support append()");
  }
  return wrap->_insert_func(wrap->_base._self, (size_t)-1, arg);
}

/**
 * Implementation of property.insert(i, x) which inserts the given item at the
 * given position.
 */
static PyObject *Dtool_MutableSequenceWrapper_insert(PyObject *self, PyObject *args) {
  Dtool_MutableSequenceWrapper *wrap = (Dtool_MutableSequenceWrapper *)self;
  nassertr(wrap, nullptr);
  if (wrap->_insert_func == nullptr) {
    return Dtool_Raise_TypeError("property does not support insert()");
  }
  if (PyTuple_GET_SIZE(args) != 2) {
    return Dtool_Raise_TypeError("insert() takes exactly 2 arguments");
  }
  Py_ssize_t index = PyNumber_AsSsize_t(PyTuple_GET_ITEM(args, 0), PyExc_IndexError);
  if (index == -1 && _PyErr_OCCURRED()) {
    return nullptr;
  }
  if (index < 0) {
    if (wrap->_len_func != nullptr) {
      index += wrap->_len_func(wrap->_base._self);
    } else {
      return PyErr_Format(PyExc_TypeError, "%s.insert() does not support negative indices", wrap->_base._name);
    }
  }
  return wrap->_insert_func(wrap->_base._self, (ssize_t)std::max(index, (Py_ssize_t)0), PyTuple_GET_ITEM(args, 1));
}

/**
 * Implementation of property.extend(seq) which is equivalent to:
 * @code
 * for x in seq:
 *   property.append(seq)
 * @endcode
 */
static PyObject *Dtool_MutableSequenceWrapper_extend(PyObject *self, PyObject *arg) {
  Dtool_MutableSequenceWrapper *wrap = (Dtool_MutableSequenceWrapper *)self;
  nassertr(wrap, nullptr);
  if (wrap->_insert_func == nullptr) {
    return Dtool_Raise_TypeError("property does not support extend()");
  }
  PyObject *iter = PyObject_GetIter(arg);
  if (iter == nullptr) {
    return nullptr;
  }
  PyObject *next = PyIter_Next(iter);
  PyObject *retval = nullptr;
  while (next != nullptr) {
    retval = wrap->_insert_func(wrap->_base._self, (size_t)-1, next);
    Py_DECREF(next);
    if (retval == nullptr) {
      Py_DECREF(iter);
      return nullptr;
    }
    Py_DECREF(retval);
    next = PyIter_Next(iter);
  }

  Py_DECREF(iter);
  Py_INCREF(Py_None);
  return Py_None;
}

/**
 * Implementation of `x in mapping`.
 */
static int Dtool_MappingWrapper_contains(PyObject *self, PyObject *key) {
  Dtool_MappingWrapper *wrap = (Dtool_MappingWrapper *)self;
  nassertr(wrap, -1);
  nassertr(wrap->_getitem_func, -1);
  PyObject *value = wrap->_getitem_func(wrap->_base._self, key);
  if (value != nullptr) {
    Py_DECREF(value);
    return 1;
  } else if (_PyErr_OCCURRED() == PyExc_KeyError ||
             _PyErr_OCCURRED() == PyExc_TypeError) {
    PyErr_Clear();
    return 0;
  } else {
    return -1;
  }
}

static PyObject *Dtool_MappingWrapper_getitem(PyObject *self, PyObject *key) {
  Dtool_MappingWrapper *wrap = (Dtool_MappingWrapper *)self;
  nassertr(wrap, nullptr);
  nassertr(wrap->_getitem_func, nullptr);
  return wrap->_getitem_func(wrap->_base._self, key);
}

/**
 * Implementation of iter(property) that returns an iterable over all the
 * keys.
 */
static PyObject *Dtool_MappingWrapper_iter(PyObject *self) {
  Dtool_MappingWrapper *wrap = (Dtool_MappingWrapper *)self;
  nassertr(wrap, nullptr);

  if (wrap->_keys._len_func == nullptr || wrap->_keys._getitem_func == nullptr) {
    return PyErr_Format(PyExc_TypeError, "%s is not iterable", wrap->_base._name);
  }

  Dtool_SequenceWrapper *keys = Dtool_NewSequenceWrapper(wrap->_base._self, wrap->_base._name);
  if (keys != nullptr) {
    keys->_len_func = wrap->_keys._len_func;
    keys->_getitem_func = wrap->_keys._getitem_func;
    return PySeqIter_New((PyObject *)keys);
  } else {
    return nullptr;
  }
}

/**
 * Implementation of property.get(key[,def=None]) which returns the value with
 * the given key in the mapping, or the given default value (which defaults to
 * None) if the key isn't found in the mapping.
 */
static PyObject *Dtool_MappingWrapper_get(PyObject *self, PyObject *args) {
  Dtool_MappingWrapper *wrap = (Dtool_MappingWrapper *)self;
  nassertr(wrap, nullptr);
  nassertr(wrap->_getitem_func, nullptr);
  Py_ssize_t size = PyTuple_GET_SIZE(args);
  if (size != 1 && size != 2) {
    return PyErr_Format(PyExc_TypeError, "%s.get() takes 1 or 2 arguments", wrap->_base._name);
  }
  PyObject *defvalue = Py_None;
  if (size >= 2) {
    defvalue = PyTuple_GET_ITEM(args, 1);
  }
  PyObject *key = PyTuple_GET_ITEM(args, 0);
  PyObject *value = wrap->_getitem_func(wrap->_base._self, key);
  if (value != nullptr) {
    return value;
  } else if (_PyErr_OCCURRED() == PyExc_KeyError) {
    PyErr_Clear();
    Py_INCREF(defvalue);
    return defvalue;
  } else {
    return nullptr;
  }
}

/**
 * This is returned by mapping.keys().
 */
static PyObject *Dtool_MappingWrapper_Keys_repr(PyObject *self) {
  Dtool_WrapperBase *wrap = (Dtool_WrapperBase *)self;
  nassertr(wrap, nullptr);

  PyObject *repr = PyObject_Repr(wrap->_self);
  PyObject *result;
#if PY_MAJOR_VERSION >= 3
  result = PyUnicode_FromFormat("<%s.keys() of %s>", wrap->_name, PyUnicode_AsUTF8(repr));
#else
  result = PyString_FromFormat("<%s.keys() of %s>", wrap->_name, PyString_AS_STRING(repr));
#endif
  Py_DECREF(repr);
  return result;
}

/**
 * Implementation of property.keys(...) that returns a view of all the keys.
 */
static PyObject *Dtool_MappingWrapper_keys(PyObject *self, PyObject *) {
  Dtool_MappingWrapper *wrap = (Dtool_MappingWrapper *)self;
  nassertr(wrap, nullptr);

  if (wrap->_keys._len_func == nullptr || wrap->_keys._getitem_func == nullptr) {
    return Dtool_Raise_TypeError("property does not support keys()");
  }

  Dtool_MappingWrapper *keys = (Dtool_MappingWrapper *)PyObject_MALLOC(sizeof(Dtool_MappingWrapper));
  if (keys == nullptr) {
    return PyErr_NoMemory();
  }

  static PySequenceMethods seq_methods = {
    Dtool_SequenceWrapper_length,
    nullptr, // sq_concat
    nullptr, // sq_repeat
    Dtool_SequenceWrapper_getitem,
    nullptr, // sq_slice
    nullptr, // sq_ass_item
    nullptr, // sq_ass_slice
    Dtool_SequenceWrapper_contains,
    nullptr, // sq_inplace_concat
    nullptr, // sq_inplace_repeat
  };

  static PyTypeObject wrapper_type = {
    PyVarObject_HEAD_INIT(nullptr, 0)
    "sequence wrapper",
    sizeof(Dtool_SequenceWrapper),
    0, // tp_itemsize
    Dtool_WrapperBase_dealloc,
    0, // tp_vectorcall_offset
    nullptr, // tp_getattr
    nullptr, // tp_setattr
    nullptr, // tp_compare
    Dtool_MappingWrapper_Keys_repr,
    nullptr, // tp_as_number
    &seq_methods,
    nullptr, // tp_as_mapping
    nullptr, // tp_hash
    nullptr, // tp_call
    nullptr, // tp_str
    PyObject_GenericGetAttr,
    PyObject_GenericSetAttr,
    nullptr, // tp_as_buffer
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_CHECKTYPES,
    nullptr, // tp_doc
    nullptr, // tp_traverse
    nullptr, // tp_clear
    nullptr, // tp_richcompare
    0, // tp_weaklistoffset
    PySeqIter_New,
    nullptr, // tp_iternext
    nullptr, // tp_methods
    nullptr, // tp_members
    nullptr, // tp_getset
    nullptr, // tp_base
    nullptr, // tp_dict
    nullptr, // tp_descr_get
    nullptr, // tp_descr_set
    0, // tp_dictoffset
    nullptr, // tp_init
    PyType_GenericAlloc,
    nullptr, // tp_new
    PyObject_Del,
    nullptr, // tp_is_gc
    nullptr, // tp_bases
    nullptr, // tp_mro
    nullptr, // tp_cache
    nullptr, // tp_subclasses
    nullptr, // tp_weaklist
    nullptr, // tp_del
    0, // tp_version_tag,
#if PY_VERSION_HEX >= 0x03040000
    nullptr, // tp_finalize
#endif
#if PY_VERSION_HEX >= 0x03080000
    nullptr, // tp_vectorcall
#endif
  };

  static bool registered = false;
  if (!registered) {
    registered = true;

    if (PyType_Ready(&wrapper_type) < 0) {
      return nullptr;
    }

    // If the collections.abc module is loaded, register this as a subclass.
    _register_collection((PyTypeObject *)&wrapper_type, "MappingView");
  }

  (void)PyObject_INIT(keys, &wrapper_type);
  Py_XINCREF(wrap->_base._self);
  keys->_base._self = wrap->_base._self;
  keys->_base._name = wrap->_base._name;
  keys->_keys._len_func = wrap->_keys._len_func;
  keys->_keys._getitem_func = wrap->_keys._getitem_func;
  keys->_getitem_func = wrap->_getitem_func;
  keys->_setitem_func = nullptr;
  return (PyObject *)keys;
}

/**
 * This is returned by mapping.values().
 */
static PyObject *Dtool_MappingWrapper_Values_repr(PyObject *self) {
  Dtool_WrapperBase *wrap = (Dtool_WrapperBase *)self;
  nassertr(wrap, nullptr);

  PyObject *repr = PyObject_Repr(wrap->_self);
  PyObject *result;
#if PY_MAJOR_VERSION >= 3
  result = PyUnicode_FromFormat("<%s.values() of %s>", wrap->_name, PyUnicode_AsUTF8(repr));
#else
  result = PyString_FromFormat("<%s.values() of %s>", wrap->_name, PyString_AS_STRING(repr));
#endif
  Py_DECREF(repr);
  return result;
}

static PyObject *Dtool_MappingWrapper_Values_getitem(PyObject *self, Py_ssize_t index) {
  Dtool_MappingWrapper *wrap = (Dtool_MappingWrapper *)self;
  nassertr(wrap, nullptr);
  nassertr(wrap->_keys._getitem_func, nullptr);

  PyObject *key = wrap->_keys._getitem_func(wrap->_base._self, index);
  if (key != nullptr) {
    PyObject *value = wrap->_getitem_func(wrap->_base._self, key);
    Py_DECREF(key);
    return value;
  }
  return nullptr;
}

/**
 * Implementation of property.values(...) that returns a view of the values.
 */
static PyObject *Dtool_MappingWrapper_values(PyObject *self, PyObject *) {
  Dtool_MappingWrapper *wrap = (Dtool_MappingWrapper *)self;
  nassertr(wrap, nullptr);
  nassertr(wrap->_getitem_func, nullptr);

  if (wrap->_keys._len_func == nullptr || wrap->_keys._getitem_func == nullptr) {
    return Dtool_Raise_TypeError("property does not support values()");
  }

  Dtool_MappingWrapper *values = (Dtool_MappingWrapper *)PyObject_MALLOC(sizeof(Dtool_MappingWrapper));
  if (values == nullptr) {
    return PyErr_NoMemory();
  }

  static PySequenceMethods seq_methods = {
    Dtool_SequenceWrapper_length,
    nullptr, // sq_concat
    nullptr, // sq_repeat
    Dtool_MappingWrapper_Values_getitem,
    nullptr, // sq_slice
    nullptr, // sq_ass_item
    nullptr, // sq_ass_slice
    Dtool_MappingWrapper_contains,
    nullptr, // sq_inplace_concat
    nullptr, // sq_inplace_repeat
  };

  static PyTypeObject wrapper_type = {
    PyVarObject_HEAD_INIT(nullptr, 0)
    "sequence wrapper",
    sizeof(Dtool_MappingWrapper),
    0, // tp_itemsize
    Dtool_WrapperBase_dealloc,
    0, // tp_vectorcall_offset
    nullptr, // tp_getattr
    nullptr, // tp_setattr
    nullptr, // tp_compare
    Dtool_MappingWrapper_Values_repr,
    nullptr, // tp_as_number
    &seq_methods,
    nullptr, // tp_as_mapping
    nullptr, // tp_hash
    nullptr, // tp_call
    nullptr, // tp_str
    PyObject_GenericGetAttr,
    PyObject_GenericSetAttr,
    nullptr, // tp_as_buffer
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_CHECKTYPES,
    nullptr, // tp_doc
    nullptr, // tp_traverse
    nullptr, // tp_clear
    nullptr, // tp_richcompare
    0, // tp_weaklistoffset
    PySeqIter_New,
    nullptr, // tp_iternext
    nullptr, // tp_methods
    nullptr, // tp_members
    nullptr, // tp_getset
    nullptr, // tp_base
    nullptr, // tp_dict
    nullptr, // tp_descr_get
    nullptr, // tp_descr_set
    0, // tp_dictoffset
    nullptr, // tp_init
    PyType_GenericAlloc,
    nullptr, // tp_new
    PyObject_Del,
    nullptr, // tp_is_gc
    nullptr, // tp_bases
    nullptr, // tp_mro
    nullptr, // tp_cache
    nullptr, // tp_subclasses
    nullptr, // tp_weaklist
    nullptr, // tp_del
    0, // tp_version_tag,
#if PY_VERSION_HEX >= 0x03040000
    nullptr, // tp_finalize
#endif
#if PY_VERSION_HEX >= 0x03080000
    nullptr, // tp_vectorcall
#endif
  };

  static bool registered = false;
  if (!registered) {
    registered = true;

    if (PyType_Ready(&wrapper_type) < 0) {
      return nullptr;
    }

    // If the collections.abc module is loaded, register this as a subclass.
    _register_collection((PyTypeObject *)&wrapper_type, "ValuesView");
  }

  (void)PyObject_INIT(values, &wrapper_type);
  Py_XINCREF(wrap->_base._self);
  values->_base._self = wrap->_base._self;
  values->_base._name = wrap->_base._name;
  values->_keys._len_func = wrap->_keys._len_func;
  values->_keys._getitem_func = wrap->_keys._getitem_func;
  values->_getitem_func = wrap->_getitem_func;
  values->_setitem_func = nullptr;
  return (PyObject *)values;
}

/**
 * This is returned by mapping.items().
 */
static PyObject *Dtool_MappingWrapper_Items_repr(PyObject *self) {
  Dtool_WrapperBase *wrap = (Dtool_WrapperBase *)self;
  nassertr(wrap, nullptr);

  PyObject *repr = PyObject_Repr(wrap->_self);
  PyObject *result;
#if PY_MAJOR_VERSION >= 3
  result = PyUnicode_FromFormat("<%s.items() of %s>", wrap->_name, PyUnicode_AsUTF8(repr));
#else
  result = PyString_FromFormat("<%s.items() of %s>", wrap->_name, PyString_AS_STRING(repr));
#endif
  Py_DECREF(repr);
  return result;
}

static PyObject *Dtool_MappingWrapper_Items_getitem(PyObject *self, Py_ssize_t index) {
  Dtool_MappingWrapper *wrap = (Dtool_MappingWrapper *)self;
  nassertr(wrap, nullptr);
  nassertr(wrap->_keys._getitem_func, nullptr);

  PyObject *key = wrap->_keys._getitem_func(wrap->_base._self, index);
  if (key != nullptr) {
    PyObject *value = wrap->_getitem_func(wrap->_base._self, key);
    if (value != nullptr) {
      // PyTuple_SET_ITEM steals the reference.
      PyObject *item = PyTuple_New(2);
      PyTuple_SET_ITEM(item, 0, key);
      PyTuple_SET_ITEM(item, 1, value);
      return item;
    } else {
      Py_DECREF(key);
    }
  }
  return nullptr;
}

/**
 * Implementation of property.items(...) that returns an iterable yielding a
 * `(key, value)` tuple for every item.
 */
static PyObject *Dtool_MappingWrapper_items(PyObject *self, PyObject *) {
  Dtool_MappingWrapper *wrap = (Dtool_MappingWrapper *)self;
  nassertr(wrap, nullptr);
  nassertr(wrap->_getitem_func, nullptr);

  if (wrap->_keys._len_func == nullptr || wrap->_keys._getitem_func == nullptr) {
    return Dtool_Raise_TypeError("property does not support items()");
  }

  Dtool_MappingWrapper *items = (Dtool_MappingWrapper *)PyObject_MALLOC(sizeof(Dtool_MappingWrapper));
  if (items == nullptr) {
    return PyErr_NoMemory();
  }

  static PySequenceMethods seq_methods = {
    Dtool_SequenceWrapper_length,
    nullptr, // sq_concat
    nullptr, // sq_repeat
    Dtool_MappingWrapper_Items_getitem,
    nullptr, // sq_slice
    nullptr, // sq_ass_item
    nullptr, // sq_ass_slice
    Dtool_MappingWrapper_contains,
    nullptr, // sq_inplace_concat
    nullptr, // sq_inplace_repeat
  };

  static PyTypeObject wrapper_type = {
    PyVarObject_HEAD_INIT(nullptr, 0)
    "sequence wrapper",
    sizeof(Dtool_MappingWrapper),
    0, // tp_itemsize
    Dtool_WrapperBase_dealloc,
    0, // tp_vectorcall_offset
    nullptr, // tp_getattr
    nullptr, // tp_setattr
    nullptr, // tp_compare
    Dtool_MappingWrapper_Items_repr,
    nullptr, // tp_as_number
    &seq_methods,
    nullptr, // tp_as_mapping
    nullptr, // tp_hash
    nullptr, // tp_call
    nullptr, // tp_str
    PyObject_GenericGetAttr,
    PyObject_GenericSetAttr,
    nullptr, // tp_as_buffer
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_CHECKTYPES,
    nullptr, // tp_doc
    nullptr, // tp_traverse
    nullptr, // tp_clear
    nullptr, // tp_richcompare
    0, // tp_weaklistoffset
    PySeqIter_New,
    nullptr, // tp_iternext
    nullptr, // tp_methods
    nullptr, // tp_members
    nullptr, // tp_getset
    nullptr, // tp_base
    nullptr, // tp_dict
    nullptr, // tp_descr_get
    nullptr, // tp_descr_set
    0, // tp_dictoffset
    nullptr, // tp_init
    PyType_GenericAlloc,
    nullptr, // tp_new
    PyObject_Del,
    nullptr, // tp_is_gc
    nullptr, // tp_bases
    nullptr, // tp_mro
    nullptr, // tp_cache
    nullptr, // tp_subclasses
    nullptr, // tp_weaklist
    nullptr, // tp_del
    0, // tp_version_tag,
#if PY_VERSION_HEX >= 0x03040000
    nullptr, // tp_finalize
#endif
#if PY_VERSION_HEX >= 0x03080000
    nullptr, // tp_vectorcall
#endif
  };

  static bool registered = false;
  if (!registered) {
    registered = true;

    if (PyType_Ready(&wrapper_type) < 0) {
      return nullptr;
    }

    // If the collections.abc module is loaded, register this as a subclass.
    _register_collection((PyTypeObject *)&wrapper_type, "MappingView");
  }

  (void)PyObject_INIT(items, &wrapper_type);
  Py_XINCREF(wrap->_base._self);
  items->_base._self = wrap->_base._self;
  items->_base._name = wrap->_base._name;
  items->_keys._len_func = wrap->_keys._len_func;
  items->_keys._getitem_func = wrap->_keys._getitem_func;
  items->_getitem_func = wrap->_getitem_func;
  items->_setitem_func = nullptr;
  return (PyObject *)items;
}

/**
 * Implementation of `property[key] = value`
 */
static int Dtool_MutableMappingWrapper_setitem(PyObject *self, PyObject *key, PyObject *value) {
  Dtool_MappingWrapper *wrap = (Dtool_MappingWrapper *)self;
  nassertr(wrap->_setitem_func != nullptr, -1);
  return wrap->_setitem_func(wrap->_base._self, key, value);
}

/**
 * Implementation of property.pop(key[,def=None]) which is the same as get()
 * except that it also removes the element from the mapping.
 */
static PyObject *Dtool_MutableMappingWrapper_pop(PyObject *self, PyObject *args) {
  Dtool_MappingWrapper *wrap = (Dtool_MappingWrapper *)self;
  nassertr(wrap, nullptr);
  if (wrap->_getitem_func == nullptr || wrap->_setitem_func == nullptr) {
    return Dtool_Raise_TypeError("property does not support pop()");
  }

  Py_ssize_t size = PyTuple_GET_SIZE(args);
  if (size != 1 && size != 2) {
    return PyErr_Format(PyExc_TypeError, "%s.pop() takes 1 or 2 arguments", wrap->_base._name);
  }
  PyObject *defvalue = Py_None;
  if (size >= 2) {
    defvalue = PyTuple_GET_ITEM(args, 1);
  }

  PyObject *key = PyTuple_GET_ITEM(args, 0);
  PyObject *value = wrap->_getitem_func(wrap->_base._self, key);
  if (value != nullptr) {
    // OK, now set unset this value.
    if (wrap->_setitem_func(wrap->_base._self, key, nullptr) == 0) {
      return value;
    } else {
      Py_DECREF(value);
      return nullptr;
    }
  } else if (_PyErr_OCCURRED() == PyExc_KeyError) {
    PyErr_Clear();
    Py_INCREF(defvalue);
    return defvalue;
  } else {
    return nullptr;
  }
}

/**
 * Implementation of property.popitem() which returns and removes an arbitrary
 * (key, value) pair from the mapping.  Useful for destructive iteration.
 */
static PyObject *Dtool_MutableMappingWrapper_popitem(PyObject *self, PyObject *) {
  Dtool_MappingWrapper *wrap = (Dtool_MappingWrapper *)self;
  nassertr(wrap, nullptr);
  if (wrap->_getitem_func == nullptr || wrap->_setitem_func == nullptr ||
      wrap->_keys._len_func == nullptr || wrap->_keys._getitem_func == nullptr) {
    return Dtool_Raise_TypeError("property does not support popitem()");
  }

  Py_ssize_t length = wrap->_keys._len_func(wrap->_base._self);
  if (length < 1) {
    return PyErr_Format(PyExc_KeyError, "%s is empty", wrap->_base._name);
  }

  PyObject *key = wrap->_keys._getitem_func(wrap->_base._self, length - 1);
  if (key != nullptr) {
    PyObject *value = wrap->_getitem_func(wrap->_base._self, key);
    if (value != nullptr) {
      // OK, now set unset this value.
      if (wrap->_setitem_func(wrap->_base._self, key, nullptr) == 0) {
        PyObject *item = PyTuple_New(2);
        PyTuple_SET_ITEM(item, 0, key);
        PyTuple_SET_ITEM(item, 1, value);
        return item;
      }
      Py_DECREF(value);
    }
  }
  return nullptr;
}

/*
 * Implementation of property.clear() which removes all elements in the
 * mapping.
 */
static PyObject *Dtool_MutableMappingWrapper_clear(PyObject *self, PyObject *) {
  Dtool_MappingWrapper *wrap = (Dtool_MappingWrapper *)self;
  nassertr(wrap, nullptr);
  Py_ssize_t index = 0;
  if (wrap->_keys._len_func != nullptr && wrap->_keys._getitem_func != nullptr &&
      wrap->_setitem_func != nullptr) {
    index = wrap->_keys._len_func(wrap->_base._self);
  } else {
    return Dtool_Raise_TypeError("property does not support clear()");
  }

  // Iterate through the items, invoking the delete function for each.  We do
  // this in reverse order, which may be more efficient.
  while (index > 0) {
    --index;
    PyObject *key = wrap->_keys._getitem_func(wrap->_base._self, index);
    if (key != nullptr) {
      int result = wrap->_setitem_func(wrap->_base._self, key, nullptr);
      Py_DECREF(key);
      if (result != 0) {
        return nullptr;
      }
    }
  }
  Py_INCREF(Py_None);
  return Py_None;
}

/**
 * Implementation of property.setdefault(key[,def=None]) which is the same as
 * get() except that it also writes the default value back to the mapping if
 * the key was not found is missing.
 */
static PyObject *Dtool_MutableMappingWrapper_setdefault(PyObject *self, PyObject *args) {
  Dtool_MappingWrapper *wrap = (Dtool_MappingWrapper *)self;
  nassertr(wrap, nullptr);

  if (wrap->_getitem_func == nullptr || wrap->_setitem_func == nullptr) {
    return Dtool_Raise_TypeError("property does not support setdefault()");
  }

  Py_ssize_t size = PyTuple_GET_SIZE(args);
  if (size != 1 && size != 2) {
    return PyErr_Format(PyExc_TypeError, "%s.setdefault() takes 1 or 2 arguments", wrap->_base._name);
  }
  PyObject *defvalue = Py_None;
  if (size >= 2) {
    defvalue = PyTuple_GET_ITEM(args, 1);
  }
  PyObject *key = PyTuple_GET_ITEM(args, 0);
  PyObject *value = wrap->_getitem_func(wrap->_base._self, key);
  if (value != nullptr) {
    return value;
  } else if (_PyErr_OCCURRED() == PyExc_KeyError) {
    PyErr_Clear();
    if (wrap->_setitem_func(wrap->_base._self, key, defvalue) == 0) {
      Py_INCREF(defvalue);
      return defvalue;
    }
  }
  return nullptr;
}

/**
 * Implementation of property.update(...) which sets multiple values in one
 * go.  It accepts either a single dictionary or keyword arguments, not both.
 */
static PyObject *Dtool_MutableMappingWrapper_update(PyObject *self, PyObject *args, PyObject *kwargs) {
  Dtool_MappingWrapper *wrap = (Dtool_MappingWrapper *)self;
  nassertr(wrap, nullptr);

  if (wrap->_getitem_func == nullptr || wrap->_setitem_func == nullptr) {
    return Dtool_Raise_TypeError("property does not support update()");
  }

  // We accept either a dict argument or keyword arguments, but not both.
  PyObject *dict;
  switch (PyTuple_GET_SIZE(args)) {
  case 0:
    if (kwargs == nullptr) {
      // This is legal.
      Py_INCREF(Py_None);
      return Py_None;
    }
    dict = kwargs;
    break;
  case 1:
    if (PyDict_Check(PyTuple_GET_ITEM(args, 0)) && (kwargs == nullptr || Py_SIZE(kwargs) == 0)) {
      dict = PyTuple_GET_ITEM(args, 0);
      break;
    }
    // Fall through
  default:
    return PyErr_Format(PyExc_TypeError, "%s.update() takes either a dict argument or keyword arguments", wrap->_base._name);
  }

  PyObject *key, *value;
  Py_ssize_t pos = 0;
  while (PyDict_Next(dict, &pos, &key, &value)) {
    if (wrap->_setitem_func(wrap->_base._self, key, value) != 0) {
      return nullptr;
    }
  }
  Py_INCREF(Py_None);
  return Py_None;
}

/**
 * This variant defines only a generator interface.
 */
static PyObject *Dtool_GeneratorWrapper_iternext(PyObject *self) {
  Dtool_GeneratorWrapper *wrap = (Dtool_GeneratorWrapper *)self;
  nassertr(wrap, nullptr);
  nassertr(wrap->_iternext_func, nullptr);
  return wrap->_iternext_func(wrap->_base._self);
}

/**
 * This is a variant of the Python getset mechanism that permits static
 * properties.
 */
static void
Dtool_StaticProperty_dealloc(PyDescrObject *descr) {
#if PY_VERSION_HEX >= 0x03080000
  PyObject_GC_UnTrack(descr);
#else
  _PyObject_GC_UNTRACK(descr);
#endif
  Py_XDECREF(descr->d_type);
  Py_XDECREF(descr->d_name);
//#if PY_MAJOR_VERSION >= 3
//  Py_XDECREF(descr->d_qualname);
//#endif
  PyObject_GC_Del(descr);
}

static PyObject *
Dtool_StaticProperty_repr(PyDescrObject *descr, const char *format) {
#if PY_MAJOR_VERSION >= 3
  return PyUnicode_FromFormat("<attribute '%s' of '%s'>",
                              PyUnicode_AsUTF8(descr->d_name),
                              descr->d_type->tp_name);
#else
  return PyString_FromFormat("<attribute '%s' of '%s'>",
                             PyString_AS_STRING(descr->d_name),
                             descr->d_type->tp_name);
#endif
}

static int
Dtool_StaticProperty_traverse(PyObject *self, visitproc visit, void *arg) {
  PyDescrObject *descr = (PyDescrObject *)self;
  Py_VISIT(descr->d_type);
  return 0;
}

static PyObject *
Dtool_StaticProperty_get(PyGetSetDescrObject *descr, PyObject *obj, PyObject *type) {
  if (descr->d_getset->get != nullptr) {
    return descr->d_getset->get(obj, descr->d_getset->closure);
  } else {
    return PyErr_Format(PyExc_AttributeError,
                        "attribute '%s' of type '%.100s' is not readable",
#if PY_MAJOR_VERSION >= 3
                        PyUnicode_AsUTF8(((PyDescrObject *)descr)->d_name),
#else
                        PyString_AS_STRING(((PyDescrObject *)descr)->d_name),
#endif
                        ((PyDescrObject *)descr)->d_type->tp_name);
  }
}

static int
Dtool_StaticProperty_set(PyGetSetDescrObject *descr, PyObject *obj, PyObject *value) {
  if (descr->d_getset->set != nullptr) {
    return descr->d_getset->set(obj, value, descr->d_getset->closure);
  } else {
    PyErr_Format(PyExc_AttributeError,
                 "attribute '%s' of type '%.100s' is not writable",
#if PY_MAJOR_VERSION >= 3
                 PyUnicode_AsUTF8(((PyDescrObject *)descr)->d_name),
#else
                 PyString_AS_STRING(((PyDescrObject *)descr)->d_name),
#endif
                 ((PyDescrObject *)descr)->d_type->tp_name);
    return -1;
  }
}

/**
 * This wraps around a property that exposes a sequence interface.
 */
Dtool_SequenceWrapper *Dtool_NewSequenceWrapper(PyObject *self, const char *name) {
  Dtool_SequenceWrapper *wrap = (Dtool_SequenceWrapper *)PyObject_MALLOC(sizeof(Dtool_SequenceWrapper));
  if (wrap == nullptr) {
    return (Dtool_SequenceWrapper *)PyErr_NoMemory();
  }

  static PySequenceMethods seq_methods = {
    Dtool_SequenceWrapper_length,
    nullptr, // sq_concat
    nullptr, // sq_repeat
    Dtool_SequenceWrapper_getitem,
    nullptr, // sq_slice
    nullptr, // sq_ass_item
    nullptr, // sq_ass_slice
    Dtool_SequenceWrapper_contains,
    nullptr, // sq_inplace_concat
    nullptr, // sq_inplace_repeat
  };

  static PyMethodDef methods[] = {
    {"index", &Dtool_SequenceWrapper_index, METH_O, nullptr},
    {"count", &Dtool_SequenceWrapper_count, METH_O, nullptr},
    {nullptr, nullptr, 0, nullptr}
  };

  static PyTypeObject wrapper_type = {
    PyVarObject_HEAD_INIT(nullptr, 0)
    "sequence wrapper",
    sizeof(Dtool_SequenceWrapper),
    0, // tp_itemsize
    Dtool_WrapperBase_dealloc,
    0, // tp_vectorcall_offset
    nullptr, // tp_getattr
    nullptr, // tp_setattr
    nullptr, // tp_compare
    Dtool_SequenceWrapper_repr,
    nullptr, // tp_as_number
    &seq_methods,
    nullptr, // tp_as_mapping
    nullptr, // tp_hash
    nullptr, // tp_call
    nullptr, // tp_str
    PyObject_GenericGetAttr,
    PyObject_GenericSetAttr,
    nullptr, // tp_as_buffer
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_CHECKTYPES,
    nullptr, // tp_doc
    nullptr, // tp_traverse
    nullptr, // tp_clear
    nullptr, // tp_richcompare
    0, // tp_weaklistoffset
    PySeqIter_New,
    nullptr, // tp_iternext
    methods,
    nullptr, // tp_members
    nullptr, // tp_getset
    nullptr, // tp_base
    nullptr, // tp_dict
    nullptr, // tp_descr_get
    nullptr, // tp_descr_set
    0, // tp_dictoffset
    nullptr, // tp_init
    PyType_GenericAlloc,
    nullptr, // tp_new
    PyObject_Del,
    nullptr, // tp_is_gc
    nullptr, // tp_bases
    nullptr, // tp_mro
    nullptr, // tp_cache
    nullptr, // tp_subclasses
    nullptr, // tp_weaklist
    nullptr, // tp_del
    0, // tp_version_tag,
#if PY_VERSION_HEX >= 0x03040000
    nullptr, // tp_finalize
#endif
#if PY_VERSION_HEX >= 0x03080000
    nullptr, // tp_vectorcall
#endif
  };

  static bool registered = false;
  if (!registered) {
    registered = true;

    if (PyType_Ready(&wrapper_type) < 0) {
      return nullptr;
    }

    // If the collections.abc module is loaded, register this as a subclass.
    _register_collection((PyTypeObject *)&wrapper_type, "Sequence");
  }

  (void)PyObject_INIT(wrap, &wrapper_type);
  Py_XINCREF(self);
  wrap->_base._self = self;
  wrap->_base._name = name;
  wrap->_len_func = nullptr;
  wrap->_getitem_func = nullptr;
  return wrap;
}

/**
 * This wraps around a property that exposes a mutable sequence interface.
 */
Dtool_MutableSequenceWrapper *Dtool_NewMutableSequenceWrapper(PyObject *self, const char *name) {
  Dtool_MutableSequenceWrapper *wrap = (Dtool_MutableSequenceWrapper *)PyObject_MALLOC(sizeof(Dtool_MutableSequenceWrapper));
  if (wrap == nullptr) {
    return (Dtool_MutableSequenceWrapper *)PyErr_NoMemory();
  }

  static PySequenceMethods seq_methods = {
    Dtool_SequenceWrapper_length,
    nullptr, // sq_concat
    nullptr, // sq_repeat
    Dtool_SequenceWrapper_getitem,
    nullptr, // sq_slice
    Dtool_MutableSequenceWrapper_setitem,
    nullptr, // sq_ass_slice
    Dtool_SequenceWrapper_contains,
    Dtool_MutableSequenceWrapper_extend,
    nullptr, // sq_inplace_repeat
  };

  static PyMethodDef methods[] = {
    {"index", &Dtool_SequenceWrapper_index, METH_O, nullptr},
    {"count", &Dtool_SequenceWrapper_count, METH_O, nullptr},
    {"clear", &Dtool_MutableSequenceWrapper_clear, METH_NOARGS, nullptr},
    {"pop", &Dtool_MutableSequenceWrapper_pop, METH_VARARGS, nullptr},
    {"remove", &Dtool_MutableSequenceWrapper_remove, METH_O, nullptr},
    {"append", &Dtool_MutableSequenceWrapper_append, METH_O, nullptr},
    {"insert", &Dtool_MutableSequenceWrapper_insert, METH_VARARGS, nullptr},
    {"extend", &Dtool_MutableSequenceWrapper_extend, METH_O, nullptr},
    {nullptr, nullptr, 0, nullptr}
  };

  static PyTypeObject wrapper_type = {
    PyVarObject_HEAD_INIT(nullptr, 0)
    "sequence wrapper",
    sizeof(Dtool_MutableSequenceWrapper),
    0, // tp_itemsize
    Dtool_WrapperBase_dealloc,
    0, // tp_vectorcall_offset
    nullptr, // tp_getattr
    nullptr, // tp_setattr
    nullptr, // tp_compare
    Dtool_SequenceWrapper_repr,
    nullptr, // tp_as_number
    &seq_methods,
    nullptr, // tp_as_mapping
    nullptr, // tp_hash
    nullptr, // tp_call
    nullptr, // tp_str
    PyObject_GenericGetAttr,
    PyObject_GenericSetAttr,
    nullptr, // tp_as_buffer
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_CHECKTYPES,
    nullptr, // tp_doc
    nullptr, // tp_traverse
    nullptr, // tp_clear
    nullptr, // tp_richcompare
    0, // tp_weaklistoffset
    PySeqIter_New,
    nullptr, // tp_iternext
    methods,
    nullptr, // tp_members
    nullptr, // tp_getset
    nullptr, // tp_base
    nullptr, // tp_dict
    nullptr, // tp_descr_get
    nullptr, // tp_descr_set
    0, // tp_dictoffset
    nullptr, // tp_init
    PyType_GenericAlloc,
    nullptr, // tp_new
    PyObject_Del,
    nullptr, // tp_is_gc
    nullptr, // tp_bases
    nullptr, // tp_mro
    nullptr, // tp_cache
    nullptr, // tp_subclasses
    nullptr, // tp_weaklist
    nullptr, // tp_del
    0, // tp_version_tag,
#if PY_VERSION_HEX >= 0x03040000
    nullptr, // tp_finalize
#endif
#if PY_VERSION_HEX >= 0x03080000
    nullptr, // tp_vectorcall
#endif
  };

  static bool registered = false;
  if (!registered) {
    registered = true;

    if (PyType_Ready(&wrapper_type) < 0) {
      return nullptr;
    }

    // If the collections.abc module is loaded, register this as a subclass.
    _register_collection((PyTypeObject *)&wrapper_type, "MutableSequence");
  }

  (void)PyObject_INIT(wrap, &wrapper_type);
  Py_XINCREF(self);
  wrap->_base._self = self;
  wrap->_base._name = name;
  wrap->_len_func = nullptr;
  wrap->_getitem_func = nullptr;
  wrap->_setitem_func = nullptr;
  wrap->_insert_func = nullptr;
  return wrap;
}

/**
 * This wraps around a mapping interface, with getitem function.
 */
Dtool_MappingWrapper *Dtool_NewMappingWrapper(PyObject *self, const char *name) {
  Dtool_MappingWrapper *wrap = (Dtool_MappingWrapper *)PyObject_MALLOC(sizeof(Dtool_MappingWrapper));
  if (wrap == nullptr) {
    return (Dtool_MappingWrapper *)PyErr_NoMemory();
  }

  static PySequenceMethods seq_methods = {
    Dtool_SequenceWrapper_length,
    nullptr, // sq_concat
    nullptr, // sq_repeat
    nullptr, // sq_item
    nullptr, // sq_slice
    nullptr, // sq_ass_item
    nullptr, // sq_ass_slice
    Dtool_MappingWrapper_contains,
    nullptr, // sq_inplace_concat
    nullptr, // sq_inplace_repeat
  };

  static PyMappingMethods map_methods = {
    Dtool_SequenceWrapper_length,
    Dtool_MappingWrapper_getitem,
    nullptr, // mp_ass_subscript
  };

  static PyMethodDef methods[] = {
    {"get", &Dtool_MappingWrapper_get, METH_VARARGS, nullptr},
    {"keys", &Dtool_MappingWrapper_keys, METH_NOARGS, nullptr},
    {"values", &Dtool_MappingWrapper_values, METH_NOARGS, nullptr},
    {"items", &Dtool_MappingWrapper_items, METH_NOARGS, nullptr},
    {nullptr, nullptr, 0, nullptr}
  };

  static PyTypeObject wrapper_type = {
    PyVarObject_HEAD_INIT(nullptr, 0)
    "mapping wrapper",
    sizeof(Dtool_MappingWrapper),
    0, // tp_itemsize
    Dtool_WrapperBase_dealloc,
    0, // tp_vectorcall_offset
    nullptr, // tp_getattr
    nullptr, // tp_setattr
    nullptr, // tp_compare
    Dtool_WrapperBase_repr,
    nullptr, // tp_as_number
    &seq_methods,
    &map_methods,
    nullptr, // tp_hash
    nullptr, // tp_call
    nullptr, // tp_str
    PyObject_GenericGetAttr,
    PyObject_GenericSetAttr,
    nullptr, // tp_as_buffer
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_CHECKTYPES,
    nullptr, // tp_doc
    nullptr, // tp_traverse
    nullptr, // tp_clear
    nullptr, // tp_richcompare
    0, // tp_weaklistoffset
    Dtool_MappingWrapper_iter,
    nullptr, // tp_iternext
    methods,
    nullptr, // tp_members
    nullptr, // tp_getset
    nullptr, // tp_base
    nullptr, // tp_dict
    nullptr, // tp_descr_get
    nullptr, // tp_descr_set
    0, // tp_dictoffset
    nullptr, // tp_init
    PyType_GenericAlloc,
    nullptr, // tp_new
    PyObject_Del,
    nullptr, // tp_is_gc
    nullptr, // tp_bases
    nullptr, // tp_mro
    nullptr, // tp_cache
    nullptr, // tp_subclasses
    nullptr, // tp_weaklist
    nullptr, // tp_del
    0, // tp_version_tag,
#if PY_VERSION_HEX >= 0x03040000
    nullptr, // tp_finalize
#endif
#if PY_VERSION_HEX >= 0x03080000
    nullptr, // tp_vectorcall
#endif
  };

  static bool registered = false;
  if (!registered) {
    registered = true;

    if (PyType_Ready(&wrapper_type) < 0) {
      return nullptr;
    }

    // If the collections.abc module is loaded, register this as a subclass.
    _register_collection((PyTypeObject *)&wrapper_type, "Mapping");
  }

  (void)PyObject_INIT(wrap, &wrapper_type);
  Py_XINCREF(self);
  wrap->_base._self = self;
  wrap->_base._name = name;
  wrap->_keys._len_func = nullptr;
  wrap->_keys._getitem_func = nullptr;
  wrap->_getitem_func = nullptr;
  wrap->_setitem_func = nullptr;
  return wrap;
}

/**
 * This wraps around a mapping interface, with getitem/setitem functions.
 */
Dtool_MappingWrapper *Dtool_NewMutableMappingWrapper(PyObject *self, const char *name) {
  Dtool_MappingWrapper *wrap = (Dtool_MappingWrapper *)PyObject_MALLOC(sizeof(Dtool_MappingWrapper));
  if (wrap == nullptr) {
    return (Dtool_MappingWrapper *)PyErr_NoMemory();
  }

  static PySequenceMethods seq_methods = {
    Dtool_SequenceWrapper_length,
    nullptr, // sq_concat
    nullptr, // sq_repeat
    nullptr, // sq_item
    nullptr, // sq_slice
    nullptr, // sq_ass_item
    nullptr, // sq_ass_slice
    Dtool_MappingWrapper_contains,
    nullptr, // sq_inplace_concat
    nullptr, // sq_inplace_repeat
  };

  static PyMappingMethods map_methods = {
    Dtool_SequenceWrapper_length,
    Dtool_MappingWrapper_getitem,
    Dtool_MutableMappingWrapper_setitem,
  };

  static PyMethodDef methods[] = {
    {"get", &Dtool_MappingWrapper_get, METH_VARARGS, nullptr},
    {"pop", &Dtool_MutableMappingWrapper_pop, METH_VARARGS, nullptr},
    {"popitem", &Dtool_MutableMappingWrapper_popitem, METH_NOARGS, nullptr},
    {"clear", &Dtool_MutableMappingWrapper_clear, METH_VARARGS, nullptr},
    {"setdefault", &Dtool_MutableMappingWrapper_setdefault, METH_VARARGS, nullptr},
    {"update", (PyCFunction) &Dtool_MutableMappingWrapper_update, METH_VARARGS | METH_KEYWORDS, nullptr},
    {"keys", &Dtool_MappingWrapper_keys, METH_NOARGS, nullptr},
    {"values", &Dtool_MappingWrapper_values, METH_NOARGS, nullptr},
    {"items", &Dtool_MappingWrapper_items, METH_NOARGS, nullptr},
    {nullptr, nullptr, 0, nullptr}
  };

  static PyTypeObject wrapper_type = {
    PyVarObject_HEAD_INIT(nullptr, 0)
    "mapping wrapper",
    sizeof(Dtool_MappingWrapper),
    0, // tp_itemsize
    Dtool_WrapperBase_dealloc,
    0, // tp_vectorcall_offset
    nullptr, // tp_getattr
    nullptr, // tp_setattr
    nullptr, // tp_compare
    Dtool_WrapperBase_repr,
    nullptr, // tp_as_number
    &seq_methods,
    &map_methods,
    nullptr, // tp_hash
    nullptr, // tp_call
    nullptr, // tp_str
    PyObject_GenericGetAttr,
    PyObject_GenericSetAttr,
    nullptr, // tp_as_buffer
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_CHECKTYPES,
    nullptr, // tp_doc
    nullptr, // tp_traverse
    nullptr, // tp_clear
    nullptr, // tp_richcompare
    0, // tp_weaklistoffset
    Dtool_MappingWrapper_iter,
    nullptr, // tp_iternext
    methods,
    nullptr, // tp_members
    nullptr, // tp_getset
    nullptr, // tp_base
    nullptr, // tp_dict
    nullptr, // tp_descr_get
    nullptr, // tp_descr_set
    0, // tp_dictoffset
    nullptr, // tp_init
    PyType_GenericAlloc,
    nullptr, // tp_new
    PyObject_Del,
    nullptr, // tp_is_gc
    nullptr, // tp_bases
    nullptr, // tp_mro
    nullptr, // tp_cache
    nullptr, // tp_subclasses
    nullptr, // tp_weaklist
    nullptr, // tp_del
    0, // tp_version_tag,
#if PY_VERSION_HEX >= 0x03040000
    nullptr, // tp_finalize
#endif
#if PY_VERSION_HEX >= 0x03080000
    nullptr, // tp_vectorcall
#endif
  };

  static bool registered = false;
  if (!registered) {
    registered = true;

    if (PyType_Ready(&wrapper_type) < 0) {
      return nullptr;
    }

    // If the collections.abc module is loaded, register this as a subclass.
    _register_collection((PyTypeObject *)&wrapper_type, "MutableMapping");
  }

  (void)PyObject_INIT(wrap, &wrapper_type);
  Py_XINCREF(self);
  wrap->_base._self = self;
  wrap->_base._name = name;
  wrap->_keys._len_func = nullptr;
  wrap->_keys._getitem_func = nullptr;
  wrap->_getitem_func = nullptr;
  wrap->_setitem_func = nullptr;
  return wrap;
}

/**
 * Creates a generator that invokes a given function with the given self arg.
 */
PyObject *
Dtool_NewGenerator(PyObject *self, iternextfunc gen_next) {
  static PyTypeObject wrapper_type = {
    PyVarObject_HEAD_INIT(nullptr, 0)
    "generator wrapper",
    sizeof(Dtool_GeneratorWrapper),
    0, // tp_itemsize
    Dtool_WrapperBase_dealloc,
    0, // tp_vectorcall_offset
    nullptr, // tp_getattr
    nullptr, // tp_setattr
    nullptr, // tp_compare
    nullptr, // tp_repr
    nullptr, // tp_as_number
    nullptr, // tp_as_sequence
    nullptr, // tp_as_mapping
    nullptr, // tp_hash
    nullptr, // tp_call
    nullptr, // tp_str
    PyObject_GenericGetAttr,
    PyObject_GenericSetAttr,
    nullptr, // tp_as_buffer
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_CHECKTYPES,
    nullptr, // tp_doc
    nullptr, // tp_traverse
    nullptr, // tp_clear
    nullptr, // tp_richcompare
    0, // tp_weaklistoffset
    PyObject_SelfIter,
    Dtool_GeneratorWrapper_iternext,
    nullptr, // tp_methods
    nullptr, // tp_members
    nullptr, // tp_getset
    nullptr, // tp_base
    nullptr, // tp_dict
    nullptr, // tp_descr_get
    nullptr, // tp_descr_set
    0, // tp_dictoffset
    nullptr, // tp_init
    PyType_GenericAlloc,
    nullptr, // tp_new
    PyObject_Del,
    nullptr, // tp_is_gc
    nullptr, // tp_bases
    nullptr, // tp_mro
    nullptr, // tp_cache
    nullptr, // tp_subclasses
    nullptr, // tp_weaklist
    nullptr, // tp_del
    0, // tp_version_tag,
#if PY_VERSION_HEX >= 0x03040000
    nullptr, // tp_finalize
#endif
#if PY_VERSION_HEX >= 0x03080000
    nullptr, // tp_vectorcall
#endif
  };

  if (PyType_Ready(&wrapper_type) < 0) {
    return nullptr;
  }

  Dtool_GeneratorWrapper *gen;
  gen = (Dtool_GeneratorWrapper *)PyType_GenericAlloc(&wrapper_type, 0);
  if (gen != nullptr) {
    Py_INCREF(self);
    gen->_base._self = self;
    gen->_iternext_func = gen_next;
  }
  return (PyObject *)gen;
}

/**
 * This is a variant of the Python getset mechanism that permits static
 * properties.
 */
PyObject *
Dtool_NewStaticProperty(PyTypeObject *type, const PyGetSetDef *getset) {
  static PyTypeObject wrapper_type = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    "getset_descriptor",
    sizeof(PyGetSetDescrObject),
    0, // tp_itemsize
    (destructor)Dtool_StaticProperty_dealloc,
    0, // tp_vectorcall_offset
    nullptr, // tp_getattr
    nullptr, // tp_setattr
    nullptr, // tp_reserved
    (reprfunc)Dtool_StaticProperty_repr,
    nullptr, // tp_as_number
    nullptr, // tp_as_sequence
    nullptr, // tp_as_mapping
    nullptr, // tp_hash
    nullptr, // tp_call
    nullptr, // tp_str
    PyObject_GenericGetAttr,
    nullptr, // tp_setattro
    nullptr, // tp_as_buffer
    Py_TPFLAGS_DEFAULT,
    nullptr, // tp_doc
    Dtool_StaticProperty_traverse,
    nullptr, // tp_clear
    nullptr, // tp_richcompare
    0, // tp_weaklistoffset
    nullptr, // tp_iter
    nullptr, // tp_iternext
    nullptr, // tp_methods
    nullptr, // tp_members
    nullptr, // tp_getset
    nullptr, // tp_base
    nullptr, // tp_dict
    (descrgetfunc)Dtool_StaticProperty_get,
    (descrsetfunc)Dtool_StaticProperty_set,
    0, // tp_dictoffset
    nullptr, // tp_init
    nullptr, // tp_alloc
    nullptr, // tp_new
    nullptr, // tp_free
    nullptr, // tp_is_gc
    nullptr, // tp_bases
    nullptr, // tp_mro
    nullptr, // tp_cache
    nullptr, // tp_subclasses
    nullptr, // tp_weaklist
    nullptr, // tp_del
    0, // tp_version_tag,
#if PY_VERSION_HEX >= 0x03040000
    nullptr, // tp_finalize
#endif
#if PY_VERSION_HEX >= 0x03080000
    nullptr, // tp_vectorcall
#endif
  };

  if (PyType_Ready(&wrapper_type) < 0) {
    return nullptr;
  }

  PyGetSetDescrObject *descr;
  descr = (PyGetSetDescrObject *)PyType_GenericAlloc(&wrapper_type, 0);
  if (descr != nullptr) {
    Py_XINCREF(type);
    descr->d_getset = (PyGetSetDef *)getset;
#if PY_MAJOR_VERSION >= 3
    descr->d_common.d_type = type;
    descr->d_common.d_name = PyUnicode_InternFromString(getset->name);
#if PY_VERSION_HEX >= 0x03030000
    descr->d_common.d_qualname = nullptr;
#endif
#else
    descr->d_type = type;
    descr->d_name = PyString_InternFromString(getset->name);
#endif
  }
  return (PyObject *)descr;
}

#endif  // HAVE_PYTHON
#line 1 "dtool/src/interrogatedb/dtool_super_base.cxx"
/**
 * PANDA 3D SOFTWARE
 * Copyright (c) Carnegie Mellon University.  All rights reserved.
 *
 * All use of this software is subject to the terms of the revised BSD
 * license.  You should have received a copy of this license along
 * with this source code in a file named "LICENSE."
 *
 * @file dtool_super_base.cxx
 * @author drose
 * @date 2005-07-04
 */

#include "py_panda.h"

#ifdef HAVE_PYTHON

static PyMemberDef standard_type_members[] = {
  {(char *)"this", (sizeof(void*) == sizeof(int)) ? T_UINT : T_ULONGLONG, offsetof(Dtool_PyInstDef, _ptr_to_object), READONLY, (char *)"C++ 'this' pointer, if any"},
  {(char *)"this_ownership", T_BOOL, offsetof(Dtool_PyInstDef, _memory_rules), READONLY, (char *)"C++ 'this' ownership rules"},
  {(char *)"this_const", T_BOOL, offsetof(Dtool_PyInstDef, _is_const), READONLY, (char *)"C++ 'this' const flag"},
// {(char *)"this_signature", T_INT, offsetof(Dtool_PyInstDef, _signature),
// READONLY, (char *)"A type check signature"},
  {(char *)"this_metatype", T_OBJECT, offsetof(Dtool_PyInstDef, _My_Type), READONLY, (char *)"The dtool meta object"},
  {nullptr}  /* Sentinel */
};

static PyObject *GetSuperBase(PyObject *self) {
  Dtool_PyTypedObject *super_base = Dtool_GetSuperBase();
  Py_XINCREF((PyTypeObject *)super_base); // order is important .. this is used for static functions
  return (PyObject *)super_base;
};

static void Dtool_PyModuleClassInit_DTOOL_SUPER_BASE(PyObject *module) {
  if (module != nullptr) {
    Dtool_PyTypedObject *super_base = Dtool_GetSuperBase();
    Py_INCREF((PyTypeObject *)&super_base);
    PyModule_AddObject(module, "DTOOL_SUPER_BASE", (PyObject *)&super_base);
  }
}

static void *Dtool_DowncastInterface_DTOOL_SUPER_BASE(void *from_this, Dtool_PyTypedObject *from_type) {
  return nullptr;
}

static void *Dtool_UpcastInterface_DTOOL_SUPER_BASE(PyObject *self, Dtool_PyTypedObject *requested_type) {
  return nullptr;
}

static int Dtool_Init_DTOOL_SUPER_BASE(PyObject *self, PyObject *args, PyObject *kwds) {
  assert(self != nullptr);
  PyErr_Format(PyExc_TypeError, "cannot init constant class %s", Py_TYPE(self)->tp_name);
  return -1;
}

static void Dtool_FreeInstance_DTOOL_SUPER_BASE(PyObject *self) {
  Py_TYPE(self)->tp_free(self);
}

/**
 * Returns a pointer to the DTOOL_SUPER_BASE class that is the base class of
 * all Panda types.  This pointer is shared by all modules.
 */
Dtool_PyTypedObject *Dtool_GetSuperBase() {
  Dtool_TypeMap *type_map = Dtool_GetGlobalTypeMap();
  auto it = type_map->find("DTOOL_SUPER_BASE");
  if (it != type_map->end()) {
    return it->second;
  }

  static PyMethodDef methods[] = {
    { "DtoolGetSuperBase", (PyCFunction)&GetSuperBase, METH_NOARGS, "Will Return SUPERbase Class"},
    { nullptr, nullptr, 0, nullptr }
  };

  static Dtool_PyTypedObject super_base_type = {
    {
      PyVarObject_HEAD_INIT(nullptr, 0)
      "dtoolconfig.DTOOL_SUPER_BASE",
      sizeof(Dtool_PyInstDef),
      0, // tp_itemsize
      &Dtool_FreeInstance_DTOOL_SUPER_BASE,
      0, // tp_vectorcall_offset
      nullptr, // tp_getattr
      nullptr, // tp_setattr
#if PY_MAJOR_VERSION >= 3
      nullptr, // tp_compare
#else
      &DtoolInstance_ComparePointers,
#endif
      nullptr, // tp_repr
      nullptr, // tp_as_number
      nullptr, // tp_as_sequence
      nullptr, // tp_as_mapping
      &DtoolInstance_HashPointer,
      nullptr, // tp_call
      nullptr, // tp_str
      PyObject_GenericGetAttr,
      PyObject_GenericSetAttr,
      nullptr, // tp_as_buffer
      (Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_CHECKTYPES),
      nullptr, // tp_doc
      nullptr, // tp_traverse
      nullptr, // tp_clear
#if PY_MAJOR_VERSION >= 3
      &DtoolInstance_RichComparePointers,
#else
      nullptr, // tp_richcompare
#endif
      0, // tp_weaklistoffset
      nullptr, // tp_iter
      nullptr, // tp_iternext
      methods,
      standard_type_members,
      nullptr, // tp_getset
      nullptr, // tp_base
      nullptr, // tp_dict
      nullptr, // tp_descr_get
      nullptr, // tp_descr_set
      0, // tp_dictoffset
      Dtool_Init_DTOOL_SUPER_BASE,
      PyType_GenericAlloc,
      nullptr, // tp_new
      PyObject_Del,
      nullptr, // tp_is_gc
      nullptr, // tp_bases
      nullptr, // tp_mro
      nullptr, // tp_cache
      nullptr, // tp_subclasses
      nullptr, // tp_weaklist
      nullptr, // tp_del
      0, // tp_version_tag,
#if PY_VERSION_HEX >= 0x03040000
      nullptr, // tp_finalize
#endif
#if PY_VERSION_HEX >= 0x03080000
      nullptr, // tp_vectorcall
#endif
    },
    TypeHandle::none(),
    Dtool_PyModuleClassInit_DTOOL_SUPER_BASE,
    Dtool_UpcastInterface_DTOOL_SUPER_BASE,
    Dtool_DowncastInterface_DTOOL_SUPER_BASE,
    nullptr,
    nullptr,
  };

  super_base_type._PyType.tp_dict = PyDict_New();
  PyDict_SetItemString(super_base_type._PyType.tp_dict, "DtoolClassDict", super_base_type._PyType.tp_dict);

  if (PyType_Ready((PyTypeObject *)&super_base_type) < 0) {
    PyErr_SetString(PyExc_TypeError, "PyType_Ready(Dtool_DTOOL_SUPER_BASE)");
    return nullptr;
  }
  Py_INCREF((PyTypeObject *)&super_base_type);

  PyDict_SetItemString(super_base_type._PyType.tp_dict, "DtoolGetSuperBase", PyCFunction_New(&methods[0], (PyObject *)&super_base_type));

  (*type_map)["DTOOL_SUPER_BASE"] = &super_base_type;
  return &super_base_type;
}

#endif  // HAVE_PYTHON

