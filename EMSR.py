import pandas as pd
import numpy as np
from scipy.stats import norm
np.seterr(divide='ignore', invalid='ignore')
# norm.cdf(1.96) = 0.97500210485177952
# norm.ppf(norm.cdf(1.96)) = 1.9599999999999991


# EMSR main
def EMSR_a(lvl_cnt, price_lvl_list, demand_mu_list, demand_sigma_list, all_seats):
    """
    EMSR-a 方法计算各个等级的保留水平
    :param lvl_cnt 价格等级数 int
    :param price_lvl_list 各个等级的价格 list
    :param demand_mu_list 各个等级的需求均值
    :param demand_sigma_list 各个等级的需求方差
    :param all_seats Y舱的容量 CAP_Y
    :return: 各个等级的保留水平
    """
    if (len(price_lvl_list) != lvl_cnt) | (len(demand_mu_list) != lvl_cnt) | (len(demand_sigma_list) != lvl_cnt):
        print("EMSR_a input parameters length not match.")
        return 0
    reserve_lvl = [0 for i in range(0, lvl_cnt-1)]
    # 各等级相对保留水平矩阵
    reserve_mat = np.zeros(shape=(lvl_cnt, lvl_cnt))
    for i in range(0, lvl_cnt):
        for j in range(i+1, lvl_cnt):
            reserve_mat[i][j] = get_reserves_level_a(mu_f=demand_mu_list[i],
                                                   sigma_f=demand_sigma_list[i],
                                                   discount_ratio=price_lvl_list[j]/price_lvl_list[i],
                                                   cap=all_seats)
    print(reserve_mat)
    reserve_lvl = reserve_mat.sum(axis=0)[1:]
    return reserve_lvl


def EMSR_b(lvl_cnt, price_lvl_list, demand_mu_list, demand_sigma_list, all_seats):
    """
    EMSR-b 方法， 修正各个等级
    :param lvl_cnt:
    :param price_lvl_list:
    :param demand_mu_list:
    :param demand_sigma_list:
    :param all_seats:
    :return:
    """
    if (len(price_lvl_list) != lvl_cnt) | (len(demand_mu_list) != lvl_cnt) | (len(demand_sigma_list) != lvl_cnt):
        print("EMSR_a input parameters length not match.")
        return 0
    reserve_lvl = [0 for i in range(0, lvl_cnt)]

    # 7.9 的假设人造等级的参数
    man_made_demand_mu_list = np.zeros(shape=(lvl_cnt))
    man_made_price_lvl_list = np.zeros(shape=(lvl_cnt))
    man_made_price_list_divider = np.zeros(shape=(lvl_cnt))
    man_made_demand_sigma_list = np.zeros(shape=(lvl_cnt))
    man_made_demand_sigma_list_square = np.zeros(shape=(lvl_cnt))

    for i in range(0, lvl_cnt):
        for j in range(0, i):
            man_made_demand_mu_list[i] += demand_mu_list[j] #u
            man_made_price_list_divider[i] += demand_mu_list[j] * price_lvl_list[j]  #p*u
            man_made_demand_sigma_list_square[i] += demand_sigma_list[j]**2  #sigma^2

    man_made_price_lvl_list = man_made_price_list_divider/man_made_demand_mu_list  #  p = p*u/u
    man_made_demand_sigma_list = np.sqrt(man_made_demand_sigma_list_square)  #sigma

    # yj = min[u+sigma*ppf（1-pj/p）,C]
    for i in range(0, lvl_cnt):
        reserve_lvl[i] = get_reserves_level(mu_f = man_made_demand_mu_list[i],
                                            sigma_f = man_made_demand_sigma_list[i],
                                            discount_ratio = price_lvl_list[i]/man_made_price_lvl_list[i],#pj/p
                                            cap = all_seats)

    # print('emsrb-reserve_lvl',reserve_lvl)
    return reserve_lvl[1:]

def get_reserves_level_a(mu_f, sigma_f, discount_ratio, cap):
    return mu_f + sigma_f * (norm.ppf(1-discount_ratio))


def get_reserves_level(mu_f, sigma_f, discount_ratio, cap):
    return min(mu_f + sigma_f * (norm.ppf(1-discount_ratio)), cap)


if __name__ == "__main__":

    # get_reserves_level test 收益管理书 栗子 7.3
    print("reserve level = ", get_reserves_level(70, 1, 0.5, 100))

    # 收益管理书 表 7.3
    # levels = 4
    # prices = [1050, 950, 699, 520]
    # demand_mus = [17.3, 45.1, 39.6, 34.0]
    # demand_sigmas = [5.8, 15.0, 13.2, 11.3]
    # cap_y = 145

    # The.Theory.and.Practice.of.Revenue.Management_2004 Page.44
    levels = 4
    prices = [1050, 567, 534, 520]
    demand_mus = [17.3, 45.1, 39.6, 34.0]
    demand_sigmas = [5.8, 15.0, 13.2, 11.3]
    cap_y = 136

    res_lvl_a = EMSR_a(levels, prices, demand_mus, demand_sigmas, cap_y)
    res_lvl_b = EMSR_b(levels, prices, demand_mus, demand_sigmas, cap_y)
    print("EMSR-a: ", res_lvl_a)
    print("EMSR-b: ", res_lvl_b)

# 结果
# reserve level =  70.0
# EMSR-a:  [ 16.71748442  38.72453728  55.67904129]
# EMSR-b:  [16.717484421033475, 50.944186381631518, 83.154838500614801]