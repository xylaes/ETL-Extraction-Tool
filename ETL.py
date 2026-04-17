# ----------------------------------------------------
# Author: xylaes (https://github.com/xylaes)
# Custom Data Extraction Tool with GUI 
# ----------------------------------------------------
import pandas as pd
from datetime import datetime
import os
import logging
from gooey import Gooey, GooeyParser

# Configure session logging
logging.basicConfig(
    filename='session_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def transform_data(input_path):
    """
    Core transformation logic separated from UI for testability.
    Reads an Excel file, extracts relevant time-tracking info, and saves
    to a standardized CSV alongside the input file location.
    """
    output_path = os.path.join(os.path.dirname(input_path), "transformed_hours_import.csv")
    try:
        logging.info(f"Started processing file: {input_path}")
        print(f"Reading file: {input_path}...", flush=True)
        
        source_raw = pd.read_excel(input_path, header=None, engine='openpyxl')

        # --- DATA TRANSFORMATION LOGIC ---
        # 1. Parse Headers
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
        data_rows = source_raw.iloc[7:]
        total_rows = len(data_rows)

        for idx_rel, (idx, row) in enumerate(data_rows.iterrows()):
            # Push Progress to Gooey UI Regex Intercepter
            progress_pct = int(100 * (idx_rel / max(total_rows, 1)))
            print(f"Progress: {progress_pct}%", flush=True)

            # Check for new Employee ID
            val0 = str(row[0]).strip() if pd.notna(row[0]) else None
            if val0 and val0 not in ['Total', 'Grand Total', 'nan']:
                current_emp_id = val0
                
            rate = row[1]
            if pd.notna(rate) and current_emp_id:
                for col_idx, info in col_mapping.items():
                    hours_val = round(float(row[col_idx]), 2) if pd.notna(row[col_idx]) else 0
                    if hours_val > 0:
                        # Convert date string to object then to M/D/YY handling single digits natively.
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
        print(f"Progress: 100%", flush=True)
        df_out = pd.DataFrame(records)
        df_out.to_csv(output_path, index=False)
        
        logging.info(f"Successfully processed and exported {len(records)} records to {output_path}")
        print(f"Success! {len(records)} records exported.", flush=True)
        print(f"File saved to: {output_path}", flush=True)
        
        return True, df_out
        
    except FileNotFoundError:
        logging.error(f"FileNotFoundError: The file {input_path} could not be located.")
        print("Error: Could not locate the selected input file. Please verify it exists.", flush=True)
        return False, None
    except Exception as e:
        logging.error(f"Failed to transform file: {str(e)}", exc_info=True)
        print(f"A critical error occurred while processing the file: {str(e)}", flush=True)
        return False, None


@Gooey(
    program_name="Custom Data Extraction Tool", 
    default_size=(600, 500),
    show_restart_button=True,
    progress_regex=r"^Progress: (?P<current>\d+)%$"
)
def main():
    parser = GooeyParser(description="Convert messy Excel reports to standardized CSV templates.")
    
    parser.add_argument(
        'input_file',
        help="Select the ReportPivotGrid (.xlsx) file",
        widget="FileChooser"
    )
    
    args = parser.parse_args()
    transform_data(args.input_file)

if __name__ == "__main__":
    main()
