/**
 * COG INVASION ONLINE
 * Copyright (c) CIO Team. All rights reserved.
 *
 * @file config_ccoginvasion.h
 * @author Brian Lach
 * @date 2016-06-28
 */

#ifndef CONFIG_CCOGINVASION_H
#define CONFIG_CCOGINVASION_H

#include <pandabase.h>
#include <notifyCategoryProxy.h>
#include <configVariableDouble.h>
#include <configVariableString.h>
#include <configVariableInt.h>

using namespace std;

#ifdef BUILDING_CCOGINVASION
#define EXPCL_CCOGINVASION EXPORT_CLASS
#define EXPTP_CCOGINVASION EXPORT_TEMPL
#else
#define EXPCL_CCOGINVASION IMPORT_CLASS
#define EXPTP_CCOGINVASION IMPORT_TEMPL
#endif

NotifyCategoryDeclNoExport(ccoginvasion);

extern ConfigVariableInt ctmusic_numsongs;

extern void init_ccoginvasion();

#endif // __CONFIG_CCOGINVASION_H__

