import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot as plt

colors = {
    'ditop_signal':'DarkBlue',
    'Signal':'DarkBlue',
    'tt_fully_leptonic_including_taus':'Maroon',
    'tt_semileptonic_including_taus':'DarkGreen',
    'tttautau':'Yellow',
}

plt.style.use('ggplot')

def make_histo(histo_name):
    fig, ax = plt.subplots()
    for p in [
        # 'tt_fully_leptonic_including_taus',
        # 'tt_semileptonic_including_taus',
        'tttautau',
        'Signal'
    ]:
        df = pd.read_table(p+'/histo_data/'+histo_name+'.txt')
        ax.bar(
                df['Bin Low Edge'][1:],
                df['Bin Entries'][1:]/sum(df['Bin Entries']),
                width=df['Bin Width'][1:],
                align='edge',
                label=p,
                color = colors[p],
                alpha = 0.6
            )

    ax.legend()
    ax.set_xlabel(histo_name)
    plt.savefig('histos/'+histo_name+'.pdf')

if __name__ == '__main__':
    for histo_name in [ 'MET', 'pt_l1', 'pt_b1', 'pt_tau', 'm_H', 'm_cH' ]:
        make_histo(histo_name)
