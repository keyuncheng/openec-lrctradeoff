#include "ComputeWorker.hh"

ComputeWorker::ComputeWorker(Config &_config, unsigned int _self_worker_id, uint16_t _self_conn_id) : ThreadPool(1), config(_config), self_worker_id(_self_worker_id), self_conn_id(_self_conn_id)
{
    printf("[Node %u, Worker %u] ComputeWorker::ComputeWorker finished initialization\n", self_conn_id, self_worker_id);
}

ComputeWorker::~ComputeWorker()
{
}

void ComputeWorker::run()
{
}

void ComputeWorker::initECTables()
{
}

void ComputeWorker::destroyECTables()
{
}

unsigned char ComputeWorker::gfPow(unsigned char val, unsigned int times)
{
    unsigned char ret_val = 1;

    for (unsigned int i = 0; i < times; i++)
    {
        ret_val = gf_mul(ret_val, val);
    }

    return ret_val;
}
