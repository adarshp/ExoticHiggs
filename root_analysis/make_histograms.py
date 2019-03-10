from tqdm import tqdm
import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot as plt

colors = {
    'tttautau-full':'DarkBlue',
    'tttautau-semi':'Maroon',
    'ttlv-full':'Gray',
    'ttll-full':'Teal',
}

plt.style.use('ggplot')

def get_xsection(process):
    with open("../"+process+"_events/run_01/run_01_tag_1_banner.txt", 'r') as f:
        for line in f:
            if "pb" in line:
                original_xsection = float(line.split()[-1])*1000
                break
    cut_table = pd.read_table(process+"/cuts.txt", index_col="Cut Name") 
    n_events_after_cuts = cut_table.loc['OS tau jet']['MC Events']
    original_events = cut_table.loc["Initial"]['MC Events']
    efficiency = float(n_events_after_cuts)/original_events
    return efficiency*original_xsection

def make_histo(histo_name):
    fig, ax = plt.subplots()
    for p in [
        'tttautau-full',
        'tttautau-semi',
        'ttll-full',
        'ttlv-full',
    ]:
        df = pd.read_table(p+'/histo_data/'+histo_name+'.txt')
        ax.bar(
                df['Bin Low Edge'][1:],
                get_xsection(p)*df['Bin Entries'][1:]/sum(df['Bin Entries']),
                width=df['Bin Width'][1:],
                align='edge',
                label=p,
                color = colors[p],
                edgecolor=colors[p],
                alpha = 0.4,
                linewidth=0,
                log=True
            )

    ax.set_xlim(0, 500)
    ax.legend()
    ax.set_xlabel(r"$m_{\tau\tau}$"+" (GeV)")
    ax.set_ylabel("Cross section (fb)")
    plt.savefig('histos/'+histo_name+'.pdf')

if __name__ == '__main__':
    for histo_name in ['m_tautau']:
        make_histo(histo_name)
