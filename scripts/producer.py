import argparse
import json
import random
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RNG = random.Random(42)

CITIES = {
    "Casablanca": "CAS",
    "Rabat": "RAB",
    "Marrakech": "MAR",
    "Tanger": "TAN",
}

ZONES = [
    "gare", "universite", "residentiel",
    "centre_affaires", "tourisme", "plage"
]

STATUSES = [
    "RESERVED", "UNLOCKED", "ENDED",
    "CANCELLED", "FAULT_REPORTED"
]

VEHICLES = ["BIKE", "EBIKE", "SCOOTER"]


def generate_stations():
    stations = []
    for city, code in CITIES.items():
        for i in range(1, 101):
            zone = ZONES[(i - 1) % len(ZONES)]
            stations.append({
                "station_id": f"S-{code}-{i:03d}",
                "name": f"Station {city} {i}",
                "city": city,
                "quartier": f"Quartier {((i-1)//10)+1}",
                "zone_type": zone,
                "capacity": RNG.randint(10, 40),
                "latitude": {
                    "Casablanca": 33.5731,
                    "Rabat": 34.0209,
                    "Marrakech": 31.6295,
                    "Tanger": 35.7595
                }[city] + RNG.uniform(-0.04, 0.04),
                "longitude": {
                    "Casablanca": -7.5898,
                    "Rabat": -6.8416,
                    "Marrakech": -7.9811,
                    "Tanger": -5.8340
                }[city] + RNG.uniform(-0.04, 0.04)
            })

    DATA.mkdir(exist_ok=True)
    with open(DATA / "stations.json", "w", encoding="utf-8") as f:
        json.dump(stations, f, ensure_ascii=False, indent=2)
    return stations


def generate_events(n, stations):
    by_city = {
        city: [s for s in stations if s["city"] == city]
        for city in CITIES
    }

    events = []
    base = datetime(2026, 11, 15, tzinfo=timezone.utc)
    unique_count = n - round(n * 0.02)

    for i in range(unique_count):
        city = RNG.choice(list(CITIES))
        candidates = by_city[city]
        event_time = base + timedelta(seconds=i * 2)
        hour = event_time.hour

        start = RNG.choice(candidates)
        end = RNG.choice(candidates)

        # Flux pendulaires du matin et du soir
        if hour in (7, 8, 9):
            start = next(s for s in candidates
                         if s["zone_type"] == "residentiel")
            end = next(s for s in candidates
                       if s["zone_type"] == "centre_affaires")
        elif hour in (17, 18, 19):
            start = next(s for s in candidates
                         if s["zone_type"] == "centre_affaires")
            end = next(s for s in candidates
                       if s["zone_type"] == "residentiel")

        # Station qui se vide progressivement
        if city == "Rabat" and i % 15 == 0:
            start = candidates[0]
            end = candidates[20]

        # Boucle touristique Marrakech A -> B -> C -> A
        if city == "Marrakech" and i % 20 == 0:
            a, b, c = candidates[4], candidates[10], candidates[16]
            cycle = [(a, b), (b, c), (c, a)]
            start, end = cycle[(i // 20) % 3]

        status = RNG.choices(
            STATUSES,
            weights=[15, 15, 60, 7, 3],
            k=1
        )[0]

        vehicle_type = RNG.choice(VEHICLES)
        finished = status == "ENDED"

        duration = RNG.randint(180, 3600) if finished else None
        distance = round(RNG.uniform(0.5, 12), 2) if finished else None

        event = {
            "trip_id": f"T-{i+1:08d}",
            "user_id": f"U-{RNG.randint(1, 10000):05d}",
            "vehicle_id": (
                "V-EB-0931" if status == "FAULT_REPORTED"
                and i % 4 == 0
                else f"V-{RNG.randint(1, 2000):05d}"
            ),
            "vehicle_type": vehicle_type,
            "start_station": start["station_id"],
            "end_station": end["station_id"] if finished else None,
            "city": city,
            "status": status,
            "duration_s": duration,
            "distance_km": distance,
            "battery_pct": (
                RNG.randint(5, 100)
                if vehicle_type != "BIKE" else None
            ),
            "price_mad": (
                round(2.5 + duration / 60 * 0.65, 2)
                if finished else None
            ),
            "event_time": event_time.isoformat().replace("+00:00", "Z")
        }
        events.append(event)

    # Environ 2 % de doublons exacts
    duplicates = [
        dict(e) for e in RNG.sample(events, n - unique_count)
    ]

    # Retards simules : deplacement dans l'ordre d'arrivee
    # Les event_time restent inchanges.
    delayed_count = round(len(events) * 0.05)
    indices = set(RNG.sample(range(len(events)), delayed_count))
    delayed = [e for j, e in enumerate(events) if j in indices]
    normal = [e for j, e in enumerate(events) if j not in indices]
    events = normal + delayed + duplicates

    path = DATA / "bronze" / "trips_history.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        for event in events:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

    counts = Counter(e["status"] for e in events)
    print(f"Stations : {len(stations)}")
    print(f"Evenements : {len(events)}")
    print(f"Doublons ajoutes : {len(duplicates)}")
    print(f"Evenements reordonnes : {delayed_count}")
    print("Statuts :", dict(counts))
    print("Fichier :", path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="file", choices=["file"])
    parser.add_argument("--n", type=int, default=50000)
    args = parser.parse_args()

    if args.n < 1:
        parser.error("--n doit etre positif")

    stations = generate_stations()
    generate_events(args.n, stations)


if __name__ == "__main__":
    main()
