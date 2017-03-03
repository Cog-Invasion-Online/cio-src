/**
 * COG INVASION ONLINE
 * Copyright (c) CIO Team. All rights reserved.
 *
 * @file config_ccoginvasion.h
 * @author Brian Lach
 * @date 2016-06-28
 */

#ifndef __CONFIG_CCOGINVASION_H__
#define __CONFIG_CCOGINVASION_H__

#include <pandabase.h>
#include <notifyCategoryProxy.h>
#include <configVariableDouble.h>
#include <configVariableString.h>
#include <configVariableInt.h>

NotifyCategoryDecl(ccoginvasion, EXPORT_CLASS, EXPORT_TEMPL);

extern ConfigVariableInt ctmusic_numsongs;

extern void initccoginvasion();

#endif // __CONFIG_CCOGINVASION_H__

