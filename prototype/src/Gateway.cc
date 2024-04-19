#include "include/include.hh"
#include "util/Config.hh"
#include "comm/GatewayNode.hh"

int main(int argc, char **argv)
{
    if (argc != 2)
    {
        printf("usage: ./Controller config_filename\n");
        return -1;
    }

    string config_filename = argv[1];

    Config config(config_filename);
    config.print();

    GatewayNode gateway_node(GATEWAY_NODE_ID, config);

    gateway_node.start();
    gateway_node.stop();

    printf("Controller::main finished\n");
}