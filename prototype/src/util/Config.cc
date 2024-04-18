#include "Config.hh"

Config::Config(string filename)
{
    inipp::Ini<char> ini;
    std::ifstream is(filename);
    ini.parse(is);

    // Common
    unsigned int k = 0, l = 0, g = 0;
    inipp::get_value(ini.sections["Common"], "k", k);
    inipp::get_value(ini.sections["Common"], "l", l);
    inipp::get_value(ini.sections["Common"], "g", g);

    // Controller
    unsigned int num_nodes = 0;
    inipp::get_value(ini.sections["Controller"], "num_nodes", num_nodes);
    string controller_addr_raw;
    inipp::get_value(ini.sections["Controller"], "controller_addr", controller_addr_raw);
    string gateway_addr_raw;
    inipp::get_value(ini.sections["Controller"], "gateway_addr", gateway_addr_raw);
    string agent_addrs_raw;
    inipp::get_value(ini.sections["Controller"], "agent_addrs", agent_addrs_raw);
    string rack_profile_raw;
    inipp::get_value(ini.sections["Controller"], "rack_profile", rack_profile_raw);
    inipp::get_value(ini.sections["Controller"], "metadata_filename", metadata_filename);

    // controller ip, port
    auto delim_pos = controller_addr_raw.find(":");
    string controller_ip = controller_addr_raw.substr(0, delim_pos);
    unsigned int controller_port = stoul(controller_addr_raw.substr(delim_pos + 1, controller_addr_raw.size() - controller_ip.size() - 1).c_str());
    controller_addr = pair<string, unsigned int>(controller_ip, controller_port);

    // gateway ip, port
    delim_pos = gateway_addr_raw.find(":");
    string gateway_ip = gateway_addr_raw.substr(0, delim_pos);
    unsigned int gateway_port = stoul(gateway_addr_raw.substr(delim_pos + 1, gateway_addr_raw.size() - gateway_ip.size() - 1).c_str());
    gateway_addr = pair<string, unsigned int>(gateway_ip, gateway_port);

    // agent ip, port
    uint16_t aid = 0;
    stringstream ss_agent_addr(agent_addrs_raw);
    while (ss_agent_addr.good())
    {
        string agent_addr_str;
        getline(ss_agent_addr, agent_addr_str, ',');

        delim_pos = agent_addr_str.find(":");
        string agent_ip = agent_addr_str.substr(0, delim_pos);
        printf("%s\n", agent_ip.c_str());
        unsigned int agent_port = stoul(agent_addr_str.substr(delim_pos + 1, agent_addr_str.size() - agent_ip.size() - 1).c_str());
        agent_addr_map[aid] = pair<string, unsigned int>(agent_ip, agent_port);
        aid++;
    }

    // Agent
    inipp::get_value(ini.sections["Agent"], "block_size", block_size);

    // init parameters
    code = AzureLRC(k, l, g);
    settings = ClusterSettings(num_nodes, rack_profile_raw);
}

Config::~Config()
{
}

void Config::print()
{
    printf("========= Configurations ==========\n");

    printf("========= Common ==========\n");
    code.print();
    printf("===========================\n");

    printf("========= Controller ==========\n");
    printf("address: %s:%u\n", controller_addr.first.c_str(), controller_addr.second);
    printf("metadata_filename: %s\n", metadata_filename.c_str());
    settings.print();
    printf("===========================\n");

    printf("========= Gateway ==========\n");
    printf("address: %s:%u\n", gateway_addr.first.c_str(), gateway_addr.second);
    printf("===========================\n");

    printf("========= Agents ==========\n");
    printf("block_size: %lu\n", block_size);
    printf("addresses: (%lu)\n", agent_addr_map.size());
    for (auto &item : agent_addr_map)
    {
        auto &agent_addr = item.second;
        auto node_id = item.first;
        printf("Agent %u (rack %u), ip: %s:%d\n", node_id, settings.getRackIdFromNodeId(node_id), agent_addr.first.c_str(), agent_addr.second);
    }
    printf("===========================\n");
}