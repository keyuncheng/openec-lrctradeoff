#ifndef __CTRL_NODE_HH__
#define __CTRL_NODE_HH__

#include "../include/include.hh"
#include "../util/Config.hh"
#include "Node.hh"
#include "CmdHandler.hh"
#include "CmdDist.hh"
#include "../util/MessageQueue.hh"

class CtrlNode : public Node
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

    CtrlNode(uint16_t _self_conn_id, Config &_config);
    ~CtrlNode();

    void start();
    void stop();

    void genCommands(vector<Command> &commands);
};

#endif // __CTRL_NODE_HH__
