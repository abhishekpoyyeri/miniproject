import os
from backend.app.database import SessionLocal
from backend.app.models.template import Template
from backend.app.models.user import User
from backend.app.engine.validator import DatasetValidator

def test_validate_valid_dataset():
    db = SessionLocal()
    try:
        t = db.query(Template).filter(Template.name == "Plantilla_polizas").first()
        u = db.query(User).filter(User.email == "client@inventiva.com").first()
        assert t is not None
        assert u is not None

        sample_path = os.path.join(os.path.dirname(__file__), "..", "backend", "sample_data", "Plantilla_polizas_valid.xlsx")
        assert os.path.exists(sample_path)

        res = DatasetValidator.process_and_validate(
            db=db,
            template_id=t.id,
            user_id=u.id,
            file_path=sample_path,
            filename="Plantilla_polizas_valid.xlsx"
        )

        assert res["status"] == "Completed"
        assert res["total_rows"] == 5
        assert res["valid_rows"] == 5
        assert res["error_rows"] == 0
        assert res["accuracy_percentage"] == 100.0
        assert len(res["errors"]) == 0
    finally:
        db.close()

def test_validate_inconsistent_dataset():
    db = SessionLocal()
    try:
        t = db.query(Template).filter(Template.name == "Plantilla_polizas").first()
        u = db.query(User).filter(User.email == "client@inventiva.com").first()

        sample_path = os.path.join(os.path.dirname(__file__), "..", "backend", "sample_data", "Plantilla_polizas_with_errors.xlsx")
        assert os.path.exists(sample_path)

        res = DatasetValidator.process_and_validate(
            db=db,
            template_id=t.id,
            user_id=u.id,
            file_path=sample_path,
            filename="Plantilla_polizas_with_errors.xlsx"
        )

        assert res["status"] == "Rejected"
        assert res["total_rows"] == 5
        assert res["error_rows"] > 0
        assert len(res["errors"]) > 0

        # Check detected error rules
        violated_rules = [e["violated_rule_name"] for e in res["errors"]]
        assert any("Document" in r for r in violated_rules)
        assert any("Policy Status" in r for r in violated_rules)
    finally:
        db.close()

def test_validate_dependency_inconsistencies():
    db = SessionLocal()
    try:
        t = db.query(Template).filter(Template.name == "Plantilla_clientes").first()
        u = db.query(User).filter(User.email == "client@inventiva.com").first()

        sample_path = os.path.join(os.path.dirname(__file__), "..", "backend", "sample_data", "Plantilla_clientes_with_errors.xlsx")
        assert os.path.exists(sample_path)

        res = DatasetValidator.process_and_validate(
            db=db,
            template_id=t.id,
            user_id=u.id,
            file_path=sample_path,
            filename="Plantilla_clientes_with_errors.xlsx"
        )

        assert res["status"] == "Rejected"
        violated_rules = [e["violated_rule_name"] for e in res["errors"]]
        # Must detect person type to document type dependency violation!
        assert any("Dependency" in r for r in violated_rules)
    finally:
        db.close()

