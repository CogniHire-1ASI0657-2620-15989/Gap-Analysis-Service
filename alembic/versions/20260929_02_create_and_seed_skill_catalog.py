"""create and seed skill catalog

Revision ID: 20260929_02
Revises: 20260929_01
Create Date: 2026-09-29
"""
from alembic import op
import sqlalchemy as sa


revision = "20260929_02"
down_revision = "20260929_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    skill_catalog = op.create_table(
        "skill_catalog",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=150), nullable=False, unique=True),
        sa.Column("skill_type", sa.String(length=20), nullable=False),
        sa.Column("aliases", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.bulk_insert(skill_catalog, _seed_skills())


def downgrade() -> None:
    op.drop_table("skill_catalog")


def _seed_skills() -> list[dict]:
    return [
        {"name": name, "skill_type": skill_type, "aliases": aliases, "is_active": True}
        for name, skill_type, aliases in [
            ("Python", "hard", ["python"]), ("Java", "hard", ["java"]), ("C#", "hard", ["c#", "csharp", ".net"]),
            ("JavaScript", "hard", ["javascript", "js"]), ("TypeScript", "hard", ["typescript", "ts"]),
            ("SQL", "hard", ["sql"]), ("PostgreSQL", "hard", ["postgresql", "postgres"]),
            ("MySQL", "hard", ["mysql"]), ("MongoDB", "hard", ["mongodb", "mongo db"]),
            ("FastAPI", "hard", ["fastapi"]), ("Django", "hard", ["django"]), ("Spring Boot", "hard", ["spring boot"]),
            ("React", "hard", ["react", "reactjs"]), ("Angular", "hard", ["angular"]), ("Vue.js", "hard", ["vue", "vue.js"]),
            ("Docker", "hard", ["docker", "contenedores"]), ("Kubernetes", "hard", ["kubernetes", "k8s"]),
            ("AWS", "hard", ["aws", "amazon web services"]), ("Azure", "hard", ["azure", "microsoft azure"]),
            ("Google Cloud", "hard", ["google cloud", "gcp"]), ("Git", "hard", ["git", "github", "gitlab"]),
            ("Linux", "hard", ["linux"]), ("CI/CD", "hard", ["ci/cd", "continuous integration", "continuous delivery"]),
            ("Figma", "hard", ["figma"]), ("UX/UI Design", "hard", ["ux", "ui", "user experience", "user interface"]),
            ("SEO", "hard", ["seo", "search engine optimization"]), ("Google Analytics", "hard", ["google analytics", "analytics"]),
            ("Marketing Digital", "hard", ["marketing digital", "digital marketing"]), ("Ventas", "hard", ["ventas", "sales", "venta consultiva"]),
            ("CRM", "hard", ["crm", "salesforce", "hubspot"]), ("Excel", "hard", ["excel", "microsoft excel"]),
            ("Power BI", "hard", ["power bi", "powerbi"]), ("Tableau", "hard", ["tableau"]),
            ("Análisis de Datos", "hard", ["analisis de datos", "análisis de datos", "data analysis"]),
            ("Contabilidad", "hard", ["contabilidad", "accounting"]), ("Finanzas", "hard", ["finanzas", "finance"]),
            ("SAP", "hard", ["sap"]), ("Recursos Humanos", "hard", ["recursos humanos", "human resources", "rrhh"]),
            ("Reclutamiento", "hard", ["reclutamiento", "recruitment", "selección de personal"]),
            ("Gestión de Proyectos", "hard", ["gestión de proyectos", "gestion de proyectos", "project management"]),
            ("Scrum", "soft", ["scrum", "agile", "ágil", "agil"]), ("Comunicación", "soft", ["comunicación", "comunicacion", "communication"]),
            ("Trabajo en equipo", "soft", ["trabajo en equipo", "teamwork"]),
            ("Liderazgo", "soft", ["liderazgo", "leadership"]),
            ("Resolución de problemas", "soft", ["resolución de problemas", "resolucion de problemas", "problem solving"]),
            ("Pensamiento crítico", "soft", ["pensamiento crítico", "pensamiento critico", "critical thinking"]),
            ("Adaptabilidad", "soft", ["adaptabilidad", "adaptable"]), ("Negociación", "soft", ["negociación", "negociacion", "negotiation"]),
            ("Orientación al cliente", "soft", ["orientación al cliente", "orientacion al cliente", "customer service"]),
            ("Gestión del tiempo", "soft", ["gestión del tiempo", "gestion del tiempo", "time management"]),
        ]
    ]
