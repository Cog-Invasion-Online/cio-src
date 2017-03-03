/**
 * COG INVASION ONLINE
 * Copyright (c) CIO Team. All rights reserved.
 *
 * @file ctMusicData.cxx
 * @author Brian Lach
 * @date 2016-06-28
 */

#include "ctMusicData.h"

#include "tools.cxx"

bool CTMusicData::initialized = false;
CTMusicData::MusicDataMap CTMusicData::data;
PT(AudioManager) CTMusicData::audio_mgr;
PT(GenericAsyncTask) CTMusicData::am_update_task = NULL;

CTMusicData::
CTMusicData() {
}

CTMusicData::
~CTMusicData() {
}

void CTMusicData::
stop_am_update_task() {
	AsyncTaskManager *taskmgr = AsyncTaskManager::get_global_ptr();
	if (am_update_task != NULL) {
		if (taskmgr->has_task(am_update_task)) {
			taskmgr->remove(am_update_task);
			am_update_task = NULL;
		}
	}
}

AsyncTask::DoneStatus CTMusicData::
audiomgr_update_task(GenericAsyncTask *task, void *data) {
	CTMusicData::audio_mgr->update();
	return AsyncTask::DS_cont;
}

void CTMusicData::
initialize_chunk_data() {

	// This should only be called once on startup, so make the task chain.
	PT(AsyncTaskChain) taskchain = AsyncTaskManager::get_global_ptr()->make_task_chain("TournamentMusicThread");
	taskchain->set_frame_sync(false);
	taskchain->set_thread_priority(ThreadPriority::TP_normal);
	taskchain->set_num_threads(1);

	// Make our own special Audio Manager that we will update on our thread.
	audio_mgr = AudioManager::create_AudioManager();

	// Start the audio manager update task
	PT(GenericAsyncTask) updatetask = new GenericAsyncTask("CTMusicData::update_audioManager", &CTMusicData::audiomgr_update_task, (void*)NULL);
	updatetask->set_task_chain("TournamentMusicThread");
	AsyncTaskManager::get_global_ptr()->add(updatetask);
	
	am_update_task = updatetask;

	//----------------------------------SONG 1---------------------------------\\

	ChunkDataMap song1 = data["encntr_nfsmw_bg_1"];

	song1["intro_base"] = range(0, 20 + 1);
	song1["intro_orchestra"] = range(20, 39 + 1);
	
	song1["intro_orchestra_from_located"] = range(24, 39 + 1);
	song1["located_orchestra"] = range(40, 71 + 1);
	song1["located_base"] = range(72, 103 + 1);

	song1["5050_base"] = range(104, 138 + 1);
	song1["5050_orchestra"] = range(139, 173 + 1);
	
	song1["approaching_orchestra"] = one_num_vec(174);
	song1["getting_worse_orchestra"] = range(175, 186 + 1);

	song1["approaching_base"] = one_num_vec(187);
	song1["getting_worse_base"] = range(188, 199 + 1);

	song1["arresting_you"] = range(200, 208 + 1);

	song1["running_away_base"] = range(209, 232 + 1);
	song1["running_away_orchestra"] = range(233, 256 + 1);

	song1["high_speed_cooldown_orchestra"] = range(257, 280 + 1);
	song1["high_speed_cooldown_base"] = range(281, 299 + 1);

	song1["static_cooldown"] = range(300, 320 + 1);

	song1["very_low_speed_cooldown"] = range(321, 340 + 1);
	song1["low_speed_cooldown_1"] = range(341, 354 + 1);
	song1["low_speed_cooldown_2"] = range(355, 369 + 1);

	song1["arrested_1"] = one_num_vec(370);
	song1["arrested_2"] = one_num_vec(371);
	song1["arrested_3"] = one_num_vec(372);
	song1["arrested_4"] = one_num_vec(373);

	song1["evaded_1"] = one_num_vec(374);
	song1["evaded_2"] = one_num_vec(375);
	song1["evaded_3"] = one_num_vec(376);
	song1["evaded_4"] = one_num_vec(377);
	song1["evaded_5"] = one_num_vec(378);
	song1["evaded_6"] = one_num_vec(379);
	song1["evaded_7"] = range(381, 382 + 1);
	song1["evaded_8"] = range(383, 384 + 1);

	// Just to make sure lol.
	data["encntr_nfsmw_bg_1"] = song1;

	//-------------------------------------------------------------------------\\
	//----------------------------------SONG 2---------------------------------\\

	ChunkDataMap song2 = data["encntr_nfsmw_bg_2"];

	song2["intro_base"] = range(385, 408 + 1);
	song2["intro_orchestra"] = range(409, 432 + 1);

	song2["5050_orchestra"] = range(433, 461 + 1);
	song2["5050_base"] = range(462, 490 + 1);

	song2["located_base"] = range(491, 515 + 1);
	song2["located_orchestra"] = range(516, 540 + 1);

	song2["getting_worse_orchestra"] = range(541, 548 + 1);
	song2["getting_worse_base"] = range(549, 556 + 1);

	song2["arresting_you"] = range(557, 566 + 1);

	song2["running_away_base"] = range(567, 574 + 1);
	song2["running_away_orchestra"] = range(575, 582 + 1);

	song2["high_speed_cooldown_base"] = range(583, 598 + 1);
	song2["high_speed_cooldown_orchestra"] = range(599, 614 + 1);

	song2["static_cooldown"] = range(615, 626 + 1);
	
	song2["very_low_speed_cooldown"] = range(627, 637 + 1);
	song2["low_speed_cooldown_1"] = range(638, 645 + 1);
	song2["low_speed_cooldown_2"] = range(646, 652 + 1);

	song2["arrested_1"] = one_num_vec(653);
	song2["arrested_2"] = one_num_vec(654);
	song2["arrested_3"] = one_num_vec(655);
	song2["arrested_4"] = one_num_vec(656);
	
	song2["evaded_1"] = one_num_vec(657);
	song2["evaded_2"] = one_num_vec(658);
	song2["evaded_3"] = one_num_vec(659);
	song2["evaded_4"] = one_num_vec(660);
	song2["evaded_5"] = one_num_vec(661);
	song2["evaded_6"] = one_num_vec(662);
	song2["evaded_7"] = one_num_vec(663);
	song2["evaded_8"] = one_num_vec(664);
	song2["evaded_9"] = range(665, 666 + 1);
	song2["evaded_10"] = range(667, 668 + 1);

	// Just to make sure lol.
	data["encntr_nfsmw_bg_2"] = song2;

	//-------------------------------------------------------------------------\\
	//----------------------------------SONG 3---------------------------------\\

	ChunkDataMap song3 = data["encntr_nfsmw_bg_3"];

	song3["intro_base"] = range(669, 689 + 1);
	song3["intro_orchestra"] = range(690, 710 + 1);

	song3["5050_orchstra"] = range(711, 724 + 1);
	song3["5050_base"] = range(725, 739 + 1);

	song3["located_base"] = range(740, 753 + 1);
	song3["located_orchestra"] = range(754, 767 + 1);

	song3["getting_worse_orchestra"] = range(768, 780 + 1);
	song3["getting_worse_base"] = range(781, 793 + 1);

	song3["arresting_you"] = range(794, 798 + 1);

	song3["running_away_base"] = range(799, 818 + 1);
	song3["running_away_orchestra"] = range(819, 838 + 1);

	song3["high_speed_cooldown_base"] = range(839, 868 + 1);
	song3["high_speed_cooldown_orchestra"] = range(869, 898 + 1);

	song3["static_cooldown"] = range(899, 921);

	song3["very_low_speed_cooldown_1"] = range(922, 944 + 1);
	song3["very_low_speed_cooldown_2"] = range(945, 966 + 1);
	
	song3["low_speed_cooldown_1"] = range(967, 973 + 1);
	song3["low_speed_cooldown_2"] = range(974, 980 + 1);

	song3["arrested_1"] = one_num_vec(982);
	song3["arrested_2"] = one_num_vec(983);
	song3["arrested_3"] = one_num_vec(984);
	song3["arrested_4"] = one_num_vec(985);

	song3["evaded_1"] = one_num_vec(986);
	song3["evaded_2"] = one_num_vec(987);
	song3["evaded_3"] = one_num_vec(988);
	song3["evaded_4"] = one_num_vec(989);
	song3["evaded_5"] = one_num_vec(990);
	song3["evaded_6"] = one_num_vec(991);
	song3["evaded_7"] = one_num_vec(992);
	song3["evaded_8"] = one_num_vec(993);
	song3["evaded_9"] = range(994, 995 + 1);

	// Just to make sure lol.
	data["encntr_nfsmw_bg_3"] = song3;

	//-------------------------------------------------------------------------\\
	//----------------------------------SONG 4---------------------------------\\

	ChunkDataMap song4 = data["encntr_nfsmw_bg_4"];
	
	song4["intro_base"] = range(996, 1007 + 1);
	song4["intro_orchestra"] = range(1008, 1019 + 1);
	
	song4["located_orchestra"] = range(1020, 1039 + 1);
	song4["located_base"] = range(1040, 1059 + 1);

	song4["5050_base"] = range(1060, 1093 + 1);
	song4["5050_orchestra"] = range(1094, 1127 + 1);
	
	song4["getting_worse_base"] = range(1128, 1140 + 1);
	song4["getting_worse_orchestra"] = range(1141, 1153 + 1);

	song4["arresting_you"] = range(1154, 1157 + 1);

	song4["running_away_base"] = range(1158, 1173 + 1);
	song4["running_away_orchestra"] = range(1174, 1189 + 1);

	song4["high_speed_cooldown_base"] = range(1190, 1225 + 1);
	song4["high_speed_cooldown_orchestra"] = range(1226, 1261 + 1);

	song4["static_cooldown"] = range(1262, 1270 + 1);

	song4["very_low_speed_cooldown"] = range(1271, 1278 + 1);
	song4["low_speed_cooldown_1"] = range(1279, 1288 + 1);
	song4["low_speed_cooldown_2"] = range(1289, 1297 + 1);

	song4["arrested_1"] = one_num_vec(1298);
	song4["arrested_2"] = one_num_vec(1299);
	song4["arrested_3"] = one_num_vec(1300);
	song4["arrested_4"] = one_num_vec(1301);
	
	song4["evaded_1"] = one_num_vec(1302);
	song4["evaded_2"] = one_num_vec(1303);
	song4["evaded_3"] = one_num_vec(1304);
	song4["evaded_4"] = one_num_vec(1305);
	song4["evaded_5"] = one_num_vec(1306);
	song4["evaded_6"] = one_num_vec(1307);
	song4["evaded_7"] = one_num_vec(1308);
	song4["evaded_8"] = one_num_vec(1309);
	song4["evaded_9"] = range(1310, 1311 + 1);
	song4["evaded_10"] = range(1312, 1313 + 1);

	// Just to make sure lol.
	data["encntr_nfsmw_bg_4"] = song4;

	//-------------------------------------------------------------------------\\

	initialized = true;
	cout << "Initialized chunk data" << endl;
}
