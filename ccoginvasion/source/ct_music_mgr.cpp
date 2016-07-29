#include "ct_music_mgr.h"

#include <stdlib.h>
#include <time.h>

#include "eventHandler.h"
#include "tools.cpp"

#include "config_ccoginvasion.h"

bool CTMusicManager::loaded = false;
CTMusicManager::MusicChunkMap CTMusicManager::tournament_music_chunks;
CTMusicManager::MusicClipMap CTMusicManager::tournament_music_clips;

CTMusicManager::~CTMusicManager()
{
}

bool CTMusicManager::is_loaded()
{
	return loaded;
}

void CTMusicManager::spawn_load_tournament_music_task()
{
	PT(GenericAsyncTask) task = new GenericAsyncTask("LTM", &CTMusicManager::load_tournament_music, (void*)NULL);
	task->set_task_chain("TournamentMusicThread");
	AsyncTaskManager::get_global_ptr()->add(task);
}

AsyncTask::DoneStatus CTMusicManager::load_tournament_music(GenericAsyncTask* task, void* data)
{
	if (loaded) {
		cout << "Redundant call to CTMusicManager::load_tournament_music()" << endl;
		return AsyncTask::DS_done;
	}

	cout << "Loading tournament music" << endl;

	srand(time(NULL));

	if (!CTMusicData::initialized) {
		cout << "Chunk data not yet initialized, initializing..." << endl;
		CTMusicData::initialize_chunk_data();
	}

	for (CTMusicData::MusicDataMap::iterator rootMapItr = CTMusicData::data.begin(); rootMapItr != CTMusicData::data.end(); ++rootMapItr)
	{

		string song_name = rootMapItr->first;

		int songnum = song_name.back() - '0';
		if (songnum > ctmusic_numsongs) {
			cout << "Not loading " << song_name << ": only " << ctmusic_numsongs << " song(s) specified in config" << endl;
			continue;
		}

		CTMusicData::ChunkDataMap chunkdata = rootMapItr->second;

		cout << song_name << endl;

		for (CTMusicData::ChunkDataMap::iterator chunkMapItr = chunkdata.begin(); chunkMapItr != chunkdata.end(); ++chunkMapItr)
		{

			string chunk_name = chunkMapItr->first;
			vector<int> file_range = chunkMapItr->second;

			for (int indexi = 0; indexi < file_range.size(); indexi++) {

				int clip_index = file_range[indexi];

				string folder = "tournament_music/" + song_name + "/";
				string filename = "MW_Music";
				string extension = ".ogg";

				if (clip_index > 0) {
					filename = filename + "_" + to_string((longlong)clip_index);
				}

				string fullfile = folder + filename + extension;
				PT(AudioSound) song = CTMusicData::audio_mgr->get_sound(fullfile);
				song->set_volume(0.75f);
				song->set_loop(false);
				tournament_music_chunks[song_name][chunk_name].push_back(song);

			}

		    tournament_music_clips[song_name][chunk_name] = AudioClip(tournament_music_chunks[song_name][chunk_name], chunk_name);
		}
	}

	loaded = true;
	cout << "Finished loading tournament music" << endl;
	return AsyncTask::DS_done;
}

CTMusicManager::CTMusicManager() : _curr_clip(NULL)
{
	_next_clip_request = "NONE";
	_curr_clip_name = "NONE";
}

void CTMusicManager::set_song_name(const string& name)
{
	_song_name = name;
}

string CTMusicManager::get_song_name() const
{
	return _song_name;
}

void CTMusicManager::set_clip_request(const string& clip)
{
	_next_clip_request = clip;
}

string CTMusicManager::get_clip_request() const
{
	return _next_clip_request;
}

string CTMusicManager::get_clip_name() const
{
	return _curr_clip_name;
}

string CTMusicManager::get_style_of_clipname(const string& clip_name) const
{
	vector<string> split_name = explode("_", clip_name);
	string style = split_name[split_name.size() - 1];
	if (style.find("orchestra") != string::npos || style.find("base") != string::npos) {
		return "_" + style;
	}
	else {
		return "_orchestra";
	}
}

string CTMusicManager::get_curr_style() const
{
	return get_style_of_clipname(_curr_clip_name);
}

void CTMusicManager::start_music(const string& base_or_orc)
{
	if (!loaded) {
		cout << "CTMusicManager: Cannot start the music before loading!" << endl;
		return;
	}

	cout << "Starting music" << endl;

	play_clip("intro" + base_or_orc);

	EventHandler* evhandl = EventHandler::get_global_event_handler();
	evhandl->add_hook(AudioClip::get_part_done_event(), &handle_part_done_event, this);
	evhandl->add_hook(AudioClip::get_clip_done_event(), &handle_clip_done, this);
}

void CTMusicManager::play_clip(string& clip_name)
{
	stop_clip();

	_curr_clip_name = clip_name;

	AudioClip* ac = &tournament_music_clips[_song_name][clip_name];
	ac->active = true;
	ac->play_all_parts();
	_curr_clip = ac;
}

void CTMusicManager::stop_clip()
{
	if (_curr_clip != NULL) {
		_curr_clip->active = false;
		_curr_clip->stop();
		_curr_clip = NULL;
	}
	_curr_clip_name = "NONE";
}

void CTMusicManager::handle_clip_done(const Event* e, void* data)
{
	((CTMusicManager*)data)->play_new_clip();
}

void CTMusicManager::play_new_clip()
{
	if (_curr_clip_name.find("evaded") != string::npos || _curr_clip_name.find("arrested") != string::npos) {
		// Don't play a new clip if we just played an evade or arrest clip (we're done).
		return;
	}
	string new_clip;
	if (_next_clip_request == "NONE") {
		new_clip = _curr_clip_name;
	}
	else {
		new_clip = _next_clip_request;
		_next_clip_request = "NONE";
	}

	play_clip(new_clip);
}

void CTMusicManager::handle_part_done_event(const Event* e, void* data)
{
	((CTMusicManager*)data)->handle_part_done(e->get_parameter(0).get_int_value());
}

void CTMusicManager::handle_part_done(int part_index)
{
	if (_next_clip_request != "NONE" && _curr_clip_name.find(explode("_", _next_clip_request)[0]) == string::npos) {
		play_new_clip();
	}
	else if (_next_clip_request != "NONE" && _curr_clip_name.find(explode("_", _next_clip_request)[0]) != string::npos &&
		     get_curr_style() != get_style_of_clipname(_next_clip_request)) {
		// We requested the same clip but in a different style. Play from the same index but in the different style.
		stop_clip();
		AudioClip* ac = &tournament_music_clips[_song_name][_next_clip_request];
		ac->active = true;
		ac->play_from_index(part_index + 1);
		_curr_clip_name = _next_clip_request;
		_next_clip_request = "NONE";
		_curr_clip = ac;
	}
}
