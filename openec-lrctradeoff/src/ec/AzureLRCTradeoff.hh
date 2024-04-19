#ifndef __AZURE_LRC_TRADEOFF_HH__
#define __AZURE_LRC_TRADEOFF_HH__

#include "Computation.hh"
#include "ECBase.hh"

using namespace std;

#define RS_N_MAX (32)

class AzureLRCTradeoff : public ECBase
{
private:
    int _l;
    int _g;
    int *_encode_matrix = NULL;

    void generateMatrix(int *matrix, int k, int l, int r, int w);

    ECDAG *DecodeSingleRepair(vector<int> from, vector<int> to);
    ECDAG *DecodeMaintenance(vector<int> from, vector<int> to);

public:
    AzureLRCTradeoff(int n, int k, int w, int opt, vector<string> param);
    ~AzureLRCTradeoff();

    ECDAG *Encode();
    ECDAG *Decode(vector<int> from, vector<int> to);
    void Place(vector<vector<int>> &group);
};

#endif // __AZURE_LRC_TRADEOFF_HH__