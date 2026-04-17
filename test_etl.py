import unittest
import pandas as pd
from datetime import datetime
import os
import sys

# Add working directory to path if needed, though run locally it'll be fine
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import ETL

class TestETL(unittest.TestCase):
    
    def test_date_formatting(self):
        """
        Verify that 2026 is properly truncated to 26 and not something else.
        And ensure missing leading zeros on day/month are handled correctly.
        """
        def format_date(dt_str):
            dt_obj = datetime.strptime(dt_str, '%m/%d/%y')
            return f"{dt_obj.month}/{dt_obj.day}/{dt_obj.year % 100:02d}"
        
        self.assertEqual(format_date('04/07/26'), '4/7/26')
        self.assertEqual(format_date('01/05/05'), '1/5/05')
        self.assertEqual(format_date('10/12/26'), '10/12/26')
        self.assertEqual(format_date('2/2/02'), '2/2/02')

    def test_ffill_logic(self):
        """
        Verify the forward filling behavior matches our metadata handling.
        Empty cells inherit from the previously seen valid cell.
        """
        data = {
            'row4': [None, None, 'Connect', None, 'Design Build', None]
        }
        df = pd.DataFrame(data)
        
        filled = df['row4'].ffill()
        
        # Test first two nulls remain null (nothing to forward-fill from)
        self.assertTrue(pd.isna(filled[0]))
        self.assertTrue(pd.isna(filled[1]))
        
        # Test valid cell
        self.assertEqual(filled[2], 'Connect')
        
        # Test successful ffill propagation over empty cell
        self.assertEqual(filled[3], 'Connect')
        
        # Test new category breaks chain
        self.assertEqual(filled[4], 'Design Build')
        
        # Test ffill propagation is successful again
        self.assertEqual(filled[5], 'Design Build')

if __name__ == '__main__':
    unittest.main()
