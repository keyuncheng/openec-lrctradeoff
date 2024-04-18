#ifndef __COMMAND_HH__
#define __COMMAND_HH__

#include <arpa/inet.h>
#include "../include/include.hh"

enum CommandType
{
    /**
     * @brief connection; acknowledge; stop connection;
     * format: <type | src_conn_id | dst_conn_id>
     */
    CMD_CONN,
    CMD_ACK,
    /**
     * @brief block computation and transfer: computation; relocation (from Controller or from Agent);
     * format: <type | src_conn_id | dst_conn_id | ***>
     */
    CMD_STOP,
    CMD_UNKNOWN,
};

class Command
{
private:
    /* data */
public:
    CommandType type;
    uint64_t len;                       // command length
    unsigned char content[MAX_CMD_LEN]; // content
    uint16_t src_conn_id;               // source connection id
    uint16_t dst_conn_id;               // dst connection id

    Command();
    ~Command();

    void print();

    // type parsing
    void writeUInt(unsigned int val);
    unsigned int readUInt();
    void writeUInt16(uint16_t val);
    uint16_t readUInt16();
    void writeString(string &val);
    string readString();

    // command types
    void parse();

    // CMD_CONN, CMD_ACK, CMD_STOP
    void buildCommand(CommandType _type, uint16_t _src_conn_id, uint16_t _dst_conn_id);
};

#endif // __COMMAND_HH__