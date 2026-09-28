from io import BytesIO
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from data_utils import read_table, sheet_names, aggregate

st.set_page_config(page_title='明析 BI · 经营数据看板', page_icon='📊', layout='wide')
st.markdown('''<style>
.stApp {background:#f5f7fb;color:#18283b}
.block-container {padding-top:2.4rem;max-width:1500px}
h1 {letter-spacing:-1px;font-weight:750!important}
[data-testid="stMetric"] {background:white;border:1px solid #e4e9f2;border-radius:14px;padding:18px 22px}
[data-testid="stSidebar"] {background:#edf1f8}
</style>''', unsafe_allow_html=True)
st.caption('明析 BI / BUSINESS INTELLIGENCE')
st.title('让表格，变成经营洞察')
st.write('导入表格，即时查看毛利、利润率与售价的变化。')

demo = pd.DataFrame({'月份': [f'2026-{i:02d}' for i in range(1, 13)],
                     '毛利': [12500,14800,13900,18200,21600,19800,24800,27500,25200,31200,34600,38200],
                     '售价': [169,172,168,185,199,192,205,215,209,229,239,249],
                     '利润率': [0.21,0.235,0.22,0.25,0.28,0.26,0.295,0.31,0.29,0.325,0.34,0.36]})

with st.sidebar:
    st.header('数据工作台')
    upload = st.file_uploader('上传表格', type=['xlsx','xls','xlsm','csv','tsv','txt','ods'])
    st.caption('文件在本机解析。支持单个文件、多工作表选择，最大 200 MB。')
    header = int(st.number_input('表头所在行', min_value=1, max_value=100, value=1)) - 1

try:
    if upload:
        raw = upload.getvalue()
        sheets = sheet_names(raw, upload.name)
        sheet = st.sidebar.selectbox('工作表', sheets) if sheets else 0
        frame = read_table(raw, upload.name, sheet, header)
        source = upload.name
    else:
        frame = demo.copy()
        source = '演示数据 · 非真实经营数据'
except Exception as exc:
    st.error(f'读取失败：{exc}')
    st.info('请检查格式、表头行和工作表；加密文件需要先解除密码。Excel 公式需要在表格软件中计算并保存。')
    st.stop()

frame = frame.dropna(how='all').copy()
frame.columns = [str(c) for c in frame.columns]
if frame.empty or len(frame.columns) < 4:
    st.warning('需要至少一行数据，以及维度、毛利、售价、利润率四列。')
    st.stop()
columns = list(frame.columns)

def guess(aliases):
    for alias in aliases:
        for i, col in enumerate(columns):
            if col.strip().lower() == alias:
                return i
    for alias in aliases:
        for i, col in enumerate(columns):
            if alias in col.lower():
                return i
    return 0

with st.sidebar:
    st.divider()
    st.subheader('字段映射')
    dimension = st.selectbox('分析维度', columns, index=guess(['月份','日期','产品','商品','month','date']))
    mapping = {}
    for label, aliases in [('毛利',['毛利','毛利额','gross profit']),('售价',['售价','销售单价','单价','price']),('利润率',['利润率','毛利率','margin'])]:
        mapping[label] = st.selectbox(label, columns, index=guess(aliases))
    scale = st.selectbox('无 % 符号的利润率数值', ['小数（0.25 = 25%）','整数（25 = 25%）'])
    profit_mode = st.radio('毛利分组口径', ['合计','平均值'], horizontal=True)
    st.caption('每行是毛利金额时选合计；每行是单件毛利时可选平均值。售价和利润率采用简单平均。')

if len(set([dimension, *mapping.values()])) != 4:
    st.warning('请在左侧为维度、毛利、售价和利润率选择不同的列。')
    st.stop()

st.caption(f'当前数据：{source} · {len(frame):,} 条记录')
with st.expander('筛选数据', expanded=False):
    filter_column = st.selectbox('筛选字段', ['不筛选', *columns])
    if filter_column != '不筛选':
        values = frame[filter_column].fillna('（空白）').astype(str)
        selected = st.multiselect('保留的值（留空表示全部）', list(values.unique()))
        if selected:
            frame = frame[values.isin(selected)]
if frame.empty:
    st.warning('筛选后没有数据。')
    st.stop()
summary, prepared, invalid = aggregate(frame, dimension, mapping, scale, profit_mode)
missing = [f'{k} {v} 条' for k,v in invalid.items() if v]
if missing:
    st.warning('空白或无法识别的数字已按缺失值处理，未填零：' + '、'.join(missing))
if any(prepared[c].notna().sum() == 0 for c in mapping):
    st.error('至少一个指标没有有效数值，请检查字段映射和源数据。')
    st.stop()

c1,c2,c3,c4 = st.columns(4)
profit = prepared['毛利'].sum(min_count=1) if profit_mode == '合计' else prepared['毛利'].mean()
c1.metric(f'毛利 · {profit_mode}', f'{profit:,.2f}')
c2.metric('平均利润率', f'{prepared["利润率"].mean():.2%}')
c3.metric('平均售价', f'{prepared["售价"].mean():,.2f}')
c4.metric('分析分组', f'{len(summary):,}', help=f'当前筛选包含 {len(frame)} 条原始记录')
st.write('')
left,right = st.columns([3,2])
with left:
    st.subheader('经营指标趋势')
with right:
    mode = st.selectbox('组合方式', ['毛利柱状 + 售价折线 + 利润率折线','毛利与售价柱状 + 利润率折线'], label_visibility='collapsed')
sort = st.selectbox('排序', ['源数据顺序','维度升序','毛利降序','利润率降序'])
if sort != '源数据顺序':
    key = {'维度升序':'维度','毛利降序':'毛利','利润率降序':'利润率'}[sort]
    summary = summary.sort_values(key, ascending=sort == '维度升序', kind='stable')
limit = st.slider('图表最多展示分组数', 5, 200, 30, 5)
shown = summary.head(limit)
fig = make_subplots(specs=[[{'secondary_y': True}]])
fig.add_trace(go.Bar(name='毛利', x=shown['维度'], y=shown['毛利'], marker_color='#4f68e8'), secondary_y=False)
price_args = dict(name='售价', x=shown['维度'], y=shown['售价'])
fig.add_trace(go.Scatter(**price_args, mode='lines+markers', line=dict(color='#12a394',width=3)) if mode.startswith('毛利柱状') else go.Bar(**price_args,marker_color='#12a394'), secondary_y=False)
fig.add_trace(go.Scatter(name='利润率',x=shown['维度'],y=shown['利润率'], mode='lines+markers',line=dict(color='#f4a340',width=3),hovertemplate='%{y:.2%}<extra>利润率</extra>'), secondary_y=True)
fig.update_layout(height=480, paper_bgcolor='white', plot_bgcolor='white', margin=dict(l=25,r=25,t=40,b=35), legend=dict(orientation='h',y=1.12,x=0), hovermode='x unified',barmode='group',font=dict(family='Arial, sans-serif',color='#40516b'))
fig.update_xaxes(title=dimension,type='category',showgrid=False)
fig.update_yaxes(title_text='金额（源数据单位）',gridcolor='#edf0f6',secondary_y=False)
fig.update_yaxes(title_text='利润率',tickformat='.0%',showgrid=False,secondary_y=True)
st.plotly_chart(fig, use_container_width=True, config={'displaylogo':False,'toImageButtonOptions':{'filename':'经营指标组合图','scale':2}})
st.caption(f'图表展示 {len(shown)} / {len(summary)} 个分组；指标卡与明细包含全部筛选结果。点击图例可隐藏指标，便于查看量级较小的售价。')
st.info('统计口径：售价、利润率均为有效记录的简单平均，利润率不求和；平均利润率不代表按收入加权的整体利润率。金额单位沿用原表，请确保一致。')

tab1,tab2 = st.tabs(['分组汇总','原始数据'])
with tab1:
    st.dataframe(summary, use_container_width=True, hide_index=True, column_config={'利润率':st.column_config.NumberColumn(format='percent')})
with tab2:
    st.dataframe(frame, use_container_width=True, hide_index=True)
d1,d2,d3 = st.columns(3)
d1.download_button('↓ 下载汇总 CSV', summary.to_csv(index=False).encode('utf-8-sig'), 'BI汇总.csv','text/csv')
d2.download_button('↓ 下载交互图表 HTML', fig.to_html(include_plotlyjs=True).encode('utf-8'), 'BI组合图.html','text/html')
d3.download_button('↓ 下载示例 CSV', demo.to_csv(index=False).encode('utf-8-sig'), '示例数据.csv','text/csv')
