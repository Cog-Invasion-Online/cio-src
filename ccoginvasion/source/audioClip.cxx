/**
 * COG INVASION ONLINE
 * Copyright (c) CIO Team. All rights reserved.
 *
 * @file audioClip.cxx
 * @author Brian Lach
 * @date 2016-06-28
 */

#include "audioClip.h"
#include <math.h>
#include "tools.cxx"

AudioClip::
AudioClip() {
}

AudioClip::
AudioClip(vector<PT(AudioSound)> chunks, string &clip_name) :
  _chunks(chunks), _taskmgr(AsyncTaskManager::get_global_ptr()),
  _clip_name(clip_name), _ticktask(NULL), _current_sound(NULL) {
}

AudioClip::
~AudioClip() {
}

const string AudioClip::
get_clip_done_event() {
	return "AudioClip_clipDone";
}

const string AudioClip::
get_part_done_event() {
	return "AudioClip_partDone";
}

string &AudioClip::
get_clip_name() {
	return _clip_name;
}

void AudioClip::
cleanup() {
	stop();
	delete _current_sound;
	delete _ticktask;
}

void AudioClip::
stop() {
	if (_ticktask != NULL) {
		_taskmgr->remove(_ticktask);
		_ticktask = NULL;
	}

	if (_current_sound != NULL) {
		if (_current_sound->status() == AudioSound::PLAYING) {
			_current_sound->stop();
			_current_sound = NULL;
		}
	}
}

static double
round(double val) {
	return floor(val + 0.5);
}

void AudioClip::
play_from_index(int start_index) {

	stop();

	PT(AudioSound) sound = _chunks[start_index];
	_current_sound = sound;

	TickParams params;
	params.sound = sound;
	params.index = start_index;
	_curr_sound_tick_params = params;

	_curr_clip_started = false;

	PT(GenericAsyncTask) _ticktask = new GenericAsyncTask("AudioClip_audioTick", &AudioClip::play_audio_tick_task, this);
	_ticktask->set_task_chain("TournamentMusicThread");
	_taskmgr->add(_ticktask);
}

// Play all of the parts in this audio clip.
void AudioClip::
play_all_parts() {
	play_from_index(0);
}

AsyncTask::DoneStatus AudioClip::
play_audio_tick(GenericAsyncTask *task, PT(AudioSound) sound, int index) {
	if (!active) {
		sound->stop();
		return AsyncTask::DS_done;
	}

	if (sound->status() != AudioSound::PLAYING && sound == _current_sound && _curr_clip_started == false) {
		_curr_clip_started = true;
		sound->play();
	}

	if (sound->status() != AudioSound::PLAYING && sound == _current_sound && _curr_clip_started == true) {
		// This part is done!
		sound->stop();
		if (index == _chunks.size() - 1) {
			// This is the last part of the clip, send out the clip done event.
			throw_event(get_clip_done_event());
		}
		else {
			// Now, play the next part.
			play_from_index(index + 1);
			// We're not done with this clip yet, send out the part done event, and say what clip we just finished.
			throw_event(get_part_done_event(), EventParameter(index));
		}
		return AsyncTask::DS_done;
	}
	return AsyncTask::DS_cont;
}

AudioClip::TickParams *AudioClip::
get_curr_sound_tick_params() {
	return &_curr_sound_tick_params;
}

AsyncTask::DoneStatus AudioClip::
play_audio_tick_task(GenericAsyncTask *task, void *data) {
	AudioClip *ac = (AudioClip *)data;
	TickParams *params = ac->get_curr_sound_tick_params();

	PT(AudioSound) sound = params->sound;
	int index = params->index;

	return ac->play_audio_tick(task, sound, index);
}