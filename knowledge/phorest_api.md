# Phorest API — Integration Reference

## Overview
Phorest is the EMR and booking system used by Treasury Aesthetics. The API is RESTful, versioned, and documented at `developer.phorest.com`.

- **Base URL:** `https://api.phorest.com/v2/`
- **Auth:** OAuth 2.0 (client credentials flow) — obtain `client_id` and `client_secret` from Phorest support
- **Content-Type:** `application/json`

---

## Authentication

```
POST https://auth.phorest.com/oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials
&client_id=YOUR_CLIENT_ID
&client_secret=YOUR_CLIENT_SECRET
```

Response:
```json
{
  "access_token": "...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

Use `Authorization: Bearer <access_token>` on all subsequent requests.

---

## Clients (Patients)

### Create a client
```
POST /v2/business/{businessId}/clients
```
Body fields: `firstName`, `lastName`, `email`, `phone`, `dateOfBirth`, `notes`

### Retrieve a client
```
GET /v2/business/{businessId}/clients/{clientId}
```

### Update a client
```
PATCH /v2/business/{businessId}/clients/{clientId}
```

### Batch retrieval
```
GET /v2/business/{businessId}/clients?page=0&size=50
```

### Client service history
```
GET /v2/business/{businessId}/clients/{clientId}/appointments
```
Returns all past appointments and services received.

### Client categorization / tags
```
GET  /v2/business/{businessId}/clients/{clientId}/categories
POST /v2/business/{businessId}/clients/{clientId}/categories
```
Use categories to tag patients by concern (e.g., "Rosacea", "Anti-aging", "Acne").

---

## Appointments

### List available slots
```
GET /v2/business/{businessId}/appointments/availabilities
```
Query params: `staffId`, `serviceId`, `startDate`, `endDate`

### Create an appointment
```
POST /v2/business/{businessId}/appointments
```
Body:
```json
{
  "clientId": "...",
  "staffId": "...",
  "serviceId": "...",
  "startTime": "2025-07-01T10:00:00",
  "notes": "Rosacea patient — pre-treat with topical numbing"
}
```

### Update an appointment
```
PATCH /v2/business/{businessId}/appointments/{appointmentId}
```

### Cancel an appointment
```
DELETE /v2/business/{businessId}/appointments/{appointmentId}
```

### Check-in a client
```
POST /v2/business/{businessId}/appointments/{appointmentId}/check-in
```

### Appointment notes
```
GET  /v2/business/{businessId}/appointments/{appointmentId}/notes
POST /v2/business/{businessId}/appointments/{appointmentId}/notes
```

---

## Bookings (Online)

### Create a booking
```
POST /v2/business/{businessId}/bookings
```

### Activate / confirm a booking
```
POST /v2/business/{businessId}/bookings/{bookingId}/activate
```

### Cancel a booking
```
DELETE /v2/business/{businessId}/bookings/{bookingId}
```

### Booking notes
```
POST /v2/business/{businessId}/bookings/{bookingId}/notes
```

---

## Staff & Resources

### List staff
```
GET /v2/business/{businessId}/staff
```
Staff members at Treasury Aesthetics:
- **Tammy** — Tox and filler only
- **Physicians (4 providers)** — All device treatments (PlaDuo, VirtueRF, OxyGeneo, DermaTwist, lasers)

### Staff availability
```
GET /v2/business/{businessId}/staff/{staffId}/availabilities
```

### Rooms / machines
```
GET /v2/business/{businessId}/resources
```

### Staff breaks
```
POST /v2/business/{businessId}/staff/{staffId}/breaks
```

---

## Services Catalog

### List services
```
GET /v2/business/{businessId}/services
```

### List products
```
GET /v2/business/{businessId}/products
```

### Courses (treatment packages)
```
GET /v2/business/{businessId}/courses
```

### Vouchers / gift cards
```
GET /v2/business/{businessId}/vouchers
```

---

## Financial

### Purchases / transactions
```
GET /v2/business/{businessId}/purchases
```

### Deposit payment links
```
POST /v2/business/{businessId}/clients/{clientId}/deposit-link
```
Generates a secure payment link to collect a deposit before the appointment.

### Client credit balance
```
GET /v2/business/{businessId}/clients/{clientId}/credit
```

### Loyalty points
```
GET  /v2/business/{businessId}/clients/{clientId}/loyalty-points
POST /v2/business/{businessId}/clients/{clientId}/loyalty-points/redeem
```

---

## Integration with Treatment Plans

### Recommended workflow at Treasury Aesthetics

1. **After agent generates a plan:** Use the exported Word document (Treasury_Aesthetics_*.docx) as the formal patient record
2. **Create appointment series:** Use Phorest appointment API to book each device session in the plan at the correct spacing (4–6 weeks for RF, 6 weeks between RF and laser)
3. **Treatment notes:** After each session, post notes to the appointment record including: device used, settings, patient response, next scheduled date
4. **Progress tracking:** Link OBSERV session URLs in appointment notes for before/after documentation
5. **Product recommendations:** Add recommended Noon and Epicutis products to the client record via the products/service history endpoints

### Booking rules derived from treatment protocols
- VirtueRF sessions: minimum 4 weeks apart (patient safety)
- RF + Laser combination: minimum 6-week gap between modalities
- PlaDuo Pro series: typically 4–6 sessions, 2–4 weeks apart depending on indication
- OxyGeneo: can be booked as standalone or monthly maintenance
- Tox/filler (Tammy): schedule separately from device treatments; book under Tammy's staff ID

---

*Full interactive API reference: `https://developer.phorest.com/reference`*
