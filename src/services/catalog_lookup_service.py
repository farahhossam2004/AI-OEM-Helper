
from src.integrations.fapi_adapter import (
    FAPIAdapter,
    FAPIAuthenticationError,
    FAPIQuotaError,
    FAPIRequestError,
    FAPIUnavailableError,
)
from src.models.catalog_lookup_result import CatalogLookupResult
from src.services.catalog_service import (
    CatalogMatchNotFound,
    CatalogService,
)
from src.services.modification_service import ModificationService


class CatalogLookupService:

    def __init__(
        self,
        adapter: FAPIAdapter,
        catalog_service: CatalogService | None = None,
        modification_service: ModificationService | None = None,
    ):
        self.adapter = adapter
        self.catalog_service = catalog_service or CatalogService()
        self.modification_service = (
            modification_service or ModificationService()
        )

    def lookup(self, request) -> CatalogLookupResult:
        try:
            # 1. Find vehicle manufacturer.
            manufacturers_data = self.adapter.get_manufacturers()

            manufacturer = self.catalog_service.find_manufacturer(
                manufacturers_data,
                request.make,
            )

            manufacturer_id = manufacturer.get("dbi")

            if manufacturer_id is None:
                raise CatalogMatchNotFound(
                    "Manufacturer record has no database ID."
                )

            # 2. Find vehicle model.
            models_data = self.adapter.get_models(
                manufacturer_id=manufacturer_id
            )

            models = self.catalog_service.find_models(
                models_data,
                request.model,
                request.year,
            )

            if not models:
                return CatalogLookupResult(
                    status="not_found",
                    details="No vehicle model matched the requested name and year.",
                )

            if len(models) > 1:
                options = [
                    item.get("fd") or item.get("d", "Unknown")
                    for item in models
                ]

                return CatalogLookupResult(
                    status="needs_clarification",
                    clarification_question=(
                        "More than one vehicle model matches. "
                        "Please specify the generation: "
                        + "; ".join(options)
                    ),
                )

            model_id = models[0].get("dbi") or models[0].get("i")

            if model_id is None:
                raise CatalogMatchNotFound(
                    "Vehicle model record has no database ID."
                )

            # 3. Resolve vehicle modification for the requested year.
            modifications_data = self.adapter.get_modifications(
                model_id=model_id
            )

            resolution = self.modification_service.resolve(
                modifications_data,
                request.year,
            )

            if resolution.status == "not_found":
                return CatalogLookupResult(
                    status="not_found",
                    details="No vehicle modification covers the requested year.",
                )

            if resolution.status == "needs_clarification":
                options = [
                    item.full_name or item.name
                    for item in resolution.modifications
                ]

                return CatalogLookupResult(
                    status="needs_clarification",
                    clarification_question=(
                        "More than one engine or drivetrain configuration "
                        "matches. Please specify which one applies: "
                        + "; ".join(options)
                    ),
                )

            modification = resolution.selected_modification

            if modification is None:
                raise CatalogMatchNotFound(
                    "Could not resolve a vehicle modification."
                )

            # 4. Find the requested part in the catalog tree.
            tree_data = self.adapter.get_parts_tree(
                modification_id=modification.modification_id
            )

            part_nodes = self.catalog_service.find_part_nodes(
                tree_data,
                request.part_name,
            )

            if not part_nodes:
                return CatalogLookupResult(
                    status="not_found",
                    details="The requested part was not found in this vehicle catalog.",
                    selected_modification_id=modification.modification_id,
                    selected_modification_name=modification.full_name,
                )

            if len(part_nodes) > 1:
                return CatalogLookupResult(
                    status="needs_clarification",
                    clarification_question=(
                        "Multiple catalog sections match this part. "
                        "Please provide more details about the requested part."
                    ),
                )

            # 5. Retrieve OEM records.
            parts = self.catalog_service.get_oem_parts(
                adapter=self.adapter,
                modification_id=modification.modification_id,
                part_nodes=part_nodes,
            )

            if not parts:
                return CatalogLookupResult(
                    status="not_found",
                    details="No OEM records were returned for this catalog part.",
                    selected_modification_id=modification.modification_id,
                    selected_modification_name=modification.full_name,
                )

            return CatalogLookupResult(
                status="found",
                parts=parts,
                selected_modification_id=modification.modification_id,
                selected_modification_name=modification.full_name,
            )

        except FAPIQuotaError:
            return CatalogLookupResult(
                status="quota_exceeded",
                details="FAPI account quota or plan does not allow this request.",
            )

        except FAPIUnavailableError:
            return CatalogLookupResult(
                status="unavailable",
                details="FAPI is temporarily unavailable.",
            )

        except FAPIAuthenticationError:
            return CatalogLookupResult(
                status="error",
                details="FAPI authentication or permission failed.",
            )

        except FAPIRequestError as exc:
            return CatalogLookupResult(
                status="error",
                details=str(exc),
            )

        except CatalogMatchNotFound as exc:
            return CatalogLookupResult(
                status="not_found",
                details=str(exc),
            )
