import csv
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]
backend_path = repo_root / "backend"

if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from sqlmodel import Session, select

from app.core.database import engine
from app.models import NormalizedEvent
from app.services.feature_extractor import (
    build_feature_vector_for_event,
    FEATURE_COLUMNS,
)


def main():
    output_path = repo_root / "ml" / "data" / "processed" / "features.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []

    with Session(engine) as session:
        events = session.exec(select(NormalizedEvent)).all()

        for event in events:
            if not event.timestamp:
                continue

            features = build_feature_vector_for_event(
                session=session,
                event=event,
            )

            rows.append(features)

    fieldnames = [
        "window_start",
        "entity_type",
        "entity_value",
    ] + FEATURE_COLUMNS

    with open(output_path, "w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} feature vectors to {output_path}")


if __name__ == "__main__":
    main()