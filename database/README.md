# Database Design

PostgreSQL stores all operational data for both Django REST Framework and FastAPI.

## Main Tables

- `accounts_user`: users with `PASSENGER` or `ADMIN` roles.
- `stations_station`: railway stations with unique codes.
- `trains_train`: train master records.
- `trains_route`: ordered station stops per train.
- `trains_coach`: coaches for each train.
- `trains_seat`: seats within coaches.
- `trains_fare`: class-wise fares and charges.
- `bookings_booking`: PNR, journey, fare, and booking status.
- `bookings_passenger`: passenger details per booking.
- `bookings_seatreservation`: seat assignments with unique `seat + journey_date`.
- `payments_payment`: simulated payment records.
- `cancellations_cancellation`: cancellation workflow and calculated refunds.
- `cancellations_refund`: refund lifecycle.

## Duplicate Seat Protection

Seat reservations use:

- A database transaction in Django booking creation.
- `SELECT ... FOR UPDATE` row locking on requested seats.
- A unique constraint on `(seat, journey_date)`.
- Pre-commit availability validation.

This prevents two users from confirming the same seat on the same journey date.
