# Custom Data Extraction Tool (ETL)

**Author:** [xylaes](https://github.com/xylaes)

This application automates the conversion of the `ReportPivotGrid` Excel file into a standardized CSV format for import.

## Instructions

1. Ensure your `ReportPivotGrid` file is saved on your computer (it must be an `.xlsx` Excel file).
2. Double-click the `ETL.exe` file to launch the Custom Data Extraction Tool.
3. In the application window, click the **Browse** button next to the input file field.
4. Locate and select your `ReportPivotGrid` Excel file, then click **Open**.
5. Click the **Start** button in the lower right corner of the window.
6. The application will scan and process the file. A progress bar will show its status.
7. Once finished, a new file named `transformed_hours_import.csv` will be automatically created in the EXACT SAME FOLDER where your original Excel file was located.
8. Your file is fully formatted and ready for import!

## Troubleshooting

- If an error occurs, an entry is written into a `session_log.txt` file located in the same folder as `ETL.exe`.
- If the output looks incorrect, ensure the Excel sheet matches the standard structure of the original `ReportPivotGrid`.
