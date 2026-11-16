from backend.app.engine.rule_evaluator import RuleEvaluator

def test_text_rule():
    rule = {
        "Data type": "Text",
        "Required field": True,
        "Rule": {"Minimum length": 3, "Maximum length": 10}
    }
    # Valid
    assert RuleEvaluator.evaluate(rule, {"col": "Hello"}, "col").is_valid == True
    # Too short
    assert RuleEvaluator.evaluate(rule, {"col": "Hi"}, "col").is_valid == False
    # Too long
    assert RuleEvaluator.evaluate(rule, {"col": "Supercalifragilistic"}, "col").is_valid == False

def test_number_rule():
    rule = {
        "Data type": "Number",
        "Required field": True,
        "Rule": {"Minimum value": 10.0, "Maximum value": 500.0, "Number of decimals": 2}
    }
    # Valid
    assert RuleEvaluator.evaluate(rule, {"col": 150.50}, "col").is_valid == True
    # Below min
    assert RuleEvaluator.evaluate(rule, {"col": 5.0}, "col").is_valid == False
    # Above max
    assert RuleEvaluator.evaluate(rule, {"col": 1000.0}, "col").is_valid == False

def test_document_rule():
    rule_dni = {
        "Data type": "Document",
        "Required field": True,
        "Rule": {"Minimum length": 8, "Maximum length": 8}
    }
    # 8 digits DNI valid
    assert RuleEvaluator.evaluate(rule_dni, {"col": "45678912"}, "col").is_valid == True
    # Invalid length
    assert RuleEvaluator.evaluate(rule_dni, {"col": "123"}, "col").is_valid == False

def test_list_rule():
    rule_list = {
        "Data type": "List",
        "Required field": True,
        "Rule": {"List": ["EMITIDA", "VIGENTE", "CANCELADA"]}
    }
    # Valid
    assert RuleEvaluator.evaluate(rule_list, {"col": "VIGENTE"}, "col").is_valid == True
    # Invalid
    assert RuleEvaluator.evaluate(rule_list, {"col": "PENDING"}, "col").is_valid == False

def test_email_rule():
    rule_email = {
        "Data type": "Email",
        "Required field": True,
        "Rule": {"Format": "email", "Maximum length": 50}
    }
    assert RuleEvaluator.evaluate(rule_email, {"col": "user@example.com"}, "col").is_valid == True
    assert RuleEvaluator.evaluate(rule_email, {"col": "invalid_email_string"}, "col").is_valid == False

def test_phone_rule():
    rule_phone = {
        "Data type": "Phone",
        "Required field": True,
        "Rule": {"Minimum length": 9, "Country code": "+51"}
    }
    assert RuleEvaluator.evaluate(rule_phone, {"col": "+51987654321"}, "col").is_valid == True
    assert RuleEvaluator.evaluate(rule_phone, {"col": "987654321"}, "col").is_valid == False

def test_date_rule():
    rule_date = {
        "Data type": "Date",
        "Required field": True,
        "Rule": {"Format": "yyyy-MM-dd", "Minimum date": "2020-01-01", "Maximum date": "2026-12-31"}
    }
    assert RuleEvaluator.evaluate(rule_date, {"col": "2024-05-15"}, "col").is_valid == True
    # Out of range date
    assert RuleEvaluator.evaluate(rule_date, {"col": "2030-01-01"}, "col").is_valid == False

def test_dependency_rule():
    rule_dep = {
        "Data type": "Dependency",
        "Required field": True,
        "Rule": {
            "Specific rules": [
                {
                    "Tipo_Persona": "PJ",
                    "List": {"List": ["RUC"]}
                },
                {
                    "Tipo_Persona": "PN",
                    "List": {"List": ["DNI", "CE", "PAS"]}
                }
            ]
        }
    }
    # Juridical person with RUC -> Valid
    assert RuleEvaluator.evaluate(rule_dep, {"Tipo_Persona": "PJ", "Tipo_Documento": "RUC"}, "Tipo_Documento").is_valid == True
    # Juridical person with DNI -> Invalid
    assert RuleEvaluator.evaluate(rule_dep, {"Tipo_Persona": "PJ", "Tipo_Documento": "DNI"}, "Tipo_Documento").is_valid == False
    # Natural person with DNI -> Valid
    assert RuleEvaluator.evaluate(rule_dep, {"Tipo_Persona": "PN", "Tipo_Documento": "DNI"}, "Tipo_Documento").is_valid == True
