
// IMPORTANT
// No include guards here
// See http://www.panda3d.org/forums/viewtopic.php?f=12&t=16162

// C4273: Inconsistent DLL-Binding
#pragma warning (disable: 4273)

// Define these constants for interrogate
#ifdef P3_INTERROGATE
#define WIN32
#define WIN32_VC
#define _WINDOWS
#endif

// Include the config of the panda3d installation. 
// This will ensure we have the same settings.
#include "dtool_config.h"
#undef DO_MEMORY_USAGE

// Import panda base
#include "pandabase.h"
