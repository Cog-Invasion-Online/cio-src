#pragma once

#include "pandabase.h"
#include "notifyCategoryProxy.h"
#include "configVariableDouble.h"
#include "configVariableString.h"
#include "configVariableInt.h"


NotifyCategoryDecl(ccoginvasion, EXPORT_CLASS, EXPORT_TEMPL);

extern ConfigVariableInt ctmusic_numsongs;

extern void initccoginvasion();

