import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest


class AppTests(unittest.TestCase):
    def test_demo_and_chart_controls(self):
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run(timeout=30)
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.metric), 4)
        mode = next(s for s in app.selectbox if s.label == '组合方式')
        mode.select('毛利与售价柱状 + 利润率折线').run()
        self.assertEqual(len(app.exception), 0)
        sort = next(s for s in app.selectbox if s.label == '排序')
        sort.select('毛利降序').run()
        self.assertEqual(app.dataframe[0].value.iloc[0]['维度'], '2026-12')


if __name__ == '__main__':
    unittest.main()
