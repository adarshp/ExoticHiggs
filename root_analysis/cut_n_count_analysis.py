from math import sqrt
import pandas as pd
df = pd.read_table('cut_flow_table.txt')
L = 3000 # Integrated luminosity in inverse femtobarns
original_signal_xsection = 11.9669505115 # femtobarns

tt_semi_xsection = 8271000.0000 # femtobarns
tt_full_xsection = 2490390.7403 # femtobarns

df['tt fully-leptonic MC Events'].replace(0,3, inplace=True)
df['tt semi-leptonic MC Events'].replace(0,3, inplace=True)

df['$\sigma_{Signal}$'] = original_signal_xsection*df['Signal MC Events']/df['Signal MC Events'][0] 

df['$\sigma_{tt-semi}$'] = tt_semi_xsection*df['tt semi-leptonic MC Events']/df['tt semi-leptonic MC Events'][0] 
df['$\sigma_{tt-full}$'] = tt_full_xsection*df['tt fully-leptonic MC Events']/df['tt fully-leptonic MC Events'][0] 

df['$\sigma_{BG}$'] = df['$\sigma_{tt-full}$'] + df['$\sigma_{tt-semi}$']

df['S/B'] = df['$\sigma_{Signal}$']/df['$\sigma_{BG}$']

df['$S/\sqrt{B}$'] = df['S/B']*sqrt(L)

pd.set_option('display.width', 1000)

def myFormatter(x):
    if x < 0.001: return '%.1e' % x
    if x < 0.01: return '%.3f' % x
    if x < 1: return '%.2f' % x
    if x < 10: return '%.1f' % x
    else: return '{:,.0f}'.format(x)

with open('cut_flow_latex_table_mc_events.tex', 'w') as f:
    df.to_latex(f,
    columns = ['Cut Name', 'Signal MC Events',
    'tt fully-leptonic MC Events',
    'tt semi-leptonic MC Events'], 
    index = False 
    )

with open('cut_flow_latex_table.tex', 'w') as f:
    df.to_latex(f, escape = False,  float_format = myFormatter,
        columns = ['Cut Name', '$\sigma_{Signal}$',
    '$\sigma_{tt-full}$','$\sigma_{tt-semi}$',
    'S/B', '$S/\sqrt{B}$'], index = False)
