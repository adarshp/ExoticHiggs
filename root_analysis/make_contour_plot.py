import matplotlib
import numpy as np

matplotlib.use('pgf')
from matplotlib import pyplot as plt
import pandas as pd

matplotlib.style.use('ggplot')

figwidth = 6
# plt.rcParams['figure.figsize'] = (figwidth,figwidth/1.618)
plt.rcParams['figure.figsize'] = (figwidth,figwidth*0.75)
plt.rcParams['font.family'] = "serif"
plt.rcParams["axes.axisbelow"] = False

def get_XYZ_grid(df, res):
    df = df.replace('None',0)
    x = df['mC']
    y = df['mH']
    z = df['bdt_significance']

    xmin, xmax = min(df['mC']), max(df['mC'])
    ymin, ymax = min(df['mH']), max(df['mH'])
    resX = res; resY = res
    xi = np.linspace(xmin, xmax, resX)
    yi = np.linspace(ymin, ymax, resY)
    X, Y = np.meshgrid(xi, yi)
    Z = matplotlib.mlab.griddata(x,y,z,xi,yi, interp='linear')
    return X,Y,Z

def make_contour_plot(filename, res):
    df = pd.read_table(filename, delim_whitespace=True)
    X, Y, Z = get_XYZ_grid(df, res)
    fig, ax = plt.subplots()
    meshplot = ax.pcolormesh(X, Y, Z, cmap='viridis')
    ax.grid(True, color='white', lw=1)
    ax.set_axisbelow(True)
    fig.colorbar(meshplot, ax=ax)
    CS = ax.contour(X, Y, Z, levels = [1.96, 5], colors='yellow')

    fmt = {}
    fmt[CS.levels[0]] = r'1.96$\sigma$'
    fmt[CS.levels[1]] = r'5$\sigma$'

    manual_locations = [(1500,1000),(2700, 2000)]

    plt.clabel(CS, inline=1, colors='white', fontsize=11, fmt=fmt,
        manual=manual_locations)

    xmin, xmax = min(df['mC']), max(df['mC'])
    ymin, ymax = min(df['mH']), max(df['mH'])
    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)

    x = np.arange(0,xmax, 0.1) 
    plt.plot(x,x,color = 'gray', linestyle = 'dashed', linewidth=1.0)
    plt.text(800, 1250, r"$m_{H^\pm} = m_H$", fontsize=10,rotation = 45)

    plt.xlabel('$m_H^\pm$ (GeV)', fontsize=11)
    plt.ylabel('$m_H$ (GeV)', fontsize=11)

    plt.tight_layout()
    plt.savefig('plots/C_HW_tataW.pdf')

if __name__ == '__main__':
    make_contour_plot('significances.txt', 25)
