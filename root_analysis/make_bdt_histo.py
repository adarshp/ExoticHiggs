from tqdm import tqdm
import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot as plt
colors = {
    'Signal':'DarkBlue',
    'Background':'Maroon',
}

fig, ax = plt.subplots()
histo_name = "BDT"
for p in ("Signal", "Background"):
    df = pd.read_table(p+'/histo_data/'+p+ " BDT Output.txt")
    ax.bar(
        df['Bin Low Edge'][1:],
        df['Bin Entries'][1:],
        width=df['Bin Width'][1:],
        align='edge',
        label=p,
        color = colors[p],
        edgecolor=colors[p],
        alpha = 0.4,
        linewidth=0,
    )

ax.legend()
ax.set_xlabel("BDT Score")
ax.set_ylabel("Cross section (fb)")
plt.savefig('histos/'+histo_name+'.pdf')
