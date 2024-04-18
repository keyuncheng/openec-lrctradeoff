#include "AzureLRC.hh"

AzureLRC::AzureLRC(/* args */)
{
}

AzureLRC::AzureLRC(uint8_t _k, uint8_t _l, uint8_t _g)
{
    k = _k;
    l = _l;
    g = _g;

    n = k + l + g;
    m = l + g;
    b = k / l;

    local_groups.resize(l);
    for (int lg_id = 0; lg_id < l; lg_id++)
    {
        local_groups[lg_id].clear();

        // add data blocks
        for (int blk_id = 0; blk_id < b; blk_id++)
        {
            uint8_t db_id = lg_id * b + blk_id;
            if (db_id < k)
            {
                local_groups[lg_id].push_back(db_id);
            }
        }

        // add local parity block
        local_groups[lg_id].push_back(k + lg_id);
    }
}

AzureLRC::~AzureLRC()
{
}

void AzureLRC::print()
{
    printf("AzureLRC(%u,%u,%u), (n,m,b) = (%u, %u, %u)\n", k, l, g, n, m, b);
    printf("local groups:\n");
    for (int lg_id = 0; lg_id < l; lg_id++)
    {
        printf("lg[%u]: ", lg_id);
        for (auto idx = 0; idx < local_groups[lg_id].size(); idx++)
        {
            printf("%d ", local_groups[lg_id][idx]);
        }
        printf("\n");
    }
}

bool AzureLRC::isValid()
{
    return (k % l == 0);
}