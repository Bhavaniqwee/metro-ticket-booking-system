from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Booking, Ticket
from metro.models import Station
from metro.utils import build_station_graph, bfs_shortest_path, count_stations, calculate_fare

import qrcode
from io import BytesIO
from django.core.files import File


# ----------------------------------------------------
# BOOK TICKET — NOW WITH SAME STATION + SAME NAME CHECK
# ----------------------------------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def book_ticket_api(request):
    user = request.user

    source_id = request.data.get("source_id")
    destination_id = request.data.get("destination_id")
    passengers = int(request.data.get("passengers", 1))
    is_return = request.data.get("is_return", False)

    if not source_id or not destination_id:
        return Response({"error": "Missing source or destination"}, status=400)

    try:
        source_station = Station.objects.get(id=source_id)
        destination_station = Station.objects.get(id=destination_id)
    except Station.DoesNotExist:
        return Response({"error": "Invalid station ID"}, status=400)

    # ❌ SAME STATION ID
    if source_id == destination_id:
        return Response({"error": "Source and destination cannot be same"}, status=400)

    # ❌ SAME NAME across blue/red line
    if source_station.name == destination_station.name:
        return Response({"error": "Same station selected across different lines"}, status=400)

    # Find shortest path
    graph = build_station_graph()
    path = bfs_shortest_path(graph, source_station.id, destination_station.id)

    if not path:
        return Response({"error": "No route found"}, status=400)

    stations_count = count_stations(path)
    fare_per_person = calculate_fare(stations_count)

    # RETURN TICKET → fare x 2
    if is_return:
        fare_per_person *= 2

    total_amount = fare_per_person * passengers

    # Create booking
    booking = Booking.objects.create(
        user=user,
        source_station=source_station.name,
        destination_station=destination_station.name,
        total_passengers=passengers,
        total_amount=total_amount
    )

    tickets = []

    # Generate tickets with QR
    for i in range(passengers):
        qr_text = f"BOOKING:{booking.id} | PASSENGER:{i+1} | FROM:{source_station.name} | TO:{destination_station.name}"

        qr_image = qrcode.make(qr_text)
        buffer = BytesIO()
        qr_image.save(buffer, format="PNG")

        ticket = Ticket.objects.create(
            booking=booking,
            user=user
        )

        ticket.qr_code.save(
            f"ticket_{ticket.id}.png",
            File(buffer),
            save=True
        )

        tickets.append({
            "ticket_id": ticket.id,
            "type": "Return" if is_return else "One-Way",
            "qr": ticket.qr_code.url
        })

    return Response({
        "booking_id": booking.id,
        "from": source_station.name,
        "to": destination_station.name,
        "passengers": passengers,
        "fare_per_person": fare_per_person,
        "total_amount": total_amount,
        "tickets": tickets
    }, status=200)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_ticket_api(request, ticket_id):
    try:
        ticket = Ticket.objects.get(id=ticket_id, user=request.user)
    except Ticket.DoesNotExist:
        return Response({"error": "Ticket not found"}, status=404)

    if ticket.status == "CANCELLED":
        return Response({"error": "Ticket already cancelled"}, status=400)

    ticket.status = "CANCELLED"
    ticket.save()

    return Response({"message": "Ticket cancelled successfully"}, status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def booking_history_api(request):
    user = request.user

    bookings = Booking.objects.filter(user=user).order_by('-created_at')

    history = []

    for booking in bookings:

        tickets = Ticket.objects.filter(booking=booking)

        ticket_list = []
        for t in tickets:
            ticket_list.append({
                "ticket_id": t.id,
                "status": t.status,
                "qr": t.qr_code.url
            })

        history.append({
            "booking_id": booking.id,
            "source": booking.source_station,
            "destination": booking.destination_station,
            "passengers": booking.total_passengers,
            "total_amount": booking.total_amount,
            "tickets": ticket_list
        })

    return Response(history)