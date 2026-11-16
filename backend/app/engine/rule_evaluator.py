import re
import math
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

class RuleEvaluationResult:
    def __init__(self, is_valid: bool, error_message: Optional[str] = None, severity: str = "Error"):
        self.is_valid = is_valid
        self.error_message = error_message
        self.severity = severity

class RuleEvaluator:
    """
    Deterministic rule evaluation engine implementing the 9 rule categories
    defined in Section III-C of the Accura base paper:
    1. Text
    2. Number
    3. Document
    4. List
    5. Complex List
    6. Phone
    7. Email
    8. Date
    9. Dependency
    """

    @classmethod
    def evaluate(cls, rule_data: Dict[str, Any], row_data: Dict[str, Any], column_name: str) -> RuleEvaluationResult:
        """
        Evaluates a single rule on a row or specific field value.
        """
        data_type = rule_data.get("Data type") or rule_data.get("data_type") or ""
        required_field = rule_data.get("Required field", False)
        default_error_msg = rule_data.get("Error message") or f"Invalid value for column '{column_name}'"
        params = rule_data.get("Rule", {})

        value = row_data.get(column_name)

        # Check required field
        is_empty = value is None or (isinstance(value, str) and value.strip() == "") or (isinstance(value, float) and math.isnan(value))
        if is_empty:
            if required_field:
                return RuleEvaluationResult(
                    is_valid=False,
                    error_message=f"Mandatory field '{column_name}' is empty or missing.",
                    severity="Error"
                )
            # If not required and empty, it passes validation
            return RuleEvaluationResult(is_valid=True)

        str_val = str(value).strip()

        # Normalize data_type name
        dtype_lower = data_type.lower().strip()

        if dtype_lower == "text":
            return cls._validate_text(str_val, params, default_error_msg)
        elif dtype_lower == "number":
            return cls._validate_number(value, str_val, params, default_error_msg)
        elif dtype_lower == "document":
            return cls._validate_document(str_val, params, default_error_msg)
        elif dtype_lower == "list":
            return cls._validate_list(str_val, params, default_error_msg)
        elif dtype_lower == "complex list":
            return cls._validate_complex_list(row_data, params, default_error_msg)
        elif dtype_lower == "phone":
            return cls._validate_phone(str_val, params, default_error_msg)
        elif dtype_lower == "email":
            return cls._validate_email(str_val, params, default_error_msg)
        elif dtype_lower == "date":
            return cls._validate_date(value, str_val, params, default_error_msg)
        elif dtype_lower == "dependency":
            return cls._validate_dependency(row_data, column_name, params, default_error_msg)
        else:
            # Fallback text validation if unspecified
            return RuleEvaluationResult(is_valid=True)

    @classmethod
    def _validate_text(cls, val: str, params: Dict[str, Any], default_msg: str) -> RuleEvaluationResult:
        min_len = params.get("Minimum length")
        max_len = params.get("Maximum length")

        length = len(val)
        if min_len is not None and length < int(min_len):
            return RuleEvaluationResult(False, default_msg or f"Text length ({length}) is below minimum allowed ({min_len}).")
        if max_len is not None and length > int(max_len):
            return RuleEvaluationResult(False, default_msg or f"Text length ({length}) exceeds maximum allowed ({max_len}).")

        return RuleEvaluationResult(True)

    @classmethod
    def _validate_number(cls, raw_val: Any, str_val: str, params: Dict[str, Any], default_msg: str) -> RuleEvaluationResult:
        try:
            # Clean possible currency / commas
            cleaned = str_val.replace(",", "").replace("$", "").replace("S/.", "").strip()
            num = float(cleaned)
        except (ValueError, TypeError):
            return RuleEvaluationResult(False, default_msg or f"Value '{str_val}' is not a valid number.")

        min_val = params.get("Minimum value")
        max_val = params.get("Maximum value")
        decimals = params.get("Number of decimals")

        if min_val is not None and num < float(min_val):
            return RuleEvaluationResult(False, default_msg or f"Value {num} is below minimum allowed {min_val}.")
        if max_val is not None and num > float(max_val):
            return RuleEvaluationResult(False, default_msg or f"Value {num} exceeds maximum allowed {max_val}.")

        if decimals is not None:
            # Check decimal precision
            if "." in cleaned:
                dec_part = cleaned.split(".")[1]
                # Strip trailing zeroes if float representation added them
                if len(dec_part) > int(decimals):
                    return RuleEvaluationResult(False, default_msg or f"Number has more than {decimals} decimal places.")

        return RuleEvaluationResult(True)

    @classmethod
    def _validate_document(cls, val: str, params: Dict[str, Any], default_msg: str) -> RuleEvaluationResult:
        min_len = params.get("Minimum length")
        max_len = params.get("Maximum length")
        val_clean = re.sub(r'[\s\-_]', '', val)
        length = len(val_clean)

        if min_len is not None and length < int(min_len):
            return RuleEvaluationResult(False, default_msg or f"Document length ({length}) is shorter than {min_len} characters.")
        if max_len is not None and length > int(max_len):
            return RuleEvaluationResult(False, default_msg or f"Document length ({length}) exceeds {max_len} characters.")

        return RuleEvaluationResult(True)

    @classmethod
    def _validate_list(cls, val: str, params: Dict[str, Any], default_msg: str) -> RuleEvaluationResult:
        allowed = params.get("List", [])
        if not allowed:
            return RuleEvaluationResult(True)

        allowed_str = [str(item).strip().upper() for item in allowed]
        if val.strip().upper() not in allowed_str:
            return RuleEvaluationResult(
                False,
                default_msg or f"Value '{val}' does not belong to allowed values: {', '.join(map(str, allowed))}."
            )

        return RuleEvaluationResult(True)

    @classmethod
    def _validate_complex_list(cls, row_data: Dict[str, Any], params: Dict[str, Any], default_msg: str) -> RuleEvaluationResult:
        complex_list = params.get("Complex list", [])
        if not complex_list or not isinstance(complex_list, list):
            return RuleEvaluationResult(True)

        # Check if row attributes match at least one allowed combination
        for combo in complex_list:
            if not isinstance(combo, dict):
                continue
            matched = True
            for col_key, expected_val in combo.items():
                row_val = str(row_data.get(col_key, "")).strip().upper()
                if row_val != str(expected_val).strip().upper():
                    matched = False
                    break
            if matched:
                return RuleEvaluationResult(True)

        return RuleEvaluationResult(
            False,
            default_msg or "Combination of multi-attribute values does not match any valid entry in the complex list."
        )

    @classmethod
    def _validate_phone(cls, val: str, params: Dict[str, Any], default_msg: str) -> RuleEvaluationResult:
        min_len = params.get("Minimum length", 9)
        country_code = params.get("Country code")

        clean_phone = re.sub(r'[^\d+]', '', val)
        if country_code and not clean_phone.startswith(country_code):
            return RuleEvaluationResult(
                False,
                default_msg or f"Phone number must start with country code {country_code}."
            )

        # Check digit length without country code if country code was present
        digits_only = re.sub(r'\D', '', clean_phone)
        if len(digits_only) < int(min_len):
            return RuleEvaluationResult(
                False,
                default_msg or f"Phone number has fewer than {min_len} digits."
            )

        return RuleEvaluationResult(True)

    @classmethod
    def _validate_email(cls, val: str, params: Dict[str, Any], default_msg: str) -> RuleEvaluationResult:
        max_len = params.get("Maximum length", 100)
        if len(val) > int(max_len):
            return RuleEvaluationResult(False, default_msg or f"Email length exceeds {max_len} characters.")

        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, val):
            return RuleEvaluationResult(False, default_msg or f"Value '{val}' is not a valid email address.")

        return RuleEvaluationResult(True)

    @classmethod
    def _validate_date(cls, raw_val: Any, str_val: str, params: Dict[str, Any], default_msg: str) -> RuleEvaluationResult:
        date_format = params.get("Format", "yyyy-MM-dd")
        min_date_str = params.get("Minimum date")
        max_date_str = params.get("Maximum date")

        # Convert Java/C# format string to python strftime/strptime
        py_format = date_format.replace("yyyy", "%Y").replace("MM", "%m").replace("dd", "%d")

        parsed_date = None
        if isinstance(raw_val, datetime):
            parsed_date = raw_val
        else:
            # Try to parse with specified format
            try:
                parsed_date = datetime.strptime(str_val.split("T")[0].split(" ")[0], py_format)
            except Exception:
                # Common format attempts
                for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d", "%d-%m-%Y"]:
                    try:
                        parsed_date = datetime.strptime(str_val.split("T")[0].split(" ")[0], fmt)
                        break
                    except Exception:
                        pass

        if not parsed_date:
            return RuleEvaluationResult(
                False,
                default_msg or f"Date '{str_val}' does not match expected format ({date_format})."
            )

        # Min date check
        if min_date_str:
            try:
                min_dt = datetime.strptime(min_date_str, "%Y-%m-%d")
                if parsed_date < min_dt:
                    return RuleEvaluationResult(
                        False,
                        default_msg or f"Date {parsed_date.strftime('%Y-%m-%d')} is before minimum allowed {min_date_str}."
                    )
            except Exception:
                pass

        # Max date check
        if max_date_str:
            try:
                max_dt = datetime.strptime(max_date_str, "%Y-%m-%d")
                if parsed_date > max_dt:
                    return RuleEvaluationResult(
                        False,
                        default_msg or f"Date {parsed_date.strftime('%Y-%m-%d')} is after maximum allowed {max_date_str}."
                    )
            except Exception:
                pass

        return RuleEvaluationResult(True)

    @classmethod
    def _validate_dependency(cls, row_data: Dict[str, Any], target_column: str, params: Dict[str, Any], default_msg: str) -> RuleEvaluationResult:
        """
        Validates conditional dependency between columns.
        Supports:
        "Specific rules": [
           {
              "Person type": "PJ",
              "List": { "List": ["RUC"] }
           },
           {
              "Person type": "PN",
              "List": { "List": ["DNI", "CE", "PAS"] }
           }
        ]
        """
        specific_rules = params.get("Specific rules", [])
        if not specific_rules:
            return RuleEvaluationResult(True)

        target_val = str(row_data.get(target_column, "")).strip()

        for spec in specific_rules:
            # Find the controlling condition key (any key other than 'List', 'Rule', etc.)
            condition_col = None
            expected_condition_val = None
            for k, v in spec.items():
                if k not in ["List", "Rule", "Condition"]:
                    condition_col = k
                    expected_condition_val = str(v).strip().upper()
                    break

            if not condition_col:
                continue

            row_condition_val = str(row_data.get(condition_col, "")).strip().upper()

            # If the row matches this condition, check the target value constraint
            if row_condition_val == expected_condition_val:
                # Sub-rule check
                sub_list = spec.get("List", {}).get("List", [])
                if sub_list:
                    allowed_items = [str(x).strip().upper() for x in sub_list]
                    if target_val.upper() not in allowed_items:
                        return RuleEvaluationResult(
                            False,
                            default_msg or f"When {condition_col} is '{row_condition_val}', {target_column} must be one of {allowed_items}, but was '{target_val}'."
                        )

        return RuleEvaluationResult(True)

