#include "include/include.hh"
#include "util/Config.hh"
#include "comm/CtrlNode.hh"

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

    // CtrlNode ctrl_node(CTRL_NODE_ID, config);

    // ctrl_node.start();
    // ctrl_node.stop();

    printf("Controller::main finished\n");
}