import os
import json
import openpyxl
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

from backend.app.database import engine, SessionLocal, Base
from backend.app.models.user import Role, User, TemplateUserAccess
from backend.app.models.template import Template, TemplateColumn, Rule, TemplateColumnRule
from backend.app.routers.auth import hash_password

def seed_database():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # 1. ROLES
        roles = {
            "Administrator": db.query(Role).filter(Role.name == "Administrator").first(),
            "Technical user": db.query(Role).filter(Role.name == "Technical user").first(),
            "Client user": db.query(Role).filter(Role.name == "Client user").first(),
        }

        for r_name in ["Administrator", "Technical user", "Client user"]:
            if not roles[r_name]:
                new_r = Role(name=r_name, status="Active")
                db.add(new_r)
                db.commit()
                db.refresh(new_r)
                roles[r_name] = new_r

        # 2. USERS
        admin_user = db.query(User).filter(User.email.in_(["admin@dataguard.ai", "admin@accura.io"])).first()
        if not admin_user:
            admin_user = User(
                role_id=roles["Administrator"].id,
                name="System Administrator",
                email="admin@dataguard.ai",
                password=hash_password("admin123"),
                document="44556677",
                department="IT & Architecture",
                send_emails=True,
                is_active=True,
                status="Active"
            )
            db.add(admin_user)
        else:
            admin_user.email = "admin@dataguard.ai"

        tech_user = db.query(User).filter(User.email.in_(["tech@dataguard.ai", "tech@accura.io"])).first()
        if not tech_user:
            tech_user = User(
                role_id=roles["Technical user"].id,
                name="QA Data Engineer",
                email="tech@dataguard.ai",
                password=hash_password("tech123"),
                document="77889900",
                department="Data Operations",
                send_emails=True,
                is_active=True,
                status="Active"
            )
            db.add(tech_user)
        else:
            tech_user.email = "tech@dataguard.ai"

        client_user = db.query(User).filter(User.email == "client@inventiva.com").first()
        if not client_user:
            client_user = User(
                role_id=roles["Client user"].id,
                name="InsurTech Functional Reviewer",
                email="client@inventiva.com",
                password=hash_password("client123"),
                document="10203040",
                department="Underwriting & Claims",
                send_emails=True,
                is_active=True,
                status="Active"
            )
            db.add(client_user)

        db.commit()

        # Check if templates already seeded
        if db.query(Template).count() > 0:
            print("Database already seeded with templates.")
            return

        print("Seeding templates, columns, and validation rules from paper...")

        # 3. GLOBAL VALIDATION RULES (InsurTech Domain)
        rules_def = [
            # 1. Document Rules
            {
                "name": "DNI Document Length (8 digits)",
                "data_type": "Document",
                "json": {
                    "Rule name": "DNI Document Length (8 digits)",
                    "Data type": "Document",
                    "Required field": True,
                    "Header": ["Numero_Documento"],
                    "Header rule": ["Numero_Documento"],
                    "Error message": "DNI must be an 8-character identification number.",
                    "Description": "Validates that national identity documents contain exactly 8 digits.",
                    "Example": {"Valid example": "45678912", "Invalid example": "123"},
                    "Rule": {"Minimum length": 8, "Maximum length": 8}
                }
            },
            {
                "name": "RUC Tax ID Length (11 digits)",
                "data_type": "Document",
                "json": {
                    "Rule name": "RUC Tax ID Length (11 digits)",
                    "Data type": "Document",
                    "Required field": True,
                    "Header": ["Numero_Documento"],
                    "Header rule": ["Numero_Documento"],
                    "Error message": "RUC must be an 11-digit fiscal identifier.",
                    "Description": "Validates corporate tax registration numbers in Peru.",
                    "Example": {"Valid example": "20512345678", "Invalid example": "205123"},
                    "Rule": {"Minimum length": 11, "Maximum length": 11}
                }
            },
            {
                "name": "Identification Document Length (8-12 chars)",
                "data_type": "Document",
                "json": {
                    "Rule name": "Identification Document Length (8-12 chars)",
                    "Data type": "Document",
                    "Required field": True,
                    "Header": ["Numero_Documento"],
                    "Header rule": ["Numero_Documento"],
                    "Error message": "Document number must be between 8 and 12 characters.",
                    "Description": "General document validation for personal or corporate IDs.",
                    "Example": {"Valid example": "45678912", "Invalid example": "123"},
                    "Rule": {"Minimum length": 8, "Maximum length": 12}
                }
            },
            # 2. List Rules
            {
                "name": "Document Type Allowed Values",
                "data_type": "List",
                "json": {
                    "Rule name": "Document Type Allowed Values",
                    "Data type": "List",
                    "Required field": True,
                    "Header": ["Tipo_Documento"],
                    "Header rule": ["Tipo_Documento"],
                    "Error message": "Document type must be DNI, RUC, CE, or PAS.",
                    "Description": "Validates that the document type belongs to authorized InsurTech categories.",
                    "Example": {"Valid example": "DNI", "Invalid example": "XYZ"},
                    "Rule": {"List": ["DNI", "RUC", "CE", "PAS"]}
                }
            },
            {
                "name": "Person Type Allowed Values",
                "data_type": "List",
                "json": {
                    "Rule name": "Person Type Allowed Values",
                    "Data type": "List",
                    "Required field": True,
                    "Header": ["Tipo_Persona"],
                    "Header rule": ["Tipo_Persona"],
                    "Error message": "Person type must be either 'PN' (Natural) or 'PJ' (Juridical).",
                    "Description": "Validates legal personality designation.",
                    "Example": {"Valid example": "PN", "Invalid example": "CORP"},
                    "Rule": {"List": ["PN", "PJ"]}
                }
            },
            {
                "name": "Policy Status Allowed Values",
                "data_type": "List",
                "json": {
                    "Rule name": "Policy Status Allowed Values",
                    "Data type": "List",
                    "Required field": True,
                    "Header": ["Estado_Poliza"],
                    "Header rule": ["Estado_Poliza"],
                    "Error message": "Policy status must be EMITIDA, VIGENTE, ANULADA, or CANCELADA.",
                    "Description": "Ensures policy state adheres to life cycle states.",
                    "Example": {"Valid example": "VIGENTE", "Invalid example": "PENDIENTE"},
                    "Rule": {"List": ["EMITIDA", "VIGENTE", "ANULADA", "CANCELADA"]}
                }
            },
            {
                "name": "Order Status Allowed Values",
                "data_type": "List",
                "json": {
                    "Rule name": "Order Status Allowed Values",
                    "Data type": "List",
                    "Required field": True,
                    "Header": ["Estado_Orden"],
                    "Header rule": ["Estado_Orden"],
                    "Error message": "Order status must be GENERADA, APROBADA, or RECHAZADA.",
                    "Description": "Enforces workflow state for issuance orders.",
                    "Example": {"Valid example": "APROBADA", "Invalid example": "WAITING"},
                    "Rule": {"List": ["GENERADA", "APROBADA", "RECHAZADA"]}
                }
            },
            {
                "name": "Currency Allowed Values",
                "data_type": "List",
                "json": {
                    "Rule name": "Currency Allowed Values",
                    "Data type": "List",
                    "Required field": True,
                    "Header": ["Moneda"],
                    "Header rule": ["Moneda"],
                    "Error message": "Currency must be PEN (Soles) or USD (US Dollars).",
                    "Description": "Restricts transactions to authorized currencies.",
                    "Example": {"Valid example": "USD", "Invalid example": "EUR"},
                    "Rule": {"List": ["PEN", "USD"]}
                }
            },
            {
                "name": "Invoice Status Allowed Values",
                "data_type": "List",
                "json": {
                    "Rule name": "Invoice Status Allowed Values",
                    "Data type": "List",
                    "Required field": True,
                    "Header": ["Estado_Factura"],
                    "Header rule": ["Estado_Factura"],
                    "Error message": "Invoice status must be PAGADA, PENDIENTE, or ANULADA.",
                    "Description": "InsurTech billing status validation.",
                    "Example": {"Valid example": "PAGADA", "Invalid example": "DRAFT"},
                    "Rule": {"List": ["PAGADA", "PENDIENTE", "ANULADA"]}
                }
            },
            # 3. Number Rules
            {
                "name": "Policy Premium Amount Range",
                "data_type": "Number",
                "json": {
                    "Rule name": "Policy Premium Amount Range",
                    "Data type": "Number",
                    "Required field": True,
                    "Header": ["Prima_Total"],
                    "Header rule": ["Prima_Total"],
                    "Error message": "Total premium must be positive between 1.00 and 1,000,000.00 with max 2 decimals.",
                    "Description": "Numeric boundaries for insurance premium amounts.",
                    "Example": {"Valid example": 1500.50, "Invalid example": -50.0},
                    "Rule": {"Minimum value": 1.00, "Maximum value": 1000000.00, "Number of decimals": 2}
                }
            },
            {
                "name": "Sum Insured Range",
                "data_type": "Number",
                "json": {
                    "Rule name": "Sum Insured Range",
                    "Data type": "Number",
                    "Required field": True,
                    "Header": ["Suma_Asegurada"],
                    "Header rule": ["Suma_Asegurada"],
                    "Error message": "Sum insured must be between 100.00 and 50,000,000.00.",
                    "Description": "Validates coverage sum insured values.",
                    "Example": {"Valid example": 50000.00, "Invalid example": 0},
                    "Rule": {"Minimum value": 100.00, "Maximum value": 50000000.00, "Number of decimals": 2}
                }
            },
            {
                "name": "Tax Amount Range",
                "data_type": "Number",
                "json": {
                    "Rule name": "Tax Amount Range",
                    "Data type": "Number",
                    "Required field": True,
                    "Header": ["Monto_IGV"],
                    "Header rule": ["Monto_IGV"],
                    "Error message": "Tax amount (IGV) must be non-negative up to 200,000.00.",
                    "Description": "Validates calculated sales tax.",
                    "Example": {"Valid example": 180.00, "Invalid example": -10.0},
                    "Rule": {"Minimum value": 0.00, "Maximum value": 200000.00, "Number of decimals": 2}
                }
            },
            {
                "name": "Invoice Total Amount Range",
                "data_type": "Number",
                "json": {
                    "Rule name": "Invoice Total Amount Range",
                    "Data type": "Number",
                    "Required field": True,
                    "Header": ["Monto_Total"],
                    "Header rule": ["Monto_Total"],
                    "Error message": "Invoice total must be between 1.00 and 2,000,000.00.",
                    "Description": "Validates invoice grand total.",
                    "Example": {"Valid example": 1180.00, "Invalid example": 0},
                    "Rule": {"Minimum value": 1.00, "Maximum value": 2000000.00, "Number of decimals": 2}
                }
            },
            {
                "name": "Commission Percentage Range (0 - 50%)",
                "data_type": "Number",
                "json": {
                    "Rule name": "Commission Percentage Range (0 - 50%)",
                    "Data type": "Number",
                    "Required field": False,
                    "Header": ["Porcentaje_Comision"],
                    "Header rule": ["Porcentaje_Comision"],
                    "Error message": "Broker commission percentage must be between 0.00% and 50.00%.",
                    "Description": "Limits broker commission margins.",
                    "Example": {"Valid example": 15.5, "Invalid example": 75.0},
                    "Rule": {"Minimum value": 0.00, "Maximum value": 50.00, "Number of decimals": 2}
                }
            },
            # 4. Email & Phone Rules
            {
                "name": "Customer Email Format",
                "data_type": "Email",
                "json": {
                    "Rule name": "Customer Email Format",
                    "Data type": "Email",
                    "Required field": False,
                    "Header": ["Correo_Electronico"],
                    "Header rule": ["Correo_Electronico"],
                    "Error message": "Customer email must follow standard email syntax and not exceed 100 characters.",
                    "Description": "Validates electronic contact addresses.",
                    "Example": {"Valid example": "cliente@empresa.com", "Invalid example": "invalid.email"},
                    "Rule": {"Format": "email", "Maximum length": 100}
                }
            },
            {
                "name": "Mobile Phone Format (+51 / 9 digits)",
                "data_type": "Phone",
                "json": {
                    "Rule name": "Mobile Phone Format (+51 / 9 digits)",
                    "Data type": "Phone",
                    "Required field": False,
                    "Header": ["Telefono_Contacto"],
                    "Header rule": ["Telefono_Contacto"],
                    "Error message": "Contact phone must have at least 9 digits with optional country prefix.",
                    "Description": "Checks phone number length and numeric format.",
                    "Example": {"Valid example": "+51987654321", "Invalid example": "123"},
                    "Rule": {"Minimum length": 9, "Country code": "+51"}
                }
            },
            # 5. Date Rules
            {
                "name": "Policy Issue Date Validity",
                "data_type": "Date",
                "json": {
                    "Rule name": "Policy Issue Date Validity",
                    "Data type": "Date",
                    "Required field": True,
                    "Header": ["Fecha_Emision"],
                    "Header rule": ["Fecha_Emision"],
                    "Error message": "Issue date must follow yyyy-MM-dd format between 2000-01-01 and 2026-12-31.",
                    "Description": "Validates policy inception dates.",
                    "Example": {"Valid example": "2024-01-15", "Invalid example": "2040-01-01"},
                    "Rule": {"Format": "yyyy-MM-dd", "Minimum date": "2000-01-01", "Maximum date": "2026-12-31"}
                }
            },
            {
                "name": "Invoice Due Date Validity",
                "data_type": "Date",
                "json": {
                    "Rule name": "Invoice Due Date Validity",
                    "Data type": "Date",
                    "Required field": True,
                    "Header": ["Fecha_Vencimiento"],
                    "Header rule": ["Fecha_Vencimiento"],
                    "Error message": "Due date must be in format yyyy-MM-dd up to 2027-12-31.",
                    "Description": "Payment due date validation.",
                    "Example": {"Valid example": "2025-06-30", "Invalid example": "1990-01-01"},
                    "Rule": {"Format": "yyyy-MM-dd", "Minimum date": "2015-01-01", "Maximum date": "2027-12-31"}
                }
            },
            # 6. Text Rules
            {
                "name": "Customer Name Length (3 - 100 chars)",
                "data_type": "Text",
                "json": {
                    "Rule name": "Customer Name Length (3 - 100 chars)",
                    "Data type": "Text",
                    "Required field": True,
                    "Header": ["Nombre_Cliente"],
                    "Header rule": ["Nombre_Cliente"],
                    "Error message": "Customer name must be between 3 and 100 characters.",
                    "Description": "Ensures customer name is not blank and does not exceed field capacity.",
                    "Example": {"Valid example": "Juan Perez", "Invalid example": "A"},
                    "Rule": {"Minimum length": 3, "Maximum length": 100}
                }
            },
            {
                "name": "Policy Number Format (5 - 30 chars)",
                "data_type": "Text",
                "json": {
                    "Rule name": "Policy Number Format (5 - 30 chars)",
                    "Data type": "Text",
                    "Required field": True,
                    "Header": ["Numero_Poliza"],
                    "Header rule": ["Numero_Poliza"],
                    "Error message": "Policy number must be between 5 and 30 alphanumeric characters.",
                    "Description": "Unique policy identifier validation.",
                    "Example": {"Valid example": "POL-2024-00192", "Invalid example": "12"},
                    "Rule": {"Minimum length": 5, "Maximum length": 30}
                }
            },
            # 7. Complex List Rule
            {
                "name": "Peruvian Geographic Division (Dept - Prov)",
                "data_type": "Complex List",
                "json": {
                    "Rule name": "Peruvian Geographic Division (Dept - Prov)",
                    "Data type": "Complex List",
                    "Required field": False,
                    "Header": ["Departamento", "Provincia"],
                    "Header rule": ["Departamento", "Provincia"],
                    "Error message": "Province does not match the designated department in official administrative division.",
                    "Description": "Ensures geographic consistency between department and province.",
                    "Example": {"Valid example": "Lima / Lima", "Invalid example": "Lima / Arequipa"},
                    "Rule": {
                        "Complex list": [
                            {"Departamento": "LIMA", "Provincia": "LIMA"},
                            {"Departamento": "LIMA", "Provincia": "CANETE"},
                            {"Departamento": "CUSCO", "Provincia": "URUBAMBA"},
                            {"Departamento": "CUSCO", "Provincia": "CUSCO"},
                            {"Departamento": "AREQUIPA", "Provincia": "AREQUIPA"},
                            {"Departamento": "PIURA", "Provincia": "PIURA"}
                        ]
                    }
                }
            },
            # 8. Dependency Rule (Key InsurTech logic from Paper Section III-C Page 5-6)
            {
                "name": "Person Type to Document Type Dependency",
                "data_type": "Dependency",
                "json": {
                    "Rule name": "Person Type to Document Type Dependency",
                    "Data type": "Dependency",
                    "Required field": True,
                    "Header": ["Tipo_Documento"],
                    "Header rule": ["Tipo_Persona"],
                    "Error message": "If Person Type is 'PJ' (Juridical), Document Type must be 'RUC'. If 'PN' (Natural), it must be 'DNI', 'CE', or 'PAS'.",
                    "Description": "Conditional relationship enforcing proper identification standard based on legal personality.",
                    "Example": {"Valid example": "PJ -> RUC", "Invalid example": "PJ -> DNI"},
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
            }
        ]

        created_rules: Dict[str, Rule] = {}
        for r_item in rules_def:
            rule_obj = Rule(
                name=r_item["name"],
                data_type=r_item["data_type"],
                json_rule=json.dumps(r_item["json"]),
                effectiveness=100.0,
                created_by="Administrator"
            )
            db.add(rule_obj)
            db.commit()
            db.refresh(rule_obj)
            created_rules[r_item["name"]] = rule_obj

        # 4. THE 4 MIGRATION TEMPLATES (Table 4 of Paper)
        # 1. Plantilla_polizas (19 columns, 5 rules)
        t_polizas = Template(
            user_id=admin_user.id,
            name="Plantilla_polizas",
            table_name="tbl_mig_polizas",
            description="Master policies dataset containing coverage, insurance lines, insured sums, and validity terms.",
            status="Published",
            created_by="Administrator"
        )
        db.add(t_polizas)
        db.commit()
        db.refresh(t_polizas)

        polizas_cols = [
            ("Numero_Poliza", "Text", True, ["Policy Number Format (5 - 30 chars)"]),
            ("Ramo_Seguro", "Text", True, []),
            ("Numero_Documento", "Document", True, ["Identification Document Length (8-12 chars)"]),
            ("Tipo_Documento", "List", True, ["Document Type Allowed Values"]),
            ("Nombre_Contratante", "Text", True, ["Customer Name Length (3 - 100 chars)"]),
            ("Fecha_Emision", "Date", True, ["Policy Issue Date Validity"]),
            ("Fecha_Inicio_Vigencia", "Date", True, []),
            ("Fecha_Fin_Vigencia", "Date", True, []),
            ("Moneda", "List", True, ["Currency Allowed Values"]),
            ("Prima_Neta", "Number", True, []),
            ("Monto_IGV", "Number", True, ["Tax Amount Range"]),
            ("Prima_Total", "Number", True, ["Policy Premium Amount Range"]),
            ("Suma_Asegurada", "Number", True, ["Sum Insured Range"]),
            ("Estado_Poliza", "List", True, ["Policy Status Allowed Values"]),
            ("Canal_Venta", "Text", False, []),
            ("Codigo_Agente", "Text", False, []),
            ("Porcentaje_Comision", "Number", False, ["Commission Percentage Range (0 - 50%)"]),
            ("Deducible", "Text", False, []),
            ("Observaciones", "Text", False, [])
        ]

        for idx, (col_name, d_type, req, r_names) in enumerate(polizas_cols):
            c_obj = TemplateColumn(
                template_id=t_polizas.id,
                name=col_name,
                data_type=d_type,
                is_required=req,
                order_index=idx,
                created_by="Administrator"
            )
            db.add(c_obj)
            db.commit()
            db.refresh(c_obj)

            for rn in r_names:
                if rn in created_rules:
                    db.add(TemplateColumnRule(template_column_id=c_obj.id, rule_id=created_rules[rn].id))
        db.commit()

        # 2. Plantilla_clientes (34 columns, 18 rules)
        t_clientes = Template(
            user_id=admin_user.id,
            name="Plantilla_clientes",
            table_name="tbl_mig_clientes",
            description="Customer demographics, tax designations, contacts, and legal entity dependencies.",
            status="Published",
            created_by="Administrator"
        )
        db.add(t_clientes)
        db.commit()
        db.refresh(t_clientes)

        clientes_cols = [
            ("Tipo_Persona", "List", True, ["Person Type Allowed Values"]),
            ("Tipo_Documento", "List", True, ["Document Type Allowed Values", "Person Type to Document Type Dependency"]),
            ("Numero_Documento", "Document", True, ["Identification Document Length (8-12 chars)"]),
            ("Nombre_Cliente", "Text", True, ["Customer Name Length (3 - 100 chars)"]),
            ("Apellido_Paterno", "Text", False, []),
            ("Apellido_Materno", "Text", False, []),
            ("Razon_Social", "Text", False, []),
            ("Correo_Electronico", "Email", False, ["Customer Email Format"]),
            ("Telefono_Contacto", "Phone", False, ["Mobile Phone Format (+51 / 9 digits)"]),
            ("Departamento", "Text", False, []),
            ("Provincia", "Text", False, ["Peruvian Geographic Division (Dept - Prov)"]),
            ("Distrito", "Text", False, []),
            ("Direccion", "Text", False, []),
            ("Fecha_Nacimiento", "Date", False, []),
            ("Estado_Civil", "List", False, []),
            ("Nacionalidad", "Text", False, []),
            ("Ocupacion", "Text", False, []),
            ("Representante_Legal", "Text", False, []),
            ("Doc_Representante", "Text", False, []),
            ("Actividad_Economica", "Text", False, []),
            ("Codigo_Postal", "Text", False, []),
            ("Telefono_Fijo", "Text", False, []),
            ("Celular_Secundario", "Text", False, []),
            ("Correo_Secundario", "Email", False, []),
            ("Tipo_Cliente", "Text", False, []),
            ("Segmento", "Text", False, []),
            ("Score_Crediticio", "Number", False, []),
            ("Fecha_Registro", "Date", False, []),
            ("Canal_Registro", "Text", False, []),
            ("PEP", "List", False, []),
            ("Estado_Contribuyente", "Text", False, []),
            ("Condicion_Domicilio", "Text", False, []),
            ("Agente_Retencion", "Text", False, []),
            ("Observaciones", "Text", False, [])
        ]

        for idx, (col_name, d_type, req, r_names) in enumerate(clientes_cols):
            c_obj = TemplateColumn(
                template_id=t_clientes.id,
                name=col_name,
                data_type=d_type,
                is_required=req,
                order_index=idx,
                created_by="Administrator"
            )
            db.add(c_obj)
            db.commit()
            db.refresh(c_obj)

            for rn in r_names:
                if rn in created_rules:
                    db.add(TemplateColumnRule(template_column_id=c_obj.id, rule_id=created_rules[rn].id))
        db.commit()

        # 3. Plantilla_ordenes (23 columns, 14 rules)
        t_ordenes = Template(
            user_id=admin_user.id,
            name="Plantilla_ordenes",
            table_name="tbl_mig_ordenes",
            description="Issue orders dataset with order amounts, status tracking, and broker channels.",
            status="Published",
            created_by="Administrator"
        )
        db.add(t_ordenes)
        db.commit()
        db.refresh(t_ordenes)

        ordenes_cols = [
            ("Numero_Orden", "Text", True, []),
            ("Numero_Poliza", "Text", True, ["Policy Number Format (5 - 30 chars)"]),
            ("Fecha_Orden", "Date", True, ["Policy Issue Date Validity"]),
            ("Estado_Orden", "List", True, ["Order Status Allowed Values"]),
            ("Tipo_Documento", "List", True, ["Document Type Allowed Values"]),
            ("Numero_Documento", "Document", True, ["Identification Document Length (8-12 chars)"]),
            ("Nombre_Solicitante", "Text", True, ["Customer Name Length (3 - 100 chars)"]),
            ("Moneda", "List", True, ["Currency Allowed Values"]),
            ("Monto_Orden", "Number", True, ["Policy Premium Amount Range"]),
            ("Porcentaje_Comision", "Number", False, ["Commission Percentage Range (0 - 50%)"]),
            ("Canal_Emision", "Text", False, []),
            ("Codigo_Sucursal", "Text", False, []),
            ("Aprobador", "Text", False, []),
            ("Fecha_Aprobacion", "Date", False, []),
            ("Tipo_Movimiento", "Text", False, []),
            ("Plan_Seguro", "Text", False, []),
            ("Frecuencia_Pago", "Text", False, []),
            ("Metodo_Pago", "Text", False, []),
            ("Numero_Cuotas", "Number", False, []),
            ("Codigo_Broker", "Text", False, []),
            ("Vigencia_Desde", "Date", False, []),
            ("Vigencia_Hasta", "Date", False, []),
            ("Observaciones", "Text", False, [])
        ]

        for idx, (col_name, d_type, req, r_names) in enumerate(ordenes_cols):
            c_obj = TemplateColumn(
                template_id=t_ordenes.id,
                name=col_name,
                data_type=d_type,
                is_required=req,
                order_index=idx,
                created_by="Administrator"
            )
            db.add(c_obj)
            db.commit()
            db.refresh(c_obj)

            for rn in r_names:
                if rn in created_rules:
                    db.add(TemplateColumnRule(template_column_id=c_obj.id, rule_id=created_rules[rn].id))
        db.commit()

        # 4. Plantilla_facturas (19 columns, 12 rules)
        t_facturas = Template(
            user_id=admin_user.id,
            name="Plantilla_facturas",
            table_name="tbl_mig_facturas",
            description="Billing, tax calculations, invoice numbers, and premium payment dates.",
            status="Published",
            created_by="Administrator"
        )
        db.add(t_facturas)
        db.commit()
        db.refresh(t_facturas)

        facturas_cols = [
            ("Numero_Factura", "Text", True, []),
            ("Numero_Poliza", "Text", True, ["Policy Number Format (5 - 30 chars)"]),
            ("Numero_Documento", "Document", True, ["Identification Document Length (8-12 chars)"]),
            ("Tipo_Documento", "List", True, ["Document Type Allowed Values"]),
            ("Nombre_Cliente", "Text", True, ["Customer Name Length (3 - 100 chars)"]),
            ("Fecha_Emision", "Date", True, ["Policy Issue Date Validity"]),
            ("Fecha_Vencimiento", "Date", True, ["Invoice Due Date Validity"]),
            ("Moneda", "List", True, ["Currency Allowed Values"]),
            ("Monto_Subtotal", "Number", True, ["Policy Premium Amount Range"]),
            ("Monto_IGV", "Number", True, ["Tax Amount Range"]),
            ("Monto_Total", "Number", True, ["Invoice Total Amount Range"]),
            ("Estado_Factura", "List", True, ["Invoice Status Allowed Values"]),
            ("Numero_Cuota", "Number", False, []),
            ("Forma_Pago", "Text", False, []),
            ("Banco", "Text", False, []),
            ("Numero_Operacion", "Text", False, []),
            ("Fecha_Pago", "Date", False, []),
            ("Monto_Pagado", "Number", False, []),
            ("Observaciones", "Text", False, [])
        ]

        for idx, (col_name, d_type, req, r_names) in enumerate(facturas_cols):
            c_obj = TemplateColumn(
                template_id=t_facturas.id,
                name=col_name,
                data_type=d_type,
                is_required=req,
                order_index=idx,
                created_by="Administrator"
            )
            db.add(c_obj)
            db.commit()
            db.refresh(c_obj)

            for rn in r_names:
                if rn in created_rules:
                    db.add(TemplateColumnRule(template_column_id=c_obj.id, rule_id=created_rules[rn].id))
        db.commit()

        # Grant client access to all 4 templates
        for t_inst in [t_polizas, t_clientes, t_ordenes, t_facturas]:
            db.add(TemplateUserAccess(
                template_id=t_inst.id,
                user_id=client_user.id,
                start_date=datetime.utcnow()
            ))
        db.commit()

        # 5. GENERATE SAMPLE TEST EXCEL FILES
        sample_dir = os.path.join(os.path.dirname(__file__), "..", "sample_data")
        os.makedirs(sample_dir, exist_ok=True)
        generate_sample_excel_files(sample_dir)

        print("DataGuard AI seed completed successfully with InsurTech templates and test datasets!")

    finally:
        db.close()

def generate_sample_excel_files(sample_dir: str):
    """
    Generates realistic Excel files for testing:
    1. Plantilla_polizas_valid.xlsx (Clean, 100% compliant)
    2. Plantilla_polizas_with_errors.xlsx (With controlled structural inconsistencies)
    3. Plantilla_clientes_with_errors.xlsx (With dependency and format errors)
    """
    # 1. Valid Policies
    wb_pol_ok = openpyxl.Workbook()
    ws = wb_pol_ok.active
    ws.title = "Plantilla_polizas"
    headers = [
        "Numero_Poliza", "Ramo_Seguro", "Numero_Documento", "Tipo_Documento", "Nombre_Contratante",
        "Fecha_Emision", "Fecha_Inicio_Vigencia", "Fecha_Fin_Vigencia", "Moneda", "Prima_Neta",
        "Monto_IGV", "Prima_Total", "Suma_Asegurada", "Estado_Poliza", "Canal_Venta",
        "Codigo_Agente", "Porcentaje_Comision", "Deducible", "Observaciones"
    ]
    ws.append(headers)

    valid_rows = [
        ["POL-2024-00101", "Vehicular", "45678912", "DNI", "Carlos Mendoza Ruiz", "2024-01-10", "2024-01-15", "2025-01-15", "USD", 1000.00, 180.00, 1180.00, 25000.00, "VIGENTE", "Directo", "AGT-01", 12.5, "10%", "Migracion sin novedad"],
        ["POL-2024-00102", "Salud", "20556677881", "RUC", "Inversiones del Sur S.A.C.", "2024-02-01", "2024-02-05", "2025-02-05", "PEN", 4500.00, 810.00, 5310.00, 150000.00, "EMITIDA", "Broker", "AGT-09", 15.0, "5%", "Poliza corporativa"],
        ["POL-2024-00103", "Vida", "71234567", "DNI", "Maria Elena Vasquez", "2024-03-12", "2024-03-15", "2025-03-15", "USD", 800.00, 144.00, 944.00, 100000.00, "VIGENTE", "Digital", "AGT-03", 8.0, "0%", "Cobro automatico"],
        ["POL-2024-00104", "Incendio", "20100456789", "RUC", "Textiles Andinos S.A.", "2024-04-18", "2024-04-20", "2025-04-20", "USD", 12000.00, 2160.00, 14160.00, 1500000.00, "VIGENTE", "Broker", "AGT-02", 18.0, "15%", "Inspeccion aprobada"],
        ["POL-2024-00105", "Responsabilidad Civil", "40987654", "DNI", "Jorge Benavides", "2024-05-02", "2024-05-05", "2025-05-05", "PEN", 1500.00, 270.00, 1770.00, 50000.00, "CANCELADA", "BancaSeguros", "AGT-11", 10.0, "10%", "Cancelacion a solicitud"]
    ]
    for r in valid_rows:
        ws.append(r)
    wb_pol_ok.save(os.path.join(sample_dir, "Plantilla_polizas_valid.xlsx"))

    # 2. Policies with intentional structural errors
    wb_pol_err = openpyxl.Workbook()
    ws_err = wb_pol_err.active
    ws_err.title = "Plantilla_polizas"
    ws_err.append(headers)

    err_rows = [
        # Row 2: Short document length (DNI 123 -> error), Invalid Policy Status (PENDING -> error)
        ["POL-2024-00201", "Vehicular", "123", "DNI", "Pedro Pascal", "2024-01-10", "2024-01-15", "2025-01-15", "USD", 1000.00, 180.00, 1180.00, 25000.00, "PENDING_APPROVAL", "Directo", "AGT-01", 12.5, "10%", ""],
        # Row 3: Negative premium (-500.00 -> error), Currency not PEN/USD (EUR -> error)
        ["POL-2024-00202", "Salud", "20556677881", "RUC", "Clinica Santa Luz", "2024-02-01", "2024-02-05", "2025-02-05", "EUR", -500.00, 810.00, -500.00, 150000.00, "EMITIDA", "Broker", "AGT-09", 15.0, "5%", ""],
        # Row 4: Short policy number ('P1' -> error min 5), Commission out of range (85.0% -> error max 50%)
        ["P1", "Vida", "71234567", "DNI", "Lucia Galvez", "2024-03-12", "2024-03-15", "2025-03-15", "USD", 800.00, 144.00, 944.00, 100000.00, "VIGENTE", "Digital", "AGT-03", 85.0, "0%", ""],
        # Row 5: Missing mandatory field (Numero_Poliza empty -> error), Date out of range (2045-12-31 -> error)
        ["", "Incendio", "20100456789", "RUC", "Fabrica El Sol", "2045-12-31", "2024-04-20", "2025-04-20", "USD", 12000.00, 2160.00, 14160.00, 1500000.00, "VIGENTE", "Broker", "AGT-02", 18.0, "15%", ""],
        # Row 6: Completely valid row
        ["POL-2024-00205", "Accidentes", "41223344", "DNI", "Andres Silva", "2024-06-01", "2024-06-05", "2025-06-05", "PEN", 600.00, 108.00, 708.00, 20000.00, "VIGENTE", "Directo", "AGT-04", 10.0, "5%", "Todo conforme"]
    ]
    for r in err_rows:
        ws_err.append(r)
    wb_pol_err.save(os.path.join(sample_dir, "Plantilla_polizas_with_errors.xlsx"))

    # 3. Customers with dependency errors & format errors
    wb_cli_err = openpyxl.Workbook()
    ws_cli = wb_cli_err.active
    ws_cli.title = "Plantilla_clientes"
    cli_headers = [
        "Tipo_Persona", "Tipo_Documento", "Numero_Documento", "Nombre_Cliente",
        "Correo_Electronico", "Telefono_Contacto", "Departamento", "Provincia"
    ]
    ws_cli.append(cli_headers)

    cli_rows = [
        # Valid natural person
        ["PN", "DNI", "45678912", "Juan Carlos Gomez", "jgomez@gmail.com", "+51987654321", "LIMA", "LIMA"],
        # Error: Person Type PJ with Document Type DNI (Violates Dependency Rule! PJ must be RUC)
        ["PJ", "DNI", "45678912", "Comercializadora Pacifico S.A.", "contacto@pacifico.pe", "+51987111222", "LIMA", "LIMA"],
        # Error: Invalid email format + Phone too short (only 4 digits)
        ["PN", "DNI", "72345678", "Ana Maria Morales", "correo_invalido_sin_arroba", "1234", "CUSCO", "CUSCO"],
        # Error: Geographic Complex List Mismatch (Lima Dept with Arequipa Prov)
        ["PN", "CE", "001234567", "Roberto Carlos Mendez", "roberto@mendez.com", "+51999888777", "LIMA", "AREQUIPA"],
        # Valid juridical person
        ["PJ", "RUC", "20551234567", "Transportes Andinos S.A.C.", "logistica@andinos.pe", "+51912345678", "AREQUIPA", "AREQUIPA"]
    ]
    for r in cli_rows:
        ws_cli.append(r)
    wb_cli_err.save(os.path.join(sample_dir, "Plantilla_clientes_with_errors.xlsx"))

if __name__ == "__main__":
    seed_database()

