from backend.app.engine.ai_generator import AIRuleGenerator

def test_ai_rule_generation_and_coherence():
    instruction = "Validate that the field 'Numero_Documento' is of type Document and has minimum length 8 and maximum length 11 digits; otherwise display: 'Document length invalid'. Valid example: 45678912, Invalid example: 123"
    
    result = AIRuleGenerator.generate_rule(
        instruction=instruction,
        selected_column="Numero_Documento",
        template_headers=["Numero_Documento", "Tipo_Documento", "Nombre_Cliente"],
        suggested_data_type="Document"
    )

    assert result["success"] == True
    assert result["coherence_passed"] == True
    assert "generated_rule" in result

    rule_json = result["generated_rule"]
    assert rule_json["Data type"] == "Document"
    assert "Numero_Documento" in rule_json["Header"]
    assert "Minimum length" in rule_json["Rule"]
    assert rule_json["Rule"]["Minimum length"] == 8
    assert rule_json["Rule"]["Maximum length"] == 11

def test_ai_rule_generation_list():
    instruction = "Validate that the field 'Moneda' is of type List with allowed values: 'USD', 'PEN'; otherwise display: 'Currency not allowed'."
    result = AIRuleGenerator.generate_rule(
        instruction=instruction,
        selected_column="Moneda",
        template_headers=["Moneda", "Prima_Total"],
        suggested_data_type="List"
    )
    assert result["success"] == True
    rule_json = result["generated_rule"]
    assert rule_json["Data type"] == "List"
    assert "USD" in rule_json["Rule"]["List"]
    assert "PEN" in rule_json["Rule"]["List"]

