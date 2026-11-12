
import re
from datetime import datetime, timezone
from typing import Any

from src.models.oem_part import OEMPart


class CatalogMatchNotFound(Exception):
    """No matching catalog item was found."""


class CatalogService:

    PART_TERMS = {
        "brake disc": ["тормозной диск", "brake disc", "brake rotor"],
        "brake discs": ["тормозной диск", "brake disc", "brake rotor"],
        "brake rotor": ["тормозной диск", "brake disc", "brake rotor"],
        "brake rotors": ["тормозной диск", "brake disc", "brake rotor"],
        "brake pad": [
            "тормозная колодка",
            "тормозные колодки",
            "brake pad",
        ],
        "brake pads": [
            "тормозная колодка",
            "тормозные колодки",
            "brake pad",
        ],
    }

    @staticmethod
    def _normalize(value: str) -> str:
        value = value.lower().strip()
        value = re.sub(r"[^a-zа-яё0-9 ]", " ", value)
        return " ".join(value.split())

    @staticmethod
    def _get_items(data: Any, key: str) -> list[dict]:
        if not isinstance(data, dict):
            return []

        items = data.get(key, [])
        return items if isinstance(items, list) else []

    def find_manufacturer(
        self,
        response_data: dict,
        requested_make: str,
    ) -> dict:
        manufacturers = self._get_items(response_data, "mf")
        requested = self._normalize(requested_make)

        matches = []

        for manufacturer in manufacturers:
            names = [
                manufacturer.get("ds", ""),
                manufacturer.get("da", ""),
            ]

            if any(
                self._normalize(name) == requested
                for name in names
                if name
            ):
                matches.append(manufacturer)

        if not matches:
            raise CatalogMatchNotFound(
                f"Manufacturer not found: {requested_make}"
            )

        if len(matches) > 1:
            raise CatalogMatchNotFound(
                f"Multiple manufacturers matched: {requested_make}"
            )

        return matches[0]

    def find_models(
        self,
        response_data: dict,
        requested_model: str,
        requested_year: int,
    ) -> list[dict]:
        models = self._get_items(response_data, "m")
        requested = self._normalize(requested_model)

        matches = []

        for model in models:
            names = [
                model.get("d", ""),
                model.get("fd", ""),
            ]

            name_matches = any(
                requested in self._normalize(name)
                for name in names
                if name
            )

            if not name_matches:
                continue

            start_year = self._timestamp_year(model.get("cb"))
            end_year = self._timestamp_year(model.get("ce"))

            if start_year is not None and requested_year < start_year:
                continue

            if end_year is not None and requested_year > end_year:
                continue

            matches.append(model)

        return matches

    @staticmethod
    def _timestamp_year(timestamp: int | None) -> int | None:
        if not timestamp:
            return None

        return datetime.fromtimestamp(
            timestamp / 1000,
            tz=timezone.utc,
        ).year

    def find_part_nodes(
        self,
        tree_data: Any,
        part_name: str,
    ) -> list[dict]:
        normalized_part = self._normalize(part_name)
        search_terms = self.PART_TERMS.get(normalized_part)

        if not search_terms:
            raise CatalogMatchNotFound(
                f"Unsupported catalog part mapping: {part_name}"
            )

        normalized_terms = [
            self._normalize(term) for term in search_terms
        ]

        matches = []
        visited_ids = set()

        def walk(item: Any):
            if isinstance(item, dict):
                node_id = item.get("i")

                searchable_values = [
                    str(value)
                    for value in item.values()
                    if isinstance(value, (str, int, float))
                ]

                searchable_text = self._normalize(
                    " ".join(searchable_values)
                )

                is_match = any(
                    term in searchable_text
                    for term in normalized_terms
                )

                if is_match and node_id is not None:
                    if node_id not in visited_ids:
                        matches.append(item)
                        visited_ids.add(node_id)

                for value in item.values():
                    walk(value)

            elif isinstance(item, list):
                for child in item:
                    walk(child)

        walk(tree_data)
        return matches

    @staticmethod
    def _extract_oem_records(data: Any) -> list[dict]:
        """Find FAPI OEM records without assuming a fixed wrapper key."""
        records = []
        visited = set()

        def walk(item: Any):
            if isinstance(item, dict):
                # FAPI OEM records contain these fields.
                if all(key in item for key in ("n", "d", "ns")):
                    identity = (
                        str(item.get("n")),
                        str(item.get("ns")),
                    )

                    if identity not in visited:
                        visited.add(identity)
                        records.append(item)

                for value in item.values():
                    if isinstance(value, (dict, list)):
                        walk(value)

            elif isinstance(item, list):
                for child in item:
                    walk(child)

        walk(data)
        return records

    def parse_oem_response(self, response_data: Any) -> list[OEMPart]:
        raw_records = self._extract_oem_records(response_data)
        results = []

        for item in raw_records:
            oem_number = item.get("n")

            if oem_number is None:
                continue

            results.append(
                OEMPart(
                    oem_number=str(oem_number),
                    description=item.get("d"),
                    manufacturer_id=item.get("mfi"),
                    manufacturer_name=item.get("mfd"),
                    namespace=str(item["ns"]),
                    sources=item.get("sources"),
                    verification_status="catalog_candidate",
                )
            )

        return results

    def get_oem_parts(
        self,
        adapter,
        modification_id: int,
        part_nodes: list[dict],
    ) -> list[OEMPart]:
        if not part_nodes:
            raise CatalogMatchNotFound(
                "No matching part node was found in the catalog."
            )

        if len(part_nodes) > 1:
            raise CatalogMatchNotFound(
                "Multiple part nodes matched. "
                "A more specific part selection is required."
            )

        node_id = part_nodes[0].get("i")

        if node_id is None:
            raise CatalogMatchNotFound(
                "The matching catalog node has no ID."
            )

        response = adapter.get_oem_parts(
            modification_id=modification_id,
            node_id=node_id,
            strict=True,
        )

        return self.parse_oem_response(response)
