#include "Command.hh"

Command::Command(/* args */)
{
    type = CommandType::CMD_UNKNOWN;
    len = 0; // command length
    memset(content, 0, MAX_CMD_LEN);
}

Command::~Command()
{
}

void Command::print()
{
    printf("Command %u, conn: (%u -> %u)", type, src_conn_id, dst_conn_id);
    switch (type)
    {
    case CommandType::CMD_CONN:
    case CommandType::CMD_ACK:
    case CommandType::CMD_STOP:
    case CommandType::CMD_UNKNOWN:
    {
        printf("\n");
        break;
    }
    }
}

void Command::writeUInt(unsigned int val)
{
    unsigned int ns_val = htonl(val);
    memcpy(content + len, (unsigned char *)&ns_val, sizeof(unsigned int));
    len += sizeof(unsigned int);
}

unsigned int Command::readUInt()
{
    unsigned int val;
    memcpy((unsigned char *)&val, content + len, sizeof(unsigned int));
    len += sizeof(unsigned int);
    return ntohl(val);
}

void Command::writeUInt16(uint16_t val)
{
    uint16_t ns_val = htons(val);
    memcpy(content + len, (unsigned char *)&ns_val, sizeof(uint16_t));
    len += sizeof(uint16_t);
}

uint16_t Command::readUInt16()
{
    uint16_t val;
    memcpy((unsigned char *)&val, content + len, sizeof(uint16_t));
    len += sizeof(uint16_t);
    return ntohs(val);
}

void Command::writeString(string &val)
{
    uint32_t slen = val.length();
    writeUInt(slen);
    // string
    if (slen > 0)
    {
        memcpy(content + len, val.c_str(), slen);
        len += slen;
    }
}

string Command::readString()
{
    string val;
    unsigned int slen = readUInt();
    if (slen > 0)
    {
        char *raw_str = (char *)calloc(sizeof(char), slen + 1);
        memcpy(raw_str, content + len, slen);
        len += slen;
        val = string(raw_str);
        free(raw_str);
    }
    return val;
}

void Command::parse()
{
    // the command string has been stored in content

    type = (CommandType)readUInt(); // type
    src_conn_id = readUInt16();     // src conn id
    dst_conn_id = readUInt16();     // dst conn id
    switch (type)
    {
    case CommandType::CMD_CONN:
    case CommandType::CMD_ACK:
    case CommandType::CMD_STOP:
    {
        break;
    }
    case CommandType::CMD_UNKNOWN:
    {
        fprintf(stderr, "invalid command type\n");
        exit(EXIT_FAILURE);
    }
    }
}

void Command::buildCommand(CommandType _type, uint16_t _src_conn_id, uint16_t _dst_conn_id)
{
    type = _type;
    src_conn_id = _src_conn_id;
    dst_conn_id = _dst_conn_id;

    writeUInt(type);          // type
    writeUInt16(src_conn_id); // src conn id
    writeUInt16(dst_conn_id); // dst conn id
}