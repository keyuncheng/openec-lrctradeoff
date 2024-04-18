#ifndef __COMPUTE_WORKER_HH__
#define __COMPUTE_WORKER_HH__

#include <isa-l.h>
#include "sockpp/tcp_connector.h"
#include "sockpp/tcp_acceptor.h"

#include "../include/include.hh"
#include "../util/ThreadPool.hh"
#include "../util/Config.hh"
#include "../util/MessageQueue.hh"
#include "../util/MultiWriterQueue.h"
#include "../util/MemoryPool.hh"
#include "Command.hh"
#include "Node.hh"
#include "BlockIO.hh"

class ComputeWorker : public ThreadPool
{
private:
    /* data */
public:
    // config
    Config &config;

    // current worker id
    unsigned int self_worker_id;

    // current connection id
    uint16_t self_conn_id;

    ComputeWorker(Config &_config, unsigned int _self_worker_id, uint16_t _self_conn_id);
    ~ComputeWorker();

    /**
     * @brief thread initializer
     *
     */
    void run() override;

    // erasure coding initializer
    void initECTables();
    void destroyECTables();
    unsigned char gfPow(unsigned char val, unsigned int times);
};

#endif // __COMPUTE_WORKER_HH__