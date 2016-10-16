import pandas as pd

def get_bps(bp_filename):
    df = pd.read_csv(bp_filename, delim_whitespace=True, dtype = 'str')
    return list(df.itertuples(index=False))

BP_IA = get_bps('benchmark_planes/BP_IA.txt')
