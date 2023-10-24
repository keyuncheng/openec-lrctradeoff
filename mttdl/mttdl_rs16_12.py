import numpy as np

# RS(16,12) MTTDL

# num_nodes
num_nodes = 400

# bw (Gbps)
bw_Gbps = 1

# data (TB)
data_TB = 16

# mttf_node_year
mttf_node_year = 4

# repair_time (min)
repair_time_min = 30

# avail_rp_bw (percentage)
avail_rp_bw = 0.1

# single repair cost
single_rp_cost = 12

# single node fail rate
single_node_fail_rate_year = 1.0 / mttf_node_year

# node repair rate (single, multiple)
single_rp_rate_year = 1.0 * avail_rp_bw * (num_nodes - 1) * (bw_Gbps * (3600 * 24 * 365)) * (10**9) / (single_rp_cost * data_TB * (10**12) * 8)
multi_rp_rate_year = 1.0 * (3600 * 24 * 365) / ((30 * 60))

print(single_rp_cost)
print(single_node_fail_rate_year)
print(single_rp_rate_year)
print(multi_rp_rate_year)

lp_mtx = np.array([
    [-(16*single_node_fail_rate_year), single_rp_rate_year, 0.0, 0.0, 0.0],
    [16*single_node_fail_rate_year, -(15*single_node_fail_rate_year+single_rp_rate_year), multi_rp_rate_year, 0.0, 0.0],
    [0.0, 15*single_node_fail_rate_year, -(14*single_node_fail_rate_year+multi_rp_rate_year), multi_rp_rate_year, 0.0],
    [0.0, 0.0, 14*single_node_fail_rate_year, -(13*single_node_fail_rate_year+multi_rp_rate_year), multi_rp_rate_year],
    [0.0, 0.0, 0.0, 13*single_node_fail_rate_year, -(12*single_node_fail_rate_year+multi_rp_rate_year)]
    ])

right = np.array([-1, 0.0, 0.0, 0.0, 0.0])

print(lp_mtx)
print(right)
sol = np.linalg.solve(lp_mtx, right)
print(sol)
print("{:e}".format(np.sum(sol)))

print(np.sum(sol))