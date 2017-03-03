/**
 * COG INVASION ONLINE
 * Copyright (c) CIO Team. All rights reserved.
 *
 * @file audioClip.h
 * @author Brian Lach
 * @date 2016-06-28
 */


#ifndef AUDIOCLIP_H
#define AUDIOCLIP_H

#include "audioSound.h"
#include "throw_event.h"
#include "asyncTaskManager.h"
#include "genericAsyncTask.h"


class AudioClip {
PUBLISHED:
	static const string get_clip_done_event();
	static const string get_part_done_event();
	string &get_clip_name();

public:
	AudioClip();
	AudioClip(vector<PT(AudioSound)> chunks, string &clip_name);
	~AudioClip();

	AsyncTask::DoneStatus play_audio_tick(GenericAsyncTask *task, PT(AudioSound) sound, int index);

	void play_from_index(int start_index);
	void play_all_parts();

	void stop();

	void cleanup();

	bool active;

	struct TickParams {
		PT(AudioSound) sound;
		int index;
	};

	TickParams *get_curr_sound_tick_params();

private:
	PT(GenericAsyncTask) _ticktask;
	PT(AsyncTaskManager) _taskmgr;
	PT(AudioSound) _current_sound;
	vector<PT(AudioSound)> _chunks;
	string _clip_name;
	static AsyncTask::DoneStatus play_audio_tick_task(GenericAsyncTask *task, void *data);

	TickParams _curr_sound_tick_params;

	bool _curr_clip_started;
};



#endif //AUDIOCLIP_H
