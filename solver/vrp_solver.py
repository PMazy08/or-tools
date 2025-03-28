from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from utils.distance import create_distance_matrix

def solve_vrp(data):
    """
    รับข้อมูลในรูปแบบ JSON ที่มี key:
        - depot: [lat, lng]
        - num_vehicles: จำนวนรถ
        - max_stops_per_vehicle: จำนวน stop สูงสุดต่อรถ
        - locations: [ [lat, lng], ... ] สำหรับนักเรียน
    แล้วคืนผลลัพธ์ในรูปแบบ dictionary ที่มี key "trips"
    """
    depot = data["depot"]
    num_vehicles = data["num_vehicles"]
    max_stops_per_vehicle = data["max_stops_per_vehicle"]
    locations = data["locations"]

    # รวม depot กับ locations (ให้ depot อยู่ที่ index 0)
    all_locations = [depot] + locations
    num_locations = len(all_locations)

    # สร้าง distance matrix
    distance_matrix = create_distance_matrix(all_locations)

    # สร้าง Routing Index Manager และ Routing Model
    manager = pywrapcp.RoutingIndexManager(num_locations, num_vehicles, 0)
    routing = pywrapcp.RoutingModel(manager)

    # Callback สำหรับคำนวณระยะทาง
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Callback สำหรับนับจำนวน stop (คืนค่า 0 เมื่อเป็น depot และ 1 เมื่อเป็นลูกค้า)
    def stop_callback(from_index, to_index):
        node = manager.IndexToNode(from_index)
        return 0 if node == 0 else 1

    stop_callback_index = routing.RegisterTransitCallback(stop_callback)
    routing.AddDimension(
        stop_callback_index,
        0,  # ไม่มี slack
        max_stops_per_vehicle,  # จำนวนลูกค้าสูงสุดที่รถแต่ละคันให้บริการได้
        True,  # ค่า cumulative เริ่มต้นที่ 0
        "StopCount"
    )
    stop_dimension = routing.GetDimensionOrDie("StopCount")
    # บังคับให้รถแต่ละคันต้องให้บริการลูกค้าอย่างน้อย 1 จุด (ไม่รวม depot)
    for vehicle_id in range(num_vehicles):
        end_index = routing.End(vehicle_id)
        stop_dimension.CumulVar(end_index).SetMin(1)

    # กำหนดพารามิเตอร์การค้นหา (ใช้ PATH_CHEAPEST_ARC เป็น heuristic เริ่มต้น)
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

    solution = routing.SolveWithParameters(search_parameters)
    if not solution:
        return None

    trips = []
    for vehicle_id in range(num_vehicles):
        index = routing.Start(vehicle_id)
        route = []
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route.append(all_locations[node_index])
            index = solution.Value(routing.NextVar(index))
        # เพิ่ม depot ที่จุดสิ้นสุดของ route
        route.append(all_locations[manager.IndexToNode(index)])
        trips.append({f"route {vehicle_id + 1}": route})
    return {"trips": trips}
