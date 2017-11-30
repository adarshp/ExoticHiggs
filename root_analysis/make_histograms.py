import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot as plt
colors = {
    'Signal':'DarkBlue',
    'tt_full':'Maroon',
    'tt_semi':'DarkGreen',
}

plt.style.use('ggplot')

def make_histo(histo_name):
    fig, ax = plt.subplots()
    for p in ['tt_full', 'tt_semi', 'Signal']:
        df = pd.read_table(p+'/histo_data/'+histo_name+'.txt')
        ax.bar(df['Bin Low Edge'][1:], df['Bin Entries'][1:]/sum(df['Bin Entries']), width=df['Bin Width'][1:],
        align='edge', label=p, color = colors[p], alpha = 0.6)

    ax.legend()
    ax.set_xlabel(histo_name)
    plt.savefig(histo_name+'.pdf')

for histo_name in ['MET', 'pt_l1', 'pt_b1', 'pt_tau', 'w_had']:
    make_histo(histo_name)
