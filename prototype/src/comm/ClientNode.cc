#include "ClientNode.hh"

ClientNode::ClientNode(uint16_t _self_conn_id, Config &_config) : Node(_self_conn_id, _config)
{
    // create command distribution queues
    for (auto &item : connectors_map)
    {
        uint16_t conn_id = item.first;
        cmd_dist_queues[conn_id] = new MessageQueue<Command>(MAX_MSG_QUEUE_LEN);
    }

    // create command distributor
    cmd_distributor = new CmdDist(config, self_conn_id, connectors_map, cmd_dist_queues);

    // create command handler
    cmd_handler = new CmdHandler(config, self_conn_id, sockets_map, NULL);
}

ClientNode::~ClientNode()
{
    // delete command distributor
    delete cmd_distributor;

    // delete command handler
    delete cmd_handler;

    // delete command distribution queues
    for (auto &item : connectors_map)
    {
        uint16_t conn_id = item.first;
        delete cmd_dist_queues[conn_id];
    }
}

void ClientNode::start()
{
}

void ClientNode::stop()
{
}
