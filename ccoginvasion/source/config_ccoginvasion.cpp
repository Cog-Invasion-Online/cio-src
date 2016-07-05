#include "config_ccoginvasion.h"

/*

Include all your dynamically typed classes here, e.g.
#include "my_dynamic_class.h"

*/

#include "dconfig.h"


Configure(config_ccoginvasion);
NotifyCategoryDef(ccoginvasion, "");

ConfigureFn(config_ccoginvasion) {
	initccoginvasion();
}

ConfigVariableInt ctmusic_numsongs("ctmusic-numsongs", 4);

void
initccoginvasion() {
	static bool initialized = false;
	if (initialized) {
		return;
	}
	initialized = true;

	// Init your dynamic types here, e.g.:
	// MyDynamicClass::init_type();

	return;
}


