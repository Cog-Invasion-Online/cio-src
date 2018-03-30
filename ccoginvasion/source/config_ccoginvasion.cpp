/**
 * COG INVASION ONLINE
 * Copyright (c) CIO Team. All rights reserved.
 *
 * @file config_ccoginvasion.cpp
 * @author Brian Lach
 * @date 2016-06-28
 */

#include "config_ccoginvasion.h"

#include <dconfig.h>

Configure( config_ccoginvasion );
NotifyCategoryDef( ccoginvasion, "" );

ConfigureFn( config_ccoginvasion )
{
        init_ccoginvasion();
}

ConfigVariableInt ctmusic_numsongs
( "ctmusic-numsongs", 4 );

void init_ccoginvasion()
{
        static bool initialized = false;
        if ( initialized )
        {
                return;
        }
        initialized = true;

}