import math
from typing import List, Tuple
from models.container import Container

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1 = math.radians(float(lat1))
    phi2 = math.radians(float(lat2))
    d_phi = math.radians(float(lat2) - float(lat1))
    d_lambda = math.radians(float(lon2) - float(lon1))
    a = math.sin(d_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def generate_optimal_route(containers: List[Container]) -> Tuple[List[str], float, float]:
    # Ordenar por menor capacidad
    ordered = sorted(containers, key=lambda c: c.capacity)

    # Calcular distancia total de la ruta
    total_distance = 0.0
    for i in range(len(ordered) - 1):
        c1 = ordered[i]
        c2 = ordered[i + 1]
        if c1.latitude and c1.longitude and c2.latitude and c2.longitude:
            total_distance += haversine(c1.latitude, c1.longitude, c2.latitude, c2.longitude)

    # Estimar duración (2 min/km)
    estimated_duration = total_distance * 2

    # Obtener lista de GUIDs ordenados
    route_guids = [c.guid for c in ordered]

    return route_guids, round(total_distance, 2), round(estimated_duration, 2)
