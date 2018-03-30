/**
 * COG INVASION ONLINE
 * Copyright (c) CIO Team. All rights reserved.
 *
 * @file ct_musicdata.h
 * @author Brian Lach
 * @date 2016-06-28
 */

#ifndef CTMUSICDATA_H
#define CTMUSICDATA_H

#include <iostream>
#include <vector>
#include <cmath>
#include <string>
#include <map>
#include <fstream>

#include <asyncTaskManager.h>
#include <genericAsyncTask.h>
#include <threadPriority.h>

#include "audiomanager.h"

NotifyCategoryDeclNoExport(ctmusicdata);

class CTMusicData
{

public:

        // song name -> chunk name -> file range (list of numbers)
        typedef map<string, vector<int>> ChunkDataMap;
        typedef map<string, ChunkDataMap> MusicDataMap;

        static MusicDataMap data;

        static PT( AudioManager ) audio_mgr;

        static PT( GenericAsyncTask ) am_update_task;

        static AsyncTask::DoneStatus audiomgr_update_task( GenericAsyncTask *task, void *data );

PUBLISHED:

        CTMusicData();
        ~CTMusicData();

        static bool initialized;
        static void initialize_chunk_data();

        static void stop_am_update_task();
};

#endif //CTMUSICDATA_H
