/**
 * COG INVASION ONLINE
 * Copyright (c) CIO Team. All rights reserved.
 *
 * @file audioclip.h
 * @author Brian Lach
 * @date 2016-06-28
 */

#ifndef AUDIOCLIP_H
#define AUDIOCLIP_H

#include <audioSound.h>
#include <throw_event.h>
#include <asyncTaskManager.h>
#include <genericAsyncTask.h>

class AudioClip
{
PUBLISHED:
        static const std::string get_clip_done_event();
        static const std::string get_part_done_event();
        std::string &get_clip_name();

public:
        struct TickParams
        {
                PT( AudioSound ) sound;
                int index;
        };

        AudioClip();
        AudioClip( std::vector<PT( AudioSound )> chunks, std::string &clip_name );
        ~AudioClip();

        AsyncTask::DoneStatus play_audio_tick( GenericAsyncTask *task, PT( AudioSound ) sound, int index );

        void play_from_index( int start_index );
        void play_all_parts();

        void stop();

        void cleanup();

        TickParams *get_curr_sound_tick_params();

public:
        bool active;

private:
        static AsyncTask::DoneStatus play_audio_tick_task( GenericAsyncTask *task, void *data );

private:
        PT( GenericAsyncTask ) _ticktask;
        PT( AsyncTaskManager ) _taskmgr;
        PT( AudioSound ) _current_sound;
        std::vector<PT( AudioSound )> _chunks;
        std::string _clip_name;

        TickParams _curr_sound_tick_params;

        bool _curr_clip_started;
};

#endif // AUDIOCLIP_H
