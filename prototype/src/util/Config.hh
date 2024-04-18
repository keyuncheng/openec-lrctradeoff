#ifndef __CONFIG_HH__
#define __CONFIG_HH__

#include "../include/include.hh"
#include "../model/AzureLRC.hh"
#include "../model/ClusterSettings.hh"
#include "../util/inipp.h"

class Config
{
private:
public:
    // Common
    AzureLRC code;
    ClusterSettings settings;

    // Controller
    pair<string, unsigned int> controller_addr;
    pair<string, unsigned int> gateway_addr;
    map<uint16_t, pair<string, unsigned int>> agent_addr_map;
    string metadata_filename; // metadata

    // Agent
    uint64_t block_size; // block size in Bytes

    Config(string filename);
    ~Config();

    void print();
};

#endif // __CONFIG_HH__