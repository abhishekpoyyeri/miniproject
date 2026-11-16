import json
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.template import Rule, TemplateColumn, TemplateColumnRule
from backend.app.models.user import User
from backend.app.models.audit import AuditLog
from backend.app.schemas.rule import (
    RuleCreate, RuleUpdate, RuleResponse, RuleGenerateRequest, RuleGenerateResponse
)
from backend.app.engine.ai_generator import AIRuleGenerator
from backend.app.engine.rule_evaluator import RuleEvaluator
from backend.app.routers.auth import get_current_user

router = APIRouter(prefix="/rules", tags=["Validation Rules"])

@router.get("", response_model=List[RuleResponse])
def get_rules(data_type: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Rule).filter(Rule.deleted == False)
    if data_type:
        query = query.filter(Rule.data_type == data_type)
    rules = query.order_by(Rule.id.desc()).all()

    results = []
    for r in rules:
        try:
            parsed = json.loads(r.json_rule) if isinstance(r.json_rule, str) else r.json_rule
        except Exception:
            parsed = {}
        results.append(RuleResponse(
            id=r.id,
            name=r.name,
            data_type=r.data_type,
            json_rule=parsed,
            effectiveness=r.effectiveness,
            prompt_used=r.prompt_used,
            is_active=r.is_active
        ))
    return results

@router.get("/{rule_id}", response_model=RuleResponse)
def get_rule(rule_id: int, db: Session = Depends(get_db)):
    r = db.query(Rule).filter(Rule.id == rule_id, Rule.deleted == False).first()
    if not r:
        raise HTTPException(status_code=404, detail="Rule not found")
    try:
        parsed = json.loads(r.json_rule) if isinstance(r.json_rule, str) else r.json_rule
    except Exception:
        parsed = {}
    return RuleResponse(
        id=r.id,
        name=r.name,
        data_type=r.data_type,
        json_rule=parsed,
        effectiveness=r.effectiveness,
        prompt_used=r.prompt_used,
        is_active=r.is_active
    )

@router.post("", response_model=RuleResponse)
def create_rule(
    rule_in: RuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    json_str = json.dumps(rule_in.json_rule) if isinstance(rule_in.json_rule, dict) else str(rule_in.json_rule)
    new_rule = Rule(
        name=rule_in.name,
        data_type=rule_in.data_type,
        json_rule=json_str,
        prompt_used=rule_in.prompt_used,
        effectiveness=100.0,
        is_active=True,
        created_by=current_user.name
    )
    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)

    # Optional immediate assignment to column
    if rule_in.column_id:
        col = db.query(TemplateColumn).filter(TemplateColumn.id == rule_in.column_id).first()
        if col:
            tcr = TemplateColumnRule(template_column_id=col.id, rule_id=new_rule.id)
            db.add(tcr)
            db.commit()

    # Audit log
    audit = AuditLog(
        operation="CREATE_RULE",
        details=f"Rule '{new_rule.name}' ({new_rule.data_type}) created",
        created_by=current_user.name
    )
    db.add(audit)
    db.commit()

    return RuleResponse(
        id=new_rule.id,
        name=new_rule.name,
        data_type=new_rule.data_type,
        json_rule=rule_in.json_rule,
        effectiveness=new_rule.effectiveness,
        prompt_used=new_rule.prompt_used,
        is_active=new_rule.is_active
    )

@router.post("/generate", response_model=RuleGenerateResponse)
def generate_rule_with_ai(
    req: RuleGenerateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    GPT-4o Assisted Natural Language Rule Generation Endpoint (Section III-B & Figure 8).
    Converts business requirements into verifiable JSON rule schemas with coherence verification.
    """
    res = AIRuleGenerator.generate_rule(
        instruction=req.instruction,
        selected_column=req.selected_column,
        template_headers=req.template_headers,
        suggested_data_type=req.suggested_data_type,
        template_name=req.template_name
    )

    return RuleGenerateResponse(
        success=res["success"],
        generated_rule=res.get("generated_rule"),
        error=res.get("error"),
        coherence_passed=res.get("coherence_passed", False),
        retries_used=res.get("retries_used", 0)
    )

@router.post("/test")
def test_rule_evaluation(test_req: Dict[str, Any]):
    """
    Test a rule JSON against a sample row or single value in real-time.
    """
    rule_data = test_req.get("rule", {})
    row_data = test_req.get("row_data", {})
    column_name = test_req.get("column_name", "")

    if not column_name and "Header" in rule_data and rule_data["Header"]:
        column_name = rule_data["Header"][0]

    result = RuleEvaluator.evaluate(rule_data, row_data, column_name)
    return {
        "is_valid": result.is_valid,
        "error_message": result.error_message,
        "severity": result.severity
    }

@router.post("/assign")
def assign_rule_to_column(
    assignment: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    column_id = assignment.get("column_id")
    rule_id = assignment.get("rule_id")

    col = db.query(TemplateColumn).filter(TemplateColumn.id == column_id).first()
    rule = db.query(Rule).filter(Rule.id == rule_id).first()

    if not col or not rule:
        raise HTTPException(status_code=404, detail="Column or Rule not found")

    existing = db.query(TemplateColumnRule).filter(
        TemplateColumnRule.template_column_id == column_id,
        TemplateColumnRule.rule_id == rule_id
    ).first()

    if not existing:
        tcr = TemplateColumnRule(template_column_id=column_id, rule_id=rule_id)
        db.add(tcr)
        db.commit()

    return {"message": f"Rule '{rule.name}' assigned to column '{col.name}'"}

@router.delete("/unassign/{column_id}/{rule_id}")
def unassign_rule(column_id: int, rule_id: int, db: Session = Depends(get_db)):
    tcr = db.query(TemplateColumnRule).filter(
        TemplateColumnRule.template_column_id == column_id,
        TemplateColumnRule.rule_id == rule_id
    ).first()
    if tcr:
        db.delete(tcr)
        db.commit()
    return {"message": "Rule unassigned"}

