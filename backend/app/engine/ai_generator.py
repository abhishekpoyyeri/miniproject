import json
import re
from typing import Dict, Any, List, Optional, Tuple
from backend.app.config import settings

# System prompt for GPT-4o as specified in Accura Paper (Section III-B & III-C)
SYSTEM_PROMPT = """You are DataGuard AI, an expert structural data validation assistant for enterprise migration in the InsurTech sector.
Your task is to interpret a natural-language validation requirement and convert it into a standardized, schema-constrained JSON rule.

The JSON output MUST follow this exact schema:
{
  "Rule name": "Descriptive rule name",
  "Data type": "One of: Text, Number, Document, List, Complex List, Phone, Email, Date, Dependency",
  "Required field": true or false,
  "Header": ["Target Column Name"],
  "Header rule": ["Target Column Name"] or ["Reference Column Name"] for dependencies,
  "Error message": "Clear explanation of what failed and acceptable format",
  "Description": "Business description of the validation",
  "Example": {
    "Valid example": "sample valid value",
    "Invalid example": "sample invalid value"
  },
  "Rule": { ... specific parameters based on Data type ... }
}

Parameter structures for each Data type:
1. Text:
   "Rule": { "Minimum length": 1, "Maximum length": 100 }
2. Number:
   "Rule": { "Minimum value": 0, "Maximum value": 999999.99, "Number of decimals": 2 }
3. Document:
   "Rule": { "Minimum length": 8, "Maximum length": 11 }
4. List:
   "Rule": { "List": ["VALUE1", "VALUE2", "VALUE3"] }
5. Complex List:
   "Rule": { "Complex list": [ {"Dept": "Lima", "Prov": "Lima"}, ... ] }
6. Phone:
   "Rule": { "Minimum length": 9, "Country code": "+51" }
7. Email:
   "Rule": { "Format": "email", "Maximum length": 100 }
8. Date:
   "Rule": { "Format": "yyyy-MM-dd", "Minimum date": "1900-01-01", "Maximum date": "2026-12-31" }
9. Dependency:
   "Rule": {
     "Specific rules": [
       { "Person type": "PJ", "List": { "List": ["RUC"] } },
       { "Person type": "PN", "List": { "List": ["DNI", "CE", "PAS"] } }
     ]
   }

Respond ONLY with valid, raw JSON. Do not include markdown codeblocks or extra conversational text.
"""

SUPPORTED_DATA_TYPES = [
    "Text", "Number", "Document", "List", "Complex List",
    "Phone", "Email", "Date", "Dependency"
]

class AIRuleGenerator:
    """
    GPT-4o based Natural Language Rule Generation Engine with Coherence Verification
    and Automatic Retry, as detailed in Section III-B of the Accura paper.
    """

    @classmethod
    def generate_rule(
        cls,
        instruction: str,
        selected_column: str,
        template_headers: List[str],
        suggested_data_type: Optional[str] = None,
        template_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes the rule generation workflow:
        1. Contextual prompt assembly
        2. LLM call (GPT-4o) or smart heuristic synthesizer fallback
        3. Coherence and schema compatibility check
        4. Single automatic retry if invalid
        """
        prompt = cls._build_contextual_prompt(
            instruction=instruction,
            selected_column=selected_column,
            template_headers=template_headers,
            suggested_data_type=suggested_data_type,
            template_name=template_name
        )

        attempts = 0
        max_retries = 1
        last_error = ""

        while attempts <= max_retries:
            attempts += 1
            raw_json_str = None

            # Attempt via OpenAI GPT-4o if API key is provided
            if settings.OPENAI_API_KEY:
                try:
                    import openai
                    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                    response = client.chat.completions.create(
                        model=settings.OPENAI_MODEL,
                        temperature=settings.OPENAI_TEMPERATURE,
                        max_tokens=settings.OPENAI_MAX_TOKENS,
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": prompt}
                        ]
                    )
                    raw_json_str = response.choices[0].message.content
                except Exception as e:
                    last_error = f"OpenAI API call failed: {str(e)}"
                    raw_json_str = None

            # If no API key or API call failed, use intelligent domain synthesizer
            if not raw_json_str:
                raw_json_str = cls._heuristic_rule_synthesis(
                    instruction=instruction,
                    selected_column=selected_column,
                    template_headers=template_headers,
                    suggested_data_type=suggested_data_type
                )

            # Validate coherence & schema
            is_valid, parsed_json, error_msg = cls._verify_rule_coherence(
                raw_json_str=raw_json_str,
                selected_column=selected_column,
                template_headers=template_headers
            )

            if is_valid:
                return {
                    "success": True,
                    "generated_rule": parsed_json,
                    "coherence_passed": True,
                    "retries_used": attempts - 1
                }
            else:
                last_error = error_msg
                # If retrying, append error context to prompt for second attempt
                prompt += f"\n\nPrevious attempt failed with error: {error_msg}. Please correct the JSON according to the schema."

        return {
            "success": False,
            "error": f"Rule generation failed after {attempts} attempts. Coherence check failed: {last_error}",
            "coherence_passed": False,
            "retries_used": attempts - 1
        }

    @classmethod
    def _build_contextual_prompt(
        cls,
        instruction: str,
        selected_column: str,
        template_headers: List[str],
        suggested_data_type: Optional[str] = None,
        template_name: Optional[str] = None
    ) -> str:
        return f"""
Insurance Migration Context:
Template Name: {template_name or 'InsurTech Migration Template'}
Selected Column: {selected_column}
Available Template Headers: {', '.join(template_headers)}
Supported Validation Types: {', '.join(SUPPORTED_DATA_TYPES)}
User Instruction / Requirement:
"{instruction}"

Generate the complete JSON rule for column '{selected_column}'. Ensure Header and Header rule match the template headers.
"""

    @classmethod
    def _verify_rule_coherence(
        cls,
        raw_json_str: str,
        selected_column: str,
        template_headers: List[str]
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Accura Coherence and Compatibility Verification (Section III-B & III-C):
        - Valid JSON structure
        - Required top-level keys
        - Data type belongs to supported list
        - References existing column headers
        - Specific parameters exist based on data type
        """
        try:
            # Clean markdown codeblocks if any
            clean_str = raw_json_str.strip()
            if clean_str.startswith("```json"):
                clean_str = clean_str[7:]
            if clean_str.startswith("```"):
                clean_str = clean_str[3:]
            if clean_str.endswith("```"):
                clean_str = clean_str[:-3]
            clean_str = clean_str.strip()

            rule_obj = json.loads(clean_str)
        except Exception as e:
            return False, None, f"JSON parse error: {str(e)}"

        if not isinstance(rule_obj, dict):
            return False, None, "Rule must be a JSON object"

        # Check required fields
        required_keys = ["Rule name", "Data type", "Header", "Error message", "Description", "Rule"]
        for key in required_keys:
            if key not in rule_obj:
                return False, None, f"Missing required top-level key '{key}'"

        # Check Data type
        data_type = rule_obj.get("Data type")
        matched_dtype = None
        for dt in SUPPORTED_DATA_TYPES:
            if dt.lower() == str(data_type).lower():
                matched_dtype = dt
                break

        if not matched_dtype:
            return False, None, f"Data type '{data_type}' is not supported. Must be one of {SUPPORTED_DATA_TYPES}"
        rule_obj["Data type"] = matched_dtype

        # Check Header references existing columns
        headers = rule_obj.get("Header", [])
        if isinstance(headers, str):
            headers = [headers]
            rule_obj["Header"] = headers

        clean_temp_headers = [h.strip().upper() for h in template_headers]
        for h in headers:
            if h.strip().upper() not in clean_temp_headers:
                return False, None, f"Header '{h}' does not exist in template headers."

        # Verify type-specific parameters
        params = rule_obj.get("Rule", {})
        if not isinstance(params, dict):
            return False, None, "'Rule' parameters must be a JSON object"

        if matched_dtype == "List":
            if "List" not in params or not isinstance(params["List"], list) or len(params["List"]) == 0:
                return False, None, "List rule must define 'List' array with accepted values."

        elif matched_dtype == "Number":
            if "Minimum value" not in params and "Maximum value" not in params and "Number of decimals" not in params:
                return False, None, "Number rule must define at least one constraint (Minimum value, Maximum value, or Number of decimals)."

        elif matched_dtype == "Text" or matched_dtype == "Document":
            if "Minimum length" not in params and "Maximum length" not in params:
                return False, None, f"{matched_dtype} rule must define Minimum length or Maximum length."

        elif matched_dtype == "Dependency":
            if "Specific rules" not in params or not isinstance(params["Specific rules"], list):
                return False, None, "Dependency rule must specify 'Specific rules' array."

        return True, rule_obj, None

    @classmethod
    def _heuristic_rule_synthesis(
        cls,
        instruction: str,
        selected_column: str,
        template_headers: List[str],
        suggested_data_type: Optional[str] = None
    ) -> str:
        """
        Intelligent offline heuristic synthesizer that interprets requirements
        following the prompt patterns in Section III-B, guaranteeing reliable operation
        even without an active OpenAI API key.
        """
        inst_lower = instruction.lower()

        # Detect data type using word boundary matching to avoid substrings like 'date' in 'validate'
        data_type = suggested_data_type or "Text"
        if re.search(r'\b(dependency|depends|conditional|when)\b', inst_lower):
            data_type = "Dependency"
        elif re.search(r'\b(document|dni|ruc|passport|ce)\b', inst_lower):
            data_type = "Document"
        elif re.search(r'\b(list|allowed values|one of)\b', inst_lower):
            data_type = "List"
        elif re.search(r'\b(email)\b', inst_lower) or "@" in inst_lower:
            data_type = "Email"
        elif re.search(r'\b(phone|mobile|celular|telefono|country code)\b', inst_lower):
            data_type = "Phone"
        elif re.search(r'\b(date|fecha)\b', inst_lower):
            data_type = "Date"
        elif re.search(r'\b(number|decimal|amount|monto|range|numeric|prima|tax|igv)\b', inst_lower):
            data_type = "Number"

        # Detect mandatory / required
        is_required = True if ("required" in inst_lower or "mandatory" in inst_lower or "obligatorio" in inst_lower) else False

        # Build specific parameters
        rule_params: Dict[str, Any] = {}
        example_valid = "SampleValue"
        example_invalid = "BadValue"
        err_msg = f"The field '{selected_column}' is invalid."

        if data_type == "List":
            # Extract list values: quotes or brackets
            found_items = re.findall(r"['\"]([^'\"]+)['\"]", instruction)
            if not found_items:
                # Try finding after colon or in comma separated words
                sub = instruction
                if "allowed:" in inst_lower:
                    sub = instruction.split("allowed:")[1]
                elif "must be" in inst_lower:
                    sub = instruction.split("must be")[1]
                found_items = [w.strip(" .,") for w in sub.split(",") if w.strip()]

            if not found_items:
                found_items = ["ACTIVO", "INACTIVO"]

            rule_params["List"] = found_items
            example_valid = found_items[0]
            example_invalid = "INVALID_CHOICE"
            err_msg = f"The {selected_column} must be one of: {', '.join(found_items)}."

        elif data_type == "Number":
            # Look for min/max
            min_match = re.search(r"(?:min|minimum|greater than|at least)\s*(?:value)?\s*(?:is|=|:)?\s*(-?\d+\.?\d*)", inst_lower)
            max_match = re.search(r"(?:max|maximum|less than|up to)\s*(?:value)?\s*(?:is|=|:)?\s*(-?\d+\.?\d*)", inst_lower)
            dec_match = re.search(r"(\d+)\s*decimals?", inst_lower)

            min_val = float(min_match.group(1)) if min_match else 0.0
            max_val = float(max_match.group(1)) if max_match else 999999.99
            decimals = int(dec_match.group(1)) if dec_match else 2

            rule_params["Minimum value"] = min_val
            rule_params["Maximum value"] = max_val
            rule_params["Number of decimals"] = decimals
            example_valid = round((min_val + max_val) / 2, decimals)
            example_invalid = max_val + 100
            err_msg = f"The {selected_column} must be between {min_val} and {max_val} with {decimals} decimals."

        elif data_type == "Document":
            min_len = 8
            max_len = 11
            # Check patterns like: 'minimum length 8', 'between 8 and 11', '8 digits', etc.
            between_match = re.search(r"between\s+(\d+)\s+and\s+(\d+)", inst_lower)
            if between_match:
                min_len = int(between_match.group(1))
                max_len = int(between_match.group(2))
            else:
                min_match = re.search(r"(?:min|minimum|at least)(?:\s+length)?\s+(\d+)", inst_lower)
                max_match = re.search(r"(?:max|maximum|up to)(?:\s+length)?\s+(\d+)", inst_lower)
                if min_match:
                    min_len = int(min_match.group(1))
                if max_match:
                    max_len = int(max_match.group(1))

            rule_params["Minimum length"] = min_len
            rule_params["Maximum length"] = max_len
            example_valid = "12345678" if min_len == 8 else "20123456789"
            example_invalid = "123"
            err_msg = f"Document number must have between {min_len} and {max_len} characters."

        elif data_type == "Email":
            rule_params["Format"] = "email"
            rule_params["Maximum length"] = 100
            example_valid = "user@domain.com"
            example_invalid = "not-an-email"
            err_msg = f"The {selected_column} must be a valid email address not exceeding 100 characters."

        elif data_type == "Phone":
            rule_params["Minimum length"] = 9
            rule_params["Country code"] = "+51" if ("+51" in instruction or "peru" in inst_lower) else ""
            example_valid = "+51987654321" if rule_params["Country code"] else "987654321"
            example_invalid = "123"
            err_msg = f"The {selected_column} must be a valid phone number with minimum length 9."

        elif data_type == "Date":
            rule_params["Format"] = "yyyy-MM-dd"
            rule_params["Minimum date"] = "1900-01-01"
            rule_params["Maximum date"] = "2026-12-31"
            example_valid = "2024-05-15"
            example_invalid = "2030-01-01"
            err_msg = f"The {selected_column} must be a valid date between 1900-01-01 and 2026-12-31 (yyyy-MM-dd)."

        elif data_type == "Dependency":
            # Dependency between Person type and Document type or similar
            rule_params["Specific rules"] = [
                {
                    "Person type": "PJ",
                    "List": { "List": ["RUC"] }
                },
                {
                    "Person type": "PN",
                    "List": { "List": ["DNI", "CE", "PAS"] }
                }
            ]
            example_valid = "RUC"
            example_invalid = "DNI (when PJ)"
            err_msg = f"Conditional validation violated for {selected_column} based on related field value."

        else:  # Text
            rule_params["Minimum length"] = 1
            rule_params["Maximum length"] = 100
            example_valid = "Valid Text"
            example_invalid = ""
            err_msg = f"Text length must be between 1 and 100 characters."

        rule_dict = {
            "Rule name": f"Validation rule for {selected_column}",
            "Data type": data_type,
            "Required field": is_required,
            "Header": [selected_column],
            "Header rule": [selected_column],
            "Error message": err_msg,
            "Description": f"Validates {selected_column} according to business migration rules.",
            "Example": {
                "Valid example": example_valid,
                "Invalid example": example_invalid
            },
            "Rule": rule_params
        }

        return json.dumps(rule_dict, indent=2)
