#include "ClusterSettings.hh"

ClusterSettings::ClusterSettings()
{
}

ClusterSettings::ClusterSettings(uint16_t _num_nodes, string _rack_profile_raw_str) : num_nodes(_num_nodes)
{
    if (parseRackProfile(_rack_profile_raw_str) == false)
    {
        printf("error: failed to parse rack profile\n");
    }
}

ClusterSettings::~ClusterSettings()
{
}

void ClusterSettings::print()
{
    printf("ClusterSettings: num_nodes: %u\n", num_nodes);
    printf("ClusterSettings: rack_profile\n");
    for (uint16_t rack_id = 0; rack_id < rack_profile.size(); rack_id++)
    {
        printf("rack %u: ", rack_id);
        for (uint16_t idx = 0; idx < rack_profile[rack_id].size(); idx++)
        {
            printf("%u ", rack_profile[rack_id][idx]);
        }
        printf("\n");
    }
}

bool ClusterSettings::isParamValid(const AzureLRC &code)
{
    // check whether the data placement violates single cluster fault
    // tolerance

    // NOT IMPLEMENTED

    return true;
}

bool ClusterSettings::parseRackProfile(string _rack_profile_raw_str)
{
    stringstream ss_rack_list(_rack_profile_raw_str);
    rack_profile.clear();
    uint16_t rack_id = 0;

    while (ss_rack_list.good())
    {
        // get agent list
        string agent_list;
        getline(ss_rack_list, agent_list, '/');
        rack_profile.push_back(vector<uint16_t>());

        stringstream ss_agent_list(agent_list);
        while (ss_agent_list.good())
        {
            string agent_id_str;
            getline(ss_agent_list, agent_id_str, ',');
            rack_profile[rack_id].push_back(stoul(agent_id_str));
        }

        rack_id++;
    }

    printf("finished parsing rack profile\n");

    return true;
}

uint16_t ClusterSettings::getRackIdFromNodeId(uint16_t node_id)
{
    for (uint16_t rack_id = 0; rack_id < rack_profile.size(); rack_id++)
    {
        for (uint16_t idx = 0; idx < rack_profile[rack_id].size(); idx++)
        {
            if (rack_profile[rack_id][idx] == node_id)
            {
                return rack_id;
            }
        }
    }

    return INVALID_RACK_ID;
}