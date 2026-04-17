import pandas as pd
from datetime import datetime
import os
from gooey import Gooey, GooeyParser

@Gooey(program_name="Excel to CSV Converter", default_size=(600, 500))
def main():
    parser = GooeyParser(description="Convert messy Excel reports to standardized CSV templates")
    
    # This creates the "Browse" button in the UI
    parser.add_argument(
        'input_file',
        help="Select the ReportPivotGrid (.xlsx) file",
        widget="FileChooser"
    )
    
    args = parser.parse_args()
    input_path = args.input_file
    
    # Professional touch: Auto-naming the output file based on the input location
    output_path = os.path.join(os.path.dirname(input_path), "transformed_hours_import.csv")

    try:
        print(f"Reading file: {input_path}...")
        source_raw = pd.read_excel(input_path, header=None, engine='openpyxl')

        # --- DATA TRANSFORMATION LOGIC ---
        # 1. Parse Headers (The 'iloc' logic we discussed)
        divisions = source_raw.iloc[4].ffill()
        dates = source_raw.iloc[5].ffill()
        hour_types = source_raw.iloc[6]

        col_mapping = {}
        for i in range(2, len(source_raw.columns)):
            div, dt, ht = str(divisions[i]), str(dates[i]), str(hour_types[i])
            if 'Total' in div or 'nan' in div or 'nan' in dt: continue
            
            rate_type = "REG" if "Regular" in ht else "OT" if "OT" in ht else None
            if rate_type:
                col_mapping[i] = {'Division': div, 'Date': dt, 'RateType': rate_type}

        # 2. Process Rows
        records = []
        current_emp_id = None

        for idx, row in source_raw.iloc[7:].iterrows():
            # Check for new Employee ID
            val0 = str(row[0]).strip() if pd.notna(row[0]) else None
            if val0 and val0 not in ['Total', 'Grand Total', 'nan']:
                current_emp_id = val0
                
            rate = row[1]
            if pd.notna(rate) and current_emp_id:
                for col_idx, info in col_mapping.items():
                    hours_val = round(float(row[col_idx]), 2) if pd.notna(row[col_idx]) else 0
                    if hours_val > 0:
                        # Convert date string to object then to M/D/YY
                        dt_obj = datetime.strptime(info['Date'], '%m/%d/%y')
                        fmt_date = f"{dt_obj.month}/{dt_obj.day}/{dt_obj.year % 100:02d}"
                        
                        records.append({
                            'Employee #': current_emp_id,
                            'Hours Worked Date': fmt_date,
                            'Pay Rate': rate,
                            'Rate Type (REG, OT, or DT)': info['RateType'],
                            'Hours Worked': hours_val,
                            'Project Name': info['Division'],
                            'Task Name': '',
                            'Shift Differential Name': '',
                            'Holiday Name': ''
                        })

        # 3. Save Output
        df_out = pd.DataFrame(records)
        df_out.to_csv(output_path, index=False)