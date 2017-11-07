from math import sqrt
import pandas as pd
df = pd.read_table('cut_flow_table.txt')
L = 3000 # Integrated luminosity in inverse femtobarns
original_signal_xsection = 11.9669505115 # femtobarns
tt_xsection = 2490390.7403 # femtobarns
df['Background MC Events'].replace(0,3, inplace=True)
df['Signal Cross Section'] = original_signal_xsection*df['Signal MC Events']/df['Signal MC Events'][0] 
df['Background Cross Section'] = tt_xsection*df['Background MC Events']/df['Background MC Events'][0] 
df['S/B'] = df['Signal Cross Section']/df['Background Cross Section']
df['S/sqrt(B)'] = df['S/B']*sqrt(L)
pd.set_option('display.width', 1000)
pd.set_option('precision', 2)
with open('cut_flow_latex_table', 'w') as f:
    df.to_latex(f, columns = ['Cut Name', 'Signal Cross Section',
    'Background Cross Section', 'S/B', 'S/sqrt(B)'], index = False)
print(df)
