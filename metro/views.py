from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import Station
from .utils import (
    build_station_graph,
    bfs_shortest_path,
    count_stations,
    calculate_fare
)

# --------------------------------------
# GET ALL STATIONS
# --------------------------------------
@api_view(['GET'])
@permission_classes([AllowAny])
def stations_api(request):
    stations = Station.objects.all().order_by('order_number')

    data = []
    for s in stations:
        data.append({
            "id": s.id,
            "name": s.name,
            "line": str(s.line)  # convert foreign key to string
        })

    return Response(data, status=200)


# --------------------------------------
# CALCULATE FARE WITH VALIDATION
# --------------------------------------
@api_view(['POST'])
def calculate_fare_api(request):
    source_id = request.data.get("source_id")
    destination_id = request.data.get("destination_id")

    if not source_id or not destination_id:
        return Response({"error": "source_id and destination_id required"}, status=400)

    try:
        source_station = Station.objects.get(id=source_id)
        destination_station = Station.objects.get(id=destination_id)
    except Station.DoesNotExist:
        return Response({"error": "Invalid station ID"}, status=400)

    # ❌ SAME ID → SAME STATION
    if source_id == destination_id:
        return Response({"error": "Source and destination cannot be same"}, status=400)

    # ❌ SAME NAME across different lines (Ameerpet case)
    if source_station.name == destination_station.name:
        return Response({"error": "Same station selected across metro lines"}, status=400)

    # Build graph
    graph = build_station_graph()
    path = bfs_shortest_path(graph, source_station.id, destination_station.id)

    if not path:
        return Response({"error": "No route found"}, status=400)

    stations_count = count_stations(path)
    fare = calculate_fare(stations_count)

    return Response({
        "stations_count": stations_count,
        "fare": fare
    })