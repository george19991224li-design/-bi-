"""Table parsing and explicit aggregation for the BI dashboard."""
from io import BytesIO, StringIO
from pathlib import Path
import re
import numpy as np
import pandas as pd


def read_table(data, name, sheet=0, header=0):
    suffix = Path(name).suffix.lower()
    if suffix in {'.csv', '.tsv', '.txt'}:
        encodings = ('utf-16',) if data.startswith((b'\xff\xfe', b'\xfe\xff')) else ('utf-8-sig', 'gb18030', 'utf-16')
        for encoding in encodings:
            try:
                text = data.decode(encoding)
                return pd.read_csv(StringIO(text), sep='\t' if suffix == '.tsv' else None,
                                   engine='python', header=header)
            except UnicodeError:
                continue
        raise ValueError('无法识别文件编码，请另存为 UTF-8 CSV。')
    engines = {'.xlsx': 'openpyxl', '.xlsm': 'openpyxl', '.xls': 'xlrd', '.ods': 'odf'}
    if suffix not in engines:
        raise ValueError('不支持此文件格式。')
    return pd.read_excel(BytesIO(data), engine=engines[suffix], sheet_name=sheet, header=header)


def sheet_names(data, name):
    if Path(name).suffix.lower() in {'.csv', '.tsv', '.txt'}:
        return []
    with pd.ExcelFile(BytesIO(data)) as book:
        return book.sheet_names


def numeric(series, percent=False, scale='小数（0.25 = 25%）'):
    def parse(value):
        if pd.isna(value):
            return np.nan
        s = str(value).strip().replace('％', '%').replace('，', ',')
        marked = '%' in s
        s = re.sub(r'[,\s¥￥$€元]', '', s).replace('%', '')
        if s.startswith('(') and s.endswith(')'):
            s = '-' + s[1:-1]
        try:
            n = float(s)
            if not np.isfinite(n):
                return np.nan
            return n / 100 if marked or (percent and scale.startswith('整数')) else n
        except ValueError:
            return np.nan
    return series.map(parse)


def aggregate(frame, dimension, mapping, scale, profit_mode):
    prepared = pd.DataFrame({'维度': frame[dimension].fillna('（空白）').astype(str)})
    invalid = {}
    for metric, column in mapping.items():
        prepared[metric] = numeric(frame[column], metric == '利润率', scale)
        invalid[metric] = int(prepared[metric].isna().sum())
    grouped = prepared.groupby('维度', sort=False)
    result = pd.DataFrame(index=grouped.size().index)
    result['毛利'] = grouped['毛利'].sum(min_count=1) if profit_mode == '合计' else grouped['毛利'].mean()
    result['售价'] = grouped['售价'].mean()
    result['利润率'] = grouped['利润率'].mean()
    result['记录数'] = grouped.size()
    return result.reset_index(), prepared, invalid
