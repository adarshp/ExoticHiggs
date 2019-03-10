from math import sqrt
import pandas as pd
import subprocess as sp

df = pd.DataFrame()
for p in ['Signal', 'tt_fully_leptonic_including_taus',
    'tt_semileptonic_including_taus', 'tttautau']:
    df_temp = pd.read_table(p+'/cuts.txt')
    df['Cut Name'] = df_temp['Cut Name']
    df[p+ ' MC Events'] = df_temp['MC Events']
L = 3000 # Integrated luminosity in inverse femtobarns

tt_semi_xsection = 8271000.0000 # femtobarns
tt_full_xsection = 2490390.7403 # femtobarns
tttautau_xsection = 95.71

mC = 1016.2776
mH = 725.09
xs_tbC = float(sp.check_output(['./cHtb_xsection', str(mC)]))

BP = pd.read_table('../benchmark_planes/BP_IIB_tb_1.5.txt', delim_whitespace=True)

br_C_HW = BP[BP['mC'] == mC][BP['mH'] == mH]['BR(C>HW)'].tolist()[0]
original_signal_xsection = br_C_HW*xs_tbC

df['tt_fully_leptonic_including_taus MC Events'].replace(0,3, inplace=True)
df['tt_semileptonic_including_taus MC Events'].replace(0,3, inplace=True)
df['tttautau MC Events'].replace(0,3, inplace=True)

# Renaming columns
df['Signal'] = df['Signal MC Events']
df['$tt_{full}$'] = df['tt_fully_leptonic_including_taus MC Events']
df['$tt_{semi}$'] = df['tt_semileptonic_including_taus MC Events']
df['$tt\\tau\\tau$'] = df['tttautau MC Events']

df['$\sigma_{Signal}$'] = original_signal_xsection*df['Signal MC Events']/df['Signal MC Events'][0] 

df['$\sigma_{tt-full}$'] = tt_full_xsection*df['$tt_{full}$']/df['$tt_{full}$'][0] 
df['$\sigma_{tt-semi}$'] = tt_semi_xsection*df['$tt_{semi}$']/df['$tt_{semi}$'][0] 
df['$\sigma_{tt\\tau\\tau}$'] = tttautau_xsection*df['$tt\\tau\\tau$']/df['$tt\\tau\\tau$'][0] 

df['$\sigma_{BG}$'] = sum([df['$\sigma_{tt-full}$'], df['$\sigma_{tt-semi}$'], df[r'$\sigma_{tt\tau\tau}$']])

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
    df.to_latex(f, escape=False,
    columns = ['Cut Name', 'Signal',
        '$tt_{full}$', '$tt_{semi}$', r'$tt\tau\tau$'],
        index = False 
    )

with open('cut_flow_latex_table.tex', 'w') as f:
    df.to_latex(f, escape = False,  float_format = myFormatter,
        columns = ['Cut Name', '$\sigma_{Signal}$',
    '$\sigma_{tt-full}$','$\sigma_{tt-semi}$', r'$\sigma_{tt\tau\tau}$',
    'S/B', '$S/\sqrt{B}$'], index = False)
