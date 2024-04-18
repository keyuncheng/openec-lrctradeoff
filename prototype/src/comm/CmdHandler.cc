#include "CmdHandler.hh"

CmdHandler::CmdHandler(Config &_config, uint16_t _self_conn_id,
                       unordered_map<uint16_t, sockpp::tcp_socket> &_sockets_map,
                       unordered_map<uint16_t, MessageQueue<Command> *> *_cmd_dist_queues) : ThreadPool(1), config(_config), self_conn_id(_self_conn_id), sockets_map(_sockets_map), cmd_dist_queues(_cmd_dist_queues)
{
    for (auto &item : sockets_map)
    {
        uint16_t conn_id = item.first;
        handler_threads_map[conn_id] = NULL;
    }
}

CmdHandler::~CmdHandler()
{
}

void CmdHandler::run()
{
    // create cmd handler thread for Controller and Agents
    for (auto &item : handler_threads_map)
    {
        uint16_t conn_id = item.first;
        if (conn_id == CTRL_NODE_ID)
        {
            item.second = new thread(&CmdHandler::handleCmdFromController, this);
        }
        else
        {
            item.second = new thread(&CmdHandler::handleCmdFromAgent, this, conn_id);
        }
    }

    // distribute stop commands (from Agents only)
    if (self_conn_id != CTRL_NODE_ID)
    {
        distStopCmds();
    }

    // join cmd handler thread for both Controller and Agents
    for (auto &item : handler_threads_map)
    {
        thread *cmd_handler_thd = item.second;
        cmd_handler_thd->join();
        delete cmd_handler_thd;
    }
}

void CmdHandler::handleCmdFromController()
{
    printf("[Node %u] CmdHandler::handleCmdFromController start to handle commands from Controller\n", self_conn_id);

    uint16_t src_conn_id = CTRL_NODE_ID;
    auto &skt = sockets_map[src_conn_id];

    while (true)
    {
        Command cmd;
        // retrieve command
        auto ret_val = skt.read_n(cmd.content, MAX_CMD_LEN * sizeof(unsigned char));
        if (ret_val.is_error())
        {
            fprintf(stderr, "CmdHandler::handleCmdFromController error reading command\n");
            exit(EXIT_FAILURE);
        }
        else if (ret_val.release() == 0)
        {
            // currently, no cmd comming in
            printf("CmdHandler::handleCmdFromController no command coming in, break\n");
            break;
        }

        // parse the command
        cmd.parse();
    }

    printf("[Node %u] CmdHandler::handleCmdFromController finished handling commands from Controller\n", self_conn_id);
}

void CmdHandler::handleCmdFromAgent(uint16_t src_conn_id)
{
    printf("[Node %u] CmdHandler::handleCmdFromAgent start to handle commands from Agent %u\n", self_conn_id, src_conn_id);

    auto &skt = sockets_map[src_conn_id];

    while (true)
    {
        Command cmd;
        // retrieve command

        auto ret_val = skt.read_n(cmd.content, MAX_CMD_LEN * sizeof(unsigned char));
        if (ret_val.is_error())
        {
            fprintf(stderr, "CmdHandler::handleCmdFromAgent error reading command\n");
            exit(EXIT_FAILURE);
        }
        else if (ret_val.release() == 0)
        {
            // currently, no cmd coming in
            printf("CmdHandler::handleCmdFromAgent no command coming in, break\n");
            break;
        }

        // parse the command
        cmd.parse();

        // cmd.print();
        // printf("CmdHandler::handleCmdFromAgent handle command, type: %u, (%u -> %u), post: (%u, %u)\n", cmd.type, cmd.src_conn_id, cmd.dst_conn_id, cmd.post_stripe_id, cmd.post_block_id);

        // validate command
        if (cmd.src_conn_id != src_conn_id || cmd.dst_conn_id != self_conn_id)
        {
            fprintf(stderr, "CmdHandler::handleCmdFromAgent error: invalid command content\n");
            exit(EXIT_FAILURE);
        }

        if (cmd.type == CommandType::CMD_STOP)
        {
            // printf("CmdHandler::handleCmdFromAgent received stop command from Agent %u\n", cmd.src_conn_id);
            skt.close();
            break;
        }
    }

    printf("[Node %u] CmdHandler::handleCmdFromAgent finished handling commands for Agent %u\n", self_conn_id, src_conn_id);
}

void CmdHandler::distStopCmds()
{
    // distribute terminate commands
    for (auto &item : sockets_map)
    {
        uint16_t dst_conn_id = item.first;

        Command cmd_disconnect;
        cmd_disconnect.buildCommand(CommandType::CMD_STOP, self_conn_id, dst_conn_id);

        // add to cmd_dist_queue
        (*cmd_dist_queues)[dst_conn_id]->Push(cmd_disconnect);
    }
}