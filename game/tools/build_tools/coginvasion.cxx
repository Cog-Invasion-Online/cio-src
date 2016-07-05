#define WANT_AUDIO

#include "nirai.h"
#include <datagram.h>
#include <datagramIterator.h>
#include <algorithm>

const char* header = "COGINVASIONONLINE";
const int header_size = 17;

unsigned char iv[16] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
unsigned char key[] = "mmkfcaaph_cio_bm";

bool niraicall_isGameExe()
{
  return true;
}

int niraicall_onPreStart(int argc, char* argv[])
{
    char* ACCOUNT_NAME = std::getenv("ACCOUNT_NAME");
    char* GAME_SERVER = std::getenv("GAME_SERVER");
    char* LOGIN_TOKEN = std::getenv("LOGIN_TOKEN");
    char* GAME_VERSION = std::getenv("GAME_VERSION");
    if (ACCOUNT_NAME == NULL || GAME_SERVER == NULL || LOGIN_TOKEN == NULL || GAME_VERSION == NULL)
    {
      std::cerr << "Exiting: Some environment variables are not set." << std::endl;
      PyErr_Print();
      return 3;
    }
    return 0;
}

int niraicall_onLoadGameData()
{
    fstream gd;

    // Open the file
    gd.open("coginvasion.bin", ios_base::in | ios_base::binary);
	if (!gd.is_open())
    {
        std::cerr << "Unable to open coginvasion.bin! Game cannot run!" << std::endl;
		return 1;
    }

    // Check the header
	char* read_header = new char[header_size];
	gd.read(read_header, header_size);

    if (memcmp(header, read_header, header_size))
    {
        std::cerr << "Invalid header" << std::endl;
        return 1;
    }

    delete[] read_header;

    // Decrypt
    std::stringstream ss;
    ss << gd.rdbuf();
    gd.close();

    std::string rawdata = ss.str();
    unsigned char* decrypted_data = new unsigned char[rawdata.size()];
    int decsize = AES_decrypt((unsigned char*)rawdata.c_str(), rawdata.size(), key, iv, decrypted_data); // Assumes no error

    // Read
    Datagram dg(decrypted_data, decsize);
    DatagramIterator dgi(dg);

    unsigned int num_modules = dgi.get_uint32();
    _frozen* fzns = new _frozen[num_modules + 1];
    std::string module, data;
    int size;

    for (unsigned int i = 0; i < num_modules; ++i)
    {
        module = dgi.get_string();
        size = dgi.get_int32();
        data = dgi.extract_bytes(abs(size));

        char* name = new char[module.size() + 1];
        memcpy(name, module.c_str(), module.size());
        memset(&name[module.size()], 0, 1);

        unsigned char* code = new unsigned char[data.size()];
        memcpy(code, data.c_str(), data.size());

        _frozen fz;
		fz.name = name;
		fz.code = code;
		fz.size = size;

        memcpy(&fzns[i], &fz, sizeof(_frozen));
    }

    nassertd(dgi.get_remaining_size() == 0)
    {
        std::cerr << "Corrupted data!" << std::endl;
        return 1;
    }

    delete[] decrypted_data;

    memset(&fzns[num_modules], 0, sizeof(_frozen));
    PyImport_FrozenModules = fzns;

    return 0;
}

extern "C" PyObject* niraicall_deobfuscate(char* code, Py_ssize_t size)
{
    std::string output(code, size);
    std::reverse(output.begin(), output.end());
    return PyString_FromStringAndSize(output.data(), size);
}
