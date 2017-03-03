/**
 * COG INVASION ONLINE
 * Copyright (c) CIO Team. All rights reserved.
 *
 * @file tools.cxx
 * @author Brian Lach
 * @date 2016-06-28
 */

#include <vector>
#include <fstream>
#include <windows.h>

using namespace std;

static vector<string> explode(const string &delimiter, const string &str)
{
	vector<string> arr;

	int strleng = str.length();
	int delleng = delimiter.length();
	if (delleng == 0)
		return arr;//no change

	int i = 0;
	int k = 0;
	while (i<strleng)
	{
		int j = 0;
		while (i + j<strleng && j<delleng && str[i + j] == delimiter[j])
			j++;
		if (j == delleng)//found delimiter
		{
			arr.push_back(str.substr(k, i - k));
			i += delleng;
			k = i;
		}
		else
		{
			i++;
		}
	}
	arr.push_back(str.substr(k, i - k));
	return arr;
}

static int get_file_length(ifstream &t)
{
	int length;
	t.seekg(0, ios::end);
	length = t.tellg();
	t.seekg(0, ios::beg);
	return length;
}

static vector<int> range(int start, int end) {
	vector<int> range_vector;
	range_vector.push_back(start);
	int index = 1;
	while (start + index < end) {
		range_vector.push_back(start + index);
		index++;
	}
	return range_vector;
}

static vector<int> one_num_vec(int num) {
	vector<int> vec;
	vec.push_back(num);
	return vec;
}

static int filter(unsigned int code) {
	if (code == EXCEPTION_ACCESS_VIOLATION) {
		return EXCEPTION_EXECUTE_HANDLER;
	}
	return EXCEPTION_CONTINUE_SEARCH;
}