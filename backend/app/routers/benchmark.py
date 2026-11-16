import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from typing import Dict, Any

router = APIRouter(prefix="/benchmark", tags=["Research Benchmark"])

@router.get("/get-sample/{sample_name}")
def get_sample_file(sample_name: str):
    """
    Downloads one of the pre-seeded sample Excel files for one-click testing.
    """
    sample_dir = os.path.join(os.path.dirname(__file__), "..", "..", "sample_data")
    file_path = os.path.join(sample_dir, sample_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Sample file not found")
    return FileResponse(
        path=file_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=sample_name
    )

@router.get("/metrics")
def get_benchmark_comparison():
    """
    Returns empirical evaluation data published in IEEE Access (Section VI).
    Compares Scenario 1 (Manual Process) vs Scenario 2 (Accura Automated Workflow).
    """
    return {
        "case_study": {
            "organization": "Inventiva Insurtech Solutions S.A.C.",
            "domain": "InsurTech Data Migration",
            "participants_count": 50,
            "total_records": 400779,
            "total_columns": 95,
            "total_rules": 49
        },
        "datasets": [
            {
                "template": "Plantilla_ordenes",
                "records": 138725,
                "columns": 23,
                "rules": 14,
                "description": "Issue orders dataset with order values, status tracking, and date limits."
            },
            {
                "template": "Plantilla_polizas",
                "records": 126403,
                "columns": 19,
                "rules": 5,
                "description": "Policy master records with coverage amounts, validity periods, and client links."
            },
            {
                "template": "Plantilla_clientes",
                "records": 23914,
                "columns": 34,
                "rules": 18,
                "description": "Customer demographics, DNI/RUC document rules, complex lists, and dependencies."
            },
            {
                "template": "Plantilla_facturas",
                "records": 111737,
                "columns": 19,
                "rules": 12,
                "description": "Billing, tax breakdowns, invoice numbers, and payment dates."
            }
        ],
        "rule_definition": {
            "evaluated_rules": 35,
            "manual": {
                "correct": 29,
                "adjusted": 6,
                "acc": 82.86,
                "adr": 17.14
            },
            "accura": {
                "correct": 34,
                "adjusted": 1,
                "acc": 97.14,
                "adr": 2.86
            },
            "improvement": {
                "acc_gain_pp": 14.28,
                "adr_reduction_pp": 14.28
            }
        },
        "validation_time_minutes": {
            "manual": {
                "format_validation": 42.50,
                "rule_creation": 77.50,
                "rule_verification": 46.25,
                "data_validation": 17.50,
                "total_average": 183.75
            },
            "accura": {
                "format_validation": 3.75,
                "rule_creation": 14.25,
                "rule_verification": 5.75,
                "data_validation": 4.25,
                "total_average": 28.00
            },
            "reduction": {
                "minutes_saved": 155.75,
                "trv_percentage": 84.76,  # Overall Time Reduction in Validation
                "trc_percentage": 81.61   # Time Reduction in Rule Creation
            }
        },
        "error_detection": {
            "manual": {
                "tp": 67509,
                "fp": 3610,
                "fn": 4521,
                "precision": 94.92,
                "recall": 93.72,
                "f1_score": 94.32
            },
            "accura": {
                "tp": 71909,
                "fp": 0,
                "fn": 121,
                "precision": 100.00,
                "recall": 99.83,
                "f1_score": 99.92
            },
            "improvement": {
                "precision_gain_pp": 5.08,
                "recall_gain_pp": 6.11,
                "f1_gain_pp": 5.60
            }
        }
    }
