#ifndef __CLIENT_NODE_HH__
#define __CLIENT_NODE_HH__

#include "../include/include.hh"
#include "../util/Config.hh"
#include "Node.hh"
#include "CmdHandler.hh"
#include "CmdDist.hh"
#include "../util/MessageQueue.hh"

class ClientNode : public Node
{
private:
    /* data */
public:
    // command distribution queues: each retrieves command from CmdHandler and distributes commands to the corresponding CmdDist (CmdHandler<conn_id> -> CmdDist<conn_id>)
    unordered_map<uint16_t, MessageQueue<Command> *> cmd_dist_queues;

    // distribute commands
    CmdDist *cmd_distributor;

    // handler commands
    CmdHandler *cmd_handler;

    ClientNode(uint16_t _self_conn_id, Config &_config);
    ~ClientNode();

    void start();
    void stop();
};

#endif // __CLIENT_NODE_HH__
