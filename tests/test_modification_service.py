
from src.services.modification_service import ModificationService


def test_multiple_modifications_require_clarification():
    service = ModificationService()

    fake_response = {
        "m": [
            {
                "dbi": 159441,
                "d": "2.5 Hybrid",
                "fd": "2.5 Hybrid A25A-FXS",
                "cb": 1704063600000,
                "ce": None,
                "p": {"p": ["2.5l", "A25A-FXS"]},
            },
            {
                "dbi": 159975,
                "d": "2.0 Petrol",
                "fd": "2.0 Petrol M20A-FKS",
                "cb": 1727730000000,
                "ce": None,
                "p": {"p": ["2.0l", "M20A-FKS"]},
            },
        ]
    }

    result = service.resolve(fake_response, 2026)

    assert result.status == "needs_clarification"
    assert len(result.modifications) == 2
    assert result.selected_modification is None


def test_single_modification_is_resolved():
    service = ModificationService()

    fake_response = {
        "m": [
            {
                "dbi": 159975,
                "d": "2.0 Petrol",
                "fd": "2.0 Petrol M20A-FKS",
                "cb": 1727730000000,
                "ce": None,
                "p": {"p": ["2.0l", "M20A-FKS"]},
            }
        ]
    }

    result = service.resolve(fake_response, 2026)

    assert result.status == "resolved"
    assert result.selected_modification.modification_id == 159975


def test_no_modification_for_year():
    service = ModificationService()

    result = service.resolve({"m": []}, 2026)

    assert result.status == "not_found"
