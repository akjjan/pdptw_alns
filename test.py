from alns import LiLimParser

if __name__ == "__main__":
    test_instance = LiLimParser.parse(
        "./pdp_100/pdp_100/lc101.txt")

    print(test_instance.number_of_vehicles_)
    print(test_instance.vehicle_capacity_)
    print(len(test_instance.tasks_))
    print(len(test_instance.requests_))
    print(test_instance.requests_)
    print(test_instance.distance_matrix_[(1, 2)])
    print(test_instance.depot_x_, test_instance.depot_y_)
