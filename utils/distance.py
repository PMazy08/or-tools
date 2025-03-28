import math

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    คำนวณระยะทาง (เมตร) ระหว่างจุดสองจุดบนพื้นโลกโดยใช้สูตร Haversine
    """
    R = 6371000  # รัศมีโลก (เมตร)
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def create_distance_matrix(all_locations):
    """
    สร้าง distance matrix จากรายการพิกัดทั้งหมด
    """
    size = len(all_locations)
    matrix = [[0] * size for _ in range(size)]
    for i in range(size):
        for j in range(size):
            if i == j:
                matrix[i][j] = 0
            else:
                matrix[i][j] = int(haversine_distance(
                    all_locations[i][0], all_locations[i][1],
                    all_locations[j][0], all_locations[j][1]
                ))
    return matrix
