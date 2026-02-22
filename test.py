from alns import LiLimParser

if __name__ == "__main__":
    test_instance = LiLimParser.parse(
        r"D:\PYPJ\pdptw_alns\pdp_100\pdp_100\lc101.txt")

    print(test_instance._number_of_vehicles)
    print(test_instance._vehicle_capacity)
    print(len(test_instance._tasks))
    print(len(test_instance._requests))
    print(test_instance._requests)
    print(test_instance._distance_matrix[(1, 2)])
    print(test_instance._depot_x, test_instance._depot_y)
