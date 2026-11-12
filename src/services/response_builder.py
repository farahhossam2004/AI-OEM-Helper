
from src.models.orchestration_result import OrchestrationResult


class ResponseBuilder:

    def build(
        self,
        user_text: str,
        result: OrchestrationResult,
    ) -> str:

        is_arabic = any(
            "\u0600" <= char <= "\u06FF"
            for char in user_text
        )

        if result.status == "invalid":
            return self._build_invalid_response(
                result.validation.errors,
                is_arabic,
            )

        if result.status == "needs_clarification":
            catalog_result = result.catalog_result

            if catalog_result and catalog_result.clarification_question:
                return catalog_result.clarification_question

            return self._build_clarification_response(
                result,
                is_arabic,
            )

        if result.status == "ready_for_catalog":
            if is_arabic:
                return "تم استخراج البيانات بنجاح، لكن خدمة البحث في الكتالوج غير مهيأة حاليًا."
            return "Information extracted successfully, but catalog lookup is not configured."

        catalog_result = result.catalog_result

        if catalog_result is None:
            return (
                "حدث خطأ أثناء معالجة الطلب."
                if is_arabic
                else "An error occurred while processing the request."
            )

        if result.status == "found":
            return self._build_found_response(
                catalog_result,
                is_arabic,
            )

        if result.status == "not_found":
            if is_arabic:
                return (
                    "لم يتم العثور على قطعة مطابقة في الكتالوج "
                    "لبيانات السيارة المدخلة. "
                    "قد تحتاج لتحديد تفاصيل إضافية عن السيارة."
                )
            return (
                "No matching part was found in the catalog "
                "for the provided vehicle details. "
                "Additional vehicle information may be required."
            )

        if result.status == "quota_exceeded":
            if is_arabic:
                return (
                    "خدمة الكتالوج غير متاحة حاليًا بسبب مشكلة في "
                    "حدود الاستخدام أو الاشتراك. حاول لاحقًا."
                )
            return (
                "Catalog lookup is currently unavailable due to "
                "an API quota or subscription limitation. Please try later."
            )

        if result.status == "unavailable":
            if is_arabic:
                return "خدمة الكتالوج غير متاحة حاليًا. من فضلك حاول مرة أخرى لاحقًا."
            return "The catalog service is temporarily unavailable. Please try again later."

        if is_arabic:
            return "حدث خطأ أثناء البحث في كتالوج قطع الغيار."
        return "An error occurred while searching the parts catalog."

    def _build_found_response(
        self,
        catalog_result,
        is_arabic: bool,
    ) -> str:

        lines = []

        if is_arabic:
            lines.append("تم العثور على نتائج في الكتالوج:")
            if catalog_result.selected_modification_name:
                lines.append(
                    f"تكوين السيارة: {catalog_result.selected_modification_name}"
                )
            lines.append("")
            lines.append("أرقام OEM المرشحة:")
        else:
            lines.append("Catalog results found:")
            if catalog_result.selected_modification_name:
                lines.append(
                    f"Vehicle configuration: {catalog_result.selected_modification_name}"
                )
            lines.append("")
            lines.append("OEM candidates:")

        for index, part in enumerate(catalog_result.parts, start=1):
            lines.append(f"{index}. {part.oem_number}")

            if part.description:
                lines.append(f"   Description: {part.description}")

            if part.manufacturer_name:
                lines.append(f"   Manufacturer: {part.manufacturer_name}")

            if part.sources is not None:
                lines.append(f"   Catalog sources: {part.sources}")

        if is_arabic:
            lines.append("")
            lines.append(
                "تنبيه: الأرقام المعروضة مرشحة من الكتالوج، "
                "وليست تأكيدًا نهائيًا للتوافق أو للجهة الأمامية/الخلفية. "
                "يجب التحقق من رقم الشاسيه (VIN) أو كتالوج الشركة قبل الشراء."
            )
        else:
            lines.append("")
            lines.append(
                "Note: These are catalog candidates, not final confirmation "
                "of fitment or front/rear position. Verify using the VIN or "
                "the manufacturer's catalog before purchase."
            )

        return "\n".join(lines)

    def _build_invalid_response(
        self,
        errors: list[str],
        is_arabic: bool,
    ) -> str:

        if "invalid_year" in errors:
            if is_arabic:
                return "سنة الموديل غير صحيحة. من فضلك أدخل سنة موديل صالحة."
            return "The model year is invalid. Please enter a valid year."

        if is_arabic:
            return "فيه مشكلة في البيانات المدخلة. من فضلك راجع بيانات السيارة والقطعة."

        return "There is an issue with the provided information. Please review the vehicle and part details."

    def _build_clarification_response(
        self,
        result: OrchestrationResult,
        is_arabic: bool,
    ) -> str:

        validation = result.validation

        missing_labels_ar = {
            "make": "الشركة المصنعة",
            "model": "موديل السيارة",
            "year": "سنة الموديل",
            "part_name": "اسم قطعة الغيار",
        }

        missing_labels_en = {
            "make": "vehicle make",
            "model": "vehicle model",
            "year": "model year",
            "part_name": "part name",
        }

        if is_arabic:
            questions = [
                f"ما هي {missing_labels_ar[field]}؟"
                for field in validation.missing_fields
            ]

            if "part_position_required" in validation.clarification_reasons:
                questions.append(
                    "هل تحتاج القطعة الأمامية أم الخلفية أم كليهما؟"
                )

            if (
                "llm_requested_clarification"
                in validation.clarification_reasons
                and not questions
                and validation.suggested_question
            ):
                questions.append(validation.suggested_question)

            if not questions:
                return "من فضلك وضّح بيانات السيارة وقطعة الغيار المطلوبة."

            return "محتاج منك توضيح بعض التفاصيل:\n" + "\n".join(questions)

        questions = [
            f"What is the {missing_labels_en[field]}?"
            for field in validation.missing_fields
        ]

        if "part_position_required" in validation.clarification_reasons:
            questions.append(
                "Do you need the front, rear, or both positions?"
            )

        if (
            "llm_requested_clarification"
            in validation.clarification_reasons
            and not questions
            and validation.suggested_question
        ):
            questions.append(validation.suggested_question)

        if not questions:
            return "Please clarify the vehicle and part details."

        return "I need a few more details:\n" + "\n".join(questions)
