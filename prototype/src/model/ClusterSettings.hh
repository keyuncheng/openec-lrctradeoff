#ifndef __CLUSTER_SETTINGS_HH__
#define __CLUSTER_SETTINGS_HH__

#include "../include/include.hh"
#include "AzureLRC.hh"

class ClusterSettings
{
private:
    /* data */
public:
    uint16_t num_nodes;
    vector<vector<uint16_t>> rack_profile;

    ClusterSettings();
    ClusterSettings(uint16_t _num_nodes, string _rack_profile_raw_str);
    ~ClusterSettings();

    /**
     * @brief print cluster settings
     *
     */
    void print();

    /**
     * @brief check if the parameters are valid
     *
     * @param code
     * @return true
     * @return false
     */
    bool isParamValid(const AzureLRC &code);

    /**
     * @brief parse rack profile raw string
     *
     * @param rack profile raw string
     * @return success
     * @return failure
     */
    bool parseRackProfile(string _rack_profile_raw_str);

    /**
     * @brief Get rack id From node id
     *
     * @param node_id
     * @return uint16_t
     */
    uint16_t getRackIdFromNodeId(uint16_t node_id);
};

#endif // __CLUSTER_SETTINGS_HH__