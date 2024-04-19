#include "include/include.hh"
#include "util/Config.hh"
#include "comm/AgentNode.hh"

int main(int argc, char **argv)
{
    if (argc != 3)
    {
        printf("usage: ./Agent agent_id config_filename\n");
        return -1;
    }

    uint16_t agent_id = atoi(argv[1]);
    string config_filename = argv[2];

    Config config(config_filename);
    config.print();

    AgentNode agent_node(agent_id, config);

    agent_node.start();

    agent_node.stop();

    printf("Agent::main finished\n");
}