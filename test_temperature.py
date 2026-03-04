from alns import LiLimParser, ALNS
from evaluator_layer import FeasibilityChecker
import copy


def green_text(text: str) -> str:
    return f"\033[92m{text}\033[0m"


def yellow_text(text: str) -> str:
    return f"\033[93m{text}\033[0m"


if __name__ == "__main__":
    test_instance = LiLimParser.parse("./pdp_100/pdp_100/lc101.txt")

    test_alns = ALNS(test_instance)
    initial_solution = test_alns.best_feasible_solution

    print(green_text("初始解信息:"))
    print(f"初始成本: {test_alns.best_feasible_cost:.2f}")
    print(f"初始温度: {test_alns.temperature:.6f}")
    print(
        f"温度/成本比: {test_alns.temperature / test_alns.best_feasible_cost:.6f}")
    print(f"降温速率 alpha: {test_alns.alpha}")
    print('=' * 80)

    solution = copy.deepcopy(initial_solution)

    ITER_NUM = 500
    cost_improvements = []
    cost_worsenings = []

    for i in range(ITER_NUM):
        old_cost = test_alns.calculate_obj(solution)
        old_temp = test_alns.temperature

        solution = test_alns.iterate(solution)

        new_cost = test_alns.calculate_obj(solution)
        new_temp = test_alns.temperature

        cost_diff = new_cost - old_cost

        # 记录成本变化
        if cost_diff < 0:
            cost_improvements.append(abs(cost_diff))
        elif cost_diff > 0:
            cost_worsenings.append(cost_diff)

        # 每50次迭代输出详细信息
        if (i + 1) % 50 == 0:
            stats = test_alns.get_stats()
            print(yellow_text(f"\n迭代 {i+1}:"))
            print(f"当前成本: {new_cost:.2f}")
            print(f"当前温度: {new_temp:.6f}")
            print(f"温度/成本比: {new_temp / new_cost:.6f}")
            print(f"最优成本: {test_alns.best_feasible_cost:.2f}")
            print(
                f"统计: better={stats['better_accepted']}, worse_cand={stats['worse_candidates']}, worse_acc={stats['worse_accepted']}")
            if stats['worse_candidates'] > 0:
                accept_rate = stats['worse_accepted'] / \
                    stats['worse_candidates'] * 100
                print(f"劣解接受率: {accept_rate:.1f}%")

            # 成本差值统计
            if cost_improvements:
                avg_imp = sum(cost_improvements) / len(cost_improvements)
                print(f"平均改进幅度: {avg_imp:.4f}")
            if cost_worsenings:
                avg_worse = sum(cost_worsenings) / len(cost_worsenings)
                print(f"平均恶化幅度: {avg_worse:.4f}")
                # 计算理论接受概率
                from math import exp
                theoretical_prob = exp(-avg_worse / new_temp)
                print(
                    f"理论接受概率 exp(-{avg_worse:.4f}/{new_temp:.6f}) = {theoretical_prob:.4f}")

            # 清空统计
            cost_improvements = []
            cost_worsenings = []
            print('-' * 80)

    print(green_text(f"\n最终统计:"))
    stats = test_alns.get_stats()
    print(f"总迭代: {stats['iterations']}")
    print(f"改进接受: {stats['better_accepted']}")
    print(f"劣解候选: {stats['worse_candidates']}")
    print(f"劣解接受: {stats['worse_accepted']}")
    if stats['worse_candidates'] > 0:
        print(
            f"总体劣解接受率: {stats['worse_accepted']/stats['worse_candidates']*100:.1f}%")
    print(f"最优可行解成本: {test_alns.best_feasible_cost:.2f}")
    print(f"最终温度: {test_alns.temperature:.6f}")

    print(green_text("\n算子权重变化:"))
    print(
        f"Destroy weights: {[f'{w:.3f}' for w in test_alns.destroy_weights]}")
    print(f"Repair weights: {[f'{w:.3f}' for w in test_alns.repair_weights]}")
