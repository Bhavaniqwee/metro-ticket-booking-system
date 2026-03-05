from collections import defaultdict, deque
from .models import Station, Fare


# 🔹 Build graph of stations (same line + interchanges)
def build_station_graph():
    graph = defaultdict(list)
    stations = Station.objects.all()

    # 1️⃣ Connect stations in the SAME line using order_number
    for station in stations:
        prev_station = Station.objects.filter(
            line=station.line,
            order_number=station.order_number - 1
        ).first()

        next_station = Station.objects.filter(
            line=station.line,
            order_number=station.order_number + 1
        ).first()

        if prev_station:
            graph[station.id].append(prev_station.id)
            graph[prev_station.id].append(station.id)

        if next_station:
            graph[station.id].append(next_station.id)
            graph[next_station.id].append(station.id)

    # 2️⃣ Connect INTERCHANGE stations (same name, different line)
    for station in stations:
        interchange_stations = Station.objects.filter(
            name=station.name
        ).exclude(id=station.id)

        for inter_station in interchange_stations:
            graph[station.id].append(inter_station.id)
            graph[inter_station.id].append(station.id)

    return graph


# 🔹 BFS shortest path between source and destination
def bfs_shortest_path(graph, start_id, end_id):
    queue = deque([start_id])
    visited = set([start_id])
    parent = {}

    while queue:
        current = queue.popleft()

        if current == end_id:
            break

        for neighbor in graph[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)

    # ❌ No path found
    if end_id not in visited:
        return []

    # 🔁 Reconstruct path
    path = [end_id]
    while path[-1] != start_id:
        path.append(parent[path[-1]])

    path.reverse()
    return path


# 🔹 Count number of stations travelled
def count_stations(path):
    if not path:
        return 0
    return len(path) - 1


# 🔹 Calculate fare using Fare table
def calculate_fare(stations_count):
    fare = Fare.objects.filter(
        min_stations__lte=stations_count,
        max_stations__gte=stations_count
    ).first()

    if fare:
        return fare.price

    return 0
