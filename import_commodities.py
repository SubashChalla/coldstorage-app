import pandas as pd
from main import db, Commodity, Variety, Grade, app

EXCEL_FILE = "Commodities Stored w Varieties Grades HSN.xlsx"

df = pd.read_excel(EXCEL_FILE)
df.columns = df.columns.str.strip()

expected_columns = ['Commodity Name', 'Variety', 'Grade', 'HSN Code']
if not all(col in df.columns for col in expected_columns):
    raise ValueError(f"Missing columns: {expected_columns}")

df = df.dropna(subset=['Commodity Name'])

with app.app_context():
    for _, row in df.iterrows():
        commodity_name = str(row['Commodity Name']).strip()
        variety_name = str(row['Variety']).strip() or None if pd.notna(row['Variety']) else None
        grade_name = str(row['Grade']).strip() or None if pd.notna(row['Grade']) else None
        hsn_code = str(row['HSN Code']).strip() or None if pd.notna(row['HSN Code']) else None

        commodity = Commodity.query.filter_by(name=commodity_name).first()
        if not commodity:
            commodity = Commodity(name=commodity_name, hsn_code=hsn_code)
            db.session.add(commodity)
            db.session.flush()

        variety = None
        if variety_name:
            variety = Variety.query.filter_by(name=variety_name, commodity_id=commodity.id).first()
            if not variety:
                variety = Variety(name=variety_name, commodity_id=commodity.id)
                db.session.add(variety)
                db.session.flush()

        if grade_name and variety:
            grade = Grade.query.filter_by(name=grade_name, variety_id=variety.id).first()
            if not grade:
                grade = Grade(name=grade_name, variety_id=variety.id)
                db.session.add(grade)

    db.session.commit()
    print("✅ Import complete.")
