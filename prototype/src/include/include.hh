#ifndef __INCLUDE_HH__
#define __INCLUDE_HH__

// #include <bits/stdc++.h>
#include <iostream>
#include <cstdio>
#include <cmath>
#include <ctime>
#include <cfloat>
#include <climits>
#include <cfloat>
#include <cstring>
#include <cstdlib>
#include <string>
#include <vector>
#include <random>
#include <algorithm>
#include <unordered_map>
#include <map>
#include <queue>
#include <cassert>
#include <fstream>
#include <sstream>
#include <sys/time.h>
#include <typeinfo>

using namespace std;

#define INVALID_NODE_ID UINT16_MAX
#define INVALID_RACK_ID UINT16_MAX
#define CTRL_NODE_ID (INVALID_NODE_ID - 1)
#define GATEWAY_NODE_ID (INVALID_NODE_ID - 2)

#define MAX_MSG_QUEUE_LEN 1024
#define MAX_CMD_LEN 1024
#define MAX_MEM_POOL_SIZE 1

#define TCP_BUFFER_SIZE 4096

#endif // __INCLUDE_HH__