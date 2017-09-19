/**
 * COG INVASION ONLINE
 * Copyright (c) CIO Team. All rights reserved.
 *
 * @file config_ccoginvasion.cxx
 * @author Brian Lach
 * @date 2016-06-28
 */

#include "config_ccoginvasion.h"
#include "ciShaderGenerator.h"

#include <dconfig.h>

Configure(config_ccoginvasion);
NotifyCategoryDef(ccoginvasion, "");

ConfigureFn(config_ccoginvasion) {
  initccoginvasion();
}

ConfigVariableInt ctmusic_numsongs
("ctmusic-numsongs", 4);

void
initccoginvasion() {
  static bool initialized = false;
  if (initialized) {
    return;
  }
  initialized = true;

  CIShaderGenerator::init_type();

}


