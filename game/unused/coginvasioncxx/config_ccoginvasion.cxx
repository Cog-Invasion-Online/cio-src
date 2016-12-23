// Filename: config_ccoginvasion.cxx
// Created by:  blach (18Aug15)

#include <pandabase.h>
#include <dconfig.h>

void init_libccoginvasion();

Configure(config_ccoginvasion);

ConfigureFn(config_ccoginvasion) {
  init_libccoginvasion();
}

void
init_libccoginvasion() {
  static bool initialized = false;

  if (initialized) {
    return;
  }

  initialized = true;
}
