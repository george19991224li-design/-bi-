import unittest
import pandas as pd
from data_utils import numeric, read_table, aggregate


class DataTests(unittest.TestCase):
    def test_currency_and_percentage(self):
        values = numeric(pd.Series(['￥1,250.50','(20)','bad','0']))
        self.assertEqual(values.iloc[0],1250.5)
        self.assertEqual(values.iloc[1],-20)
        self.assertTrue(pd.isna(values.iloc[2]))
        self.assertEqual(values.iloc[3],0)
        self.assertEqual(list(numeric(pd.Series(['25%',25]),True,'整数')), [.25,.25])

    def test_gbk_csv(self):
        df = read_table('产品,毛利,售价,利润率\n茶杯,10,20,50%'.encode('gb18030'),'test.csv')
        self.assertEqual(df.iloc[0]['产品'],'茶杯')

    def test_aggregation_missing_and_rates(self):
        df = pd.DataFrame({'类别':['A','A','B'],'利润':[10,30,None],'价格':[20,60,10],'比例':['50%','25%',None]})
        result, _, invalid = aggregate(df,'类别',{'毛利':'利润','售价':'价格','利润率':'比例'},'小数','合计')
        self.assertEqual(result.iloc[0]['毛利'],40)
        self.assertEqual(result.iloc[0]['售价'],40)
        self.assertEqual(result.iloc[0]['利润率'],.375)
        self.assertTrue(pd.isna(result.iloc[1]['毛利']))
        self.assertEqual(invalid['利润率'],1)


if __name__ == '__main__':
    unittest.main()
