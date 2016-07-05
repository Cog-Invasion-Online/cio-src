#include "nirai.h"

#include "graphicsPipeSelection.h"

// Obviously we have miles
#define HAVE_RAD_MSS

#include "config_milesAudio.h"

AudioManager* Create_MilesAudioManager();
// Register Miles audio (like setup_env, must be in static time).
void* load_miles()
{
    std::cout << "Using Miles audio library." << std::endl;
    init_libMilesAudio();
    AudioManager::register_AudioManager_creator(Create_MilesAudioManager);
    return NULL;
}

static void* __ = load_miles();

// P3D Python modules initers.
#ifdef WIN32
#define _P3D_INIT(MODULE) extern "C" __declspec(dllexport) void init##MODULE ();
#else
#define _P3D_INIT(MODULE) extern "C" void init##MODULE ();
#endif

_P3D_INIT(_core)
_P3D_INIT(_direct)
_P3D_INIT(fx)
_P3D_INIT(egg)
_P3D_INIT(ode)
_P3D_INIT(physics)
_P3D_INIT(interrogatedb)
_P3D_INIT(libpandadna)

// P3D CXX fwd decls.
#ifdef WIN32
void init_libwgldisplay();
#elif __APPLE__
void init_libcocoadisplay();
#endif
void init_libmovies();
void init_libpnmimagetypes();

static PyMethodDef NiraiMethods[] = {{NULL, NULL, 0}};

static void inject_into_sys_modules(const std::string& module, const std::string& alias)
{
    PyObject* sysmodule = PyImport_ImportModule("sys");
    Py_INCREF(sysmodule);
    PyObject* modulesdict = PyObject_GetAttrString(sysmodule, "modules");
    Py_INCREF(modulesdict);

    PyObject* mod = PyImport_ImportModule(module.c_str());
    Py_INCREF(mod);
    PyDict_SetItemString(modulesdict, alias.c_str(), mod);

    Py_DECREF(modulesdict);
    Py_DECREF(sysmodule);
}

static void start_nirai()
{
    // Setup __nirai__.
    PyObject* niraimod = Py_InitModule("__nirai__", NiraiMethods);
    PyObject* bt = PyImport_ImportModule("__builtin__");
    PyObject_SetAttrString(bt, "__nirai__", niraimod);
    Py_INCREF(niraimod);
    Py_DECREF(bt);

    // Init Panda3D.
    PyObject* panda3d_mod = Py_InitModule("panda3d", NiraiMethods);
    Py_INCREF(panda3d_mod);

    init_core();

    // Setup the display.
#ifdef WIN32
    init_libwgldisplay();
#elif __APPLE__
    init_libcocoadisplay();
#endif

    // Setup audio.
    init_libmovies();

    // Setup pnmimagetypes.
    init_libpnmimagetypes();

    // Init other modules.
	std::cout << "initinterrogatedb" << std::endl;
    initinterrogatedb();
	std::cout << "init_direct" << std::endl;
    init_direct();
	std::cout << "initegg" << std::endl;
    initegg();
    initfx();
    initode();
    initphysics();

    // Init libpandadna
    initlibpandadna();

    // Remove our hacked panda3d root from sys.modules
    // so it can be reloaded with a proper __init__.py
    // but all panda3d.xxx submodules are still accessible.
    // However, another hack is required (see main).
    PyObject* sysmodule = PyImport_ImportModule("sys");
    Py_INCREF(sysmodule);
    PyObject* modulesdict = PyObject_GetAttrString(sysmodule, "modules");
    Py_INCREF(modulesdict);
    PyDict_DelItemString(modulesdict, "panda3d");
    //PyDict_DelItemString(modulesdict, "libpandadna");
    Py_DECREF(modulesdict);
    Py_DECREF(sysmodule);
};

// fwd decls
void initaes();

static void setup_python()
{
    initaes();

    // Clear sys.path.
    PyObject* sysmodule = PyImport_ImportModule("sys");
    Py_INCREF(sysmodule);

    PyObject* pathlist = PyObject_GetAttrString(sysmodule, "path");
    Py_DECREF(pathlist);

    PyObject* newpathlist = PyList_New(1);
    Py_INCREF(newpathlist);
    PyList_SET_ITEM(newpathlist, 0, Py_BuildValue("s", "."));
    PyObject_SetAttrString(sysmodule, "path", newpathlist);

    Py_DECREF(sysmodule);
}

int main(int argc, char* argv[])
{

    if (niraicall_onPreStart(argc, argv))
        return 1;

    Py_NoSiteFlag++;
    Py_FrozenFlag++;
    Py_InspectFlag++; // For crash at the exit.

    Py_SetProgramName(argv[0]);
    Py_Initialize();
    PyEval_InitThreads();
    PySys_SetArgv(argc, argv);

    start_nirai();
    setup_python();

    if (niraicall_onLoadGameData())
        return 2;

    // Until panda3d directory stops mixing .py and .pyd files, we need to explicitly do this:
    // N.B. No error checking, these modules are guaranteed to exist.
    PyObject* panda3d_mod = PyImport_ImportModule("panda3d");
    PyObject_SetAttrString(panda3d_mod, "_core", PyImport_ImportModule("panda3d.core"));
    PyObject_SetAttrString(panda3d_mod, "interrogatedb", PyImport_ImportModule("panda3d.interrogatedb"));
    PyObject_SetAttrString(panda3d_mod, "_direct", PyImport_ImportModule("panda3d._direct"));
    PyObject_SetAttrString(panda3d_mod, "egg", PyImport_ImportModule("panda3d.egg"));
    PyObject_SetAttrString(panda3d_mod, "fx", PyImport_ImportModule("panda3d.fx"));
    PyObject_SetAttrString(panda3d_mod, "ode", PyImport_ImportModule("panda3d.ode"));
    PyObject_SetAttrString(panda3d_mod, "physics", PyImport_ImportModule("panda3d.physics"));

    /*
    // Do the same for libpandadna.
    PyObject* lpdna_mod = PyImport_ImportModule("libpandadna");
    PyObject_SetAttrString(lpdna_mod, "DNALoader", PyImport_ImportModule("libpandadna.DNALoader"));
    PyObject_SetAttrString(lpdna_mod, "DNAStorage", PyImport_ImportModule("libpandadna.DNAStorage"));
    PyObject_SetAttrString(lpdna_mod, "DNAAnimBuilding", PyImport_ImportModule("libpandadna.DNAAnimBuilding"));
    PyObject_SetAttrString(lpdna_mod, "DNAAnimProp", PyImport_ImportModule("libpandadna.DNAAnimProp"));
    PyObject_SetAttrString(lpdna_mod, "DNABattleCell", PyImport_ImportModule("libpandadna.DNABattleCell"));
    PyObject_SetAttrString(lpdna_mod, "DNACornice", PyImport_ImportModule("libpandadna.DNACornice"));
    PyObject_SetAttrString(lpdna_mod, "DNADoor", PyImport_ImportModule("libpandadna.DNADoor"));
    PyObject_SetAttrString(lpdna_mod, "DNAFlatBuilding", PyImport_ImportModule("libpandadna.DNAFlatBuilding"));
    PyObject_SetAttrString(lpdna_mod, "DNAFlatDoor", PyImport_ImportModule("libpandadna.DNAFlatDoor"));
    PyObject_SetAttrString(lpdna_mod, "DNAGroup", PyImport_ImportModule("libpandadna.DNAGroup"));
    PyObject_SetAttrString(lpdna_mod, "DNAInteractiveProp", PyImport_ImportModule("libpandadna.DNAInteractiveProp"));
    PyObject_SetAttrString(lpdna_mod, "DNALandmarkBuilding", PyImport_ImportModule("libpandadna.DNALandmarkBuilding"));
    PyObject_SetAttrString(lpdna_mod, "DNANode", PyImport_ImportModule("libpandadna.DNANode"));
    PyObject_SetAttrString(lpdna_mod, "DNAProp", PyImport_ImportModule("libpandadna.DNAProp"));
    PyObject_SetAttrString(lpdna_mod, "DNASign", PyImport_ImportModule("libpandadna.DNASign"));
    PyObject_SetAttrString(lpdna_mod, "DNASignBaseline", PyImport_ImportModule("libpandadna.DNASignBaseline"));
    PyObject_SetAttrString(lpdna_mod, "DNASignGraphic", PyImport_ImportModule("libpandadna.DNASignGraphic"));
    PyObject_SetAttrString(lpdna_mod, "DNAStreet", PyImport_ImportModule("libpandadna.DNAStreet"));
    PyObject_SetAttrString(lpdna_mod, "DNAVisGroup", PyImport_ImportModule("libpandadna.DNAVisGroup"));
    PyObject_SetAttrString(lpdna_mod, "DNAWall", PyImport_ImportModule("libpandadna.DNAWall"));
    PyObject_SetAttrString(lpdna_mod, "DNAWindows", PyImport_ImportModule("libpandadna.DNAWindows"));
    */

    const char* module = "lib.coginvasion.base.CIStartGlobal";
    if (!niraicall_isGameExe()) {
      module = "lib.launcher";
    }

	std::cout << "PyImport_ImportModule" << std::endl;

    PyObject* res = PyImport_ImportModule(module);

    if (res == NULL)
    {
        std::cerr << "Error importing main module!" << std::endl;
        PyErr_Print();

        return 3;
    }

    return 0;
}
