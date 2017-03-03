#ifndef CTMUSICMGR_H
#define CTMUSICMGR_H

/**
 * COG INVASION ONLINE
 * Copyright (c) CIO Team. All rights reserved.
 *
 * @file ctMusicMgr.h
 * @author Brian Lach
 * @date 2016-06-28
 */

#include <map>

#include "audioClip.h"
#include "ctMusicData.h"

class CTMusicManager {
PUBLISHED:

	CTMusicManager();
	~CTMusicManager();

	static void spawn_load_tournament_music_task();
	void set_clip_request(const string &clip);
	string get_clip_request() const;
	void start_music(const string &base_or_orc);
	void stop_clip();
	static bool is_loaded();
	void set_song_name(const string &name);
	string get_song_name() const;
	string get_clip_name() const;
	string get_curr_style() const;

	void handle_part_done(int part_index);

public:

	typedef map<string, map<string, vector<PT(AudioSound)>>> MusicChunkMap;
	typedef map<string, map<string, AudioClip>> MusicClipMap;

	static MusicChunkMap tournament_music_chunks;
	static MusicClipMap tournament_music_clips;

	static bool loaded;

private:
	string _next_clip_request;
	string _song_name;
	AudioClip *_curr_clip;
	string _curr_clip_name;

	static AsyncTask::DoneStatus load_tournament_music(GenericAsyncTask *task, void *data);

	static void handle_clip_done(const Event *e, void *data);
	static void handle_part_done_event(const Event *e, void *data);
	void play_new_clip();
	void play_clip(string &clip_name);

	string get_style_of_clipname(const string &clip_name) const;
};

#endif //CTMUSICMGR_H
