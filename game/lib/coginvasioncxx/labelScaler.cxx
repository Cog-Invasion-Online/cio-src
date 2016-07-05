// Filename: labelScaler.cxx
// Created by:  blach (09Aug15)

#include "labelScaler.h"

LabelScaler::
LabelScaler(NodePath& node, NodePath& camera) :
	_node(node), _cam(camera) {
	_scaling_factor = 0.06;
	_task_mgr = AsyncTaskManager::get_global_ptr();
}

LabelScaler::
~LabelScaler(){

}

float LabelScaler::
get_scaling_factor() {
	return _scaling_factor;
}

NodePath& LabelScaler::
get_np() {
	return _node;
}

NodePath& LabelScaler::
get_cam() {
	return _cam;
}

AsyncTaskManager* LabelScaler::
get_task_mgr() {
	return _task_mgr;
}

AsyncTask::DoneStatus LabelScaler::
do_resize_task() {

	if (_node == NULL || _node.get_error_type() == ErrorType::ET_ok || _node.is_empty()) {
		return AsyncTask::DS_done;
	}

	const float max_distance = 50.0;
	const float min_distance = 1.0;

	double distance = _node.get_pos(_cam).length();
	if (distance > max_distance) {
		distance = max_distance;
	}
	else if (distance < min_distance) {
		distance = min_distance;
	}

	_node.set_scale(sqrt(distance) * _scaling_factor);

	return AsyncTask::DS_cont;
}

AsyncTask::DoneStatus LabelScaler::
resize_task(GenericAsyncTask* task, void* data) {
	return ((LabelScaler*)data)->do_resize_task();
}

void LabelScaler::
resize() {
	PT(GenericAsyncTask) task = new GenericAsyncTask("LabelScaler_resize_task", &LabelScaler::resize_task, (void*) this);
	_task_mgr->add(task);
}
