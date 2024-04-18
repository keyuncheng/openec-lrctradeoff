#ifndef __AZURE_LRC_HH__
#define __AZURE_LRC_HH__

#include "../include/include.hh"

class AzureLRC
{
private:
    /* data */
public:
    // coding parameters (k,l,g)
    uint8_t k;
    uint8_t l;
    uint8_t g;

    uint8_t n;
    uint8_t m;
    uint8_t b;
    vector<vector<int>> local_groups;

    AzureLRC(/* args */);
    AzureLRC(uint8_t _k, uint8_t _l, uint8_t _g);
    ~AzureLRC();

    /**
     * @brief print coding parameters
     *
     */
    void print();

    /**
     * @brief check the coding parameter is valid
     *
     * @return true
     * @return false
     */
    bool isValid();
};

#endif // __AZURE_LRC_HH__