#include <isa-l.h>
#include "include/include.hh"
#include "util/Utils.hh"
#include "model/AzureLRC.hh"
#include "comm/BlockIO.hh"

int main(int argc, char *argv[])
{
    if (argc != 6)
    {
        printf("usage: ./GenECStripe k l g block_size data_dir\n");
        return -1;
    }

    uint8_t k = atoi(argv[1]);
    uint8_t l = atoi(argv[2]);
    uint8_t g = atoi(argv[3]);
    char *end;
    uint64_t block_size = strtoull(argv[4], &end, 10);
    string data_dir = argv[5];

    AzureLRC lrc(k, l, g);
    if (lrc.isValid() == false)
    {
        printf("invalid input parameters\n");
        exit(EXIT_FAILURE);
    }

    if (data_dir.find_last_of("/") == string::npos)
    {
        printf("invalid input data directory\n");
        exit(EXIT_FAILURE);
    }

    // init rs encoding table (global parity blocks)
    unsigned char *enc_rs_matrix = (unsigned char *)malloc((lrc.k + lrc.g) * lrc.k * sizeof(unsigned char));
    gf_gen_cauchy1_matrix(enc_rs_matrix, lrc.k + lrc.g, lrc.k); // Cauchy matrix

    // init encoding table
    unsigned char *enc_lrc_matrix = (unsigned char *)malloc(lrc.n * lrc.k * sizeof(unsigned char));
    unsigned char *encode_lrc_gftbl = (unsigned char *)malloc(32 * lrc.k * lrc.m * sizeof(unsigned char));

    // Construct LRC encoding matrix
    // (1) create indentity matrix for data blocks
    memcpy(enc_lrc_matrix, enc_rs_matrix, lrc.k * lrc.k * sizeof(unsigned char));
    // (2) create entries for local parity blocks
    uint8_t db_id = 0;
    for (uint8_t lg_id = 0; lg_id < lrc.l; lg_id++)
    {
        for (uint8_t idx = 0; idx < lrc.local_groups[lg_id].size() - 1; idx++)
        {
            enc_lrc_matrix[(lrc.k + lg_id) * lrc.k + db_id] = 1;
            db_id++;
        }
    }
    // (3) create entries for global parity blocks
    memcpy(enc_lrc_matrix + (lrc.k + lrc.l) * lrc.k * sizeof(unsigned char), enc_rs_matrix + lrc.k * lrc.k * sizeof(unsigned char), lrc.k * lrc.g * sizeof(unsigned char));

    printf("LRC encode matrix: \n");
    Utils::printUCharMatrix(enc_lrc_matrix, lrc.n, lrc.k);

    // init ec table
    ec_init_tables(lrc.k, lrc.m, &enc_lrc_matrix[lrc.k * lrc.k], encode_lrc_gftbl);

    // buffers
    unsigned char **data_buffer = (unsigned char **)calloc(lrc.k, sizeof(unsigned char *));
    unsigned char **parity_buffer = (unsigned char **)calloc(lrc.m, sizeof(unsigned char *));

    for (uint8_t db_id = 0; db_id < lrc.k; db_id++)
    {
        data_buffer[db_id] = (unsigned char *)calloc(block_size, sizeof(unsigned char));
        memset(data_buffer[db_id], db_id, block_size); // initialize the content
    }

    for (uint8_t parity_id = 0; parity_id < lrc.m; parity_id++)
    {
        parity_buffer[parity_id] = (unsigned char *)calloc(block_size, sizeof(unsigned char));
    }

    // store data blocks
    for (uint8_t db_id = 0; db_id < lrc.k; db_id++)
    {
        string data_block_path = data_dir + string("block_") + to_string(db_id);

        // write block
        if (BlockIO::writeBlock(data_block_path, data_buffer[db_id], block_size) != block_size)
        {
            fprintf(stderr, "error writing block: %s\n", data_block_path.c_str());
            exit(EXIT_FAILURE);
        }
    }

    // store parity blocks
    ec_encode_data(block_size, lrc.k, lrc.m, encode_lrc_gftbl, data_buffer, parity_buffer);

    for (uint8_t pb_id = 0; pb_id < lrc.m; pb_id++)
    {
        string parity_block_path = data_dir + string("block_") + to_string(lrc.k + pb_id);

        // write block
        if (BlockIO::writeBlock(parity_block_path, parity_buffer[pb_id], block_size) != block_size)
        {
            fprintf(stderr, "error writing block: %s\n", parity_block_path.c_str());
            exit(EXIT_FAILURE);
        }
    }

    // free buffer
    for (uint8_t data_id = 0; data_id < lrc.k; data_id++)
    {
        free(data_buffer[data_id]);
    }

    for (uint8_t parity_id = 0; parity_id < lrc.m; parity_id++)
    {
        free(parity_buffer[parity_id]);
    }
    free(data_buffer);
    free(parity_buffer);

    free(enc_lrc_matrix);
    free(encode_lrc_gftbl);
    free(enc_rs_matrix);

    return 0;
}