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

def make_contour_plot(inputFilename, outputFilename, xlabel, ylabel, zlabel,
        xaxislabel, yaxislabel, res, draw_line, plt_xmin, plt_xmax, plt_ymin,
        plt_ymax):

    df = pd.read_table(inputFilename, delim_whitespace=True)
    df['deltaM'] = df['mC']-df['mH']

    df = df.replace('None',0)
    x, y, z = df[xlabel], df[ylabel], df[zlabel]
    xmin, xmax = min(df[xlabel]), max(df[xlabel])
    ymin, ymax = min(df[ylabel]), max(df[ylabel])
    resX = res; resY = res
    xi = np.linspace(xmin, xmax, resX)
    yi = np.linspace(ymin, ymax, resY)
    X, Y = np.meshgrid(xi, yi)
    Z = matplotlib.mlab.griddata(x,y,z,xi,yi, interp='linear')

    fig, ax = plt.subplots()
    meshplot = ax.pcolormesh(X, Y, Z, cmap='viridis')
    ax.grid(True, color='white', lw=1)
    ax.set_axisbelow(True)
    fig.colorbar(meshplot, ax=ax)
    CS = ax.contour(X, Y, Z, colors='yellow')

    # fmt = {}
    # fmt[CS.levels[0]] = r'1.96$\sigma$'
    # fmt[CS.levels[1]] = r'5$\sigma$'

    # manual_locations = [(1500,1000),(2700, 2000)]

    ax.clabel(CS, inline=1, colors='white', fontsize=11)

    ax.set_xlim(xmin, plt_xmax)
    ax.set_ylim(ymin, plt_ymax)

    if draw_line:
        x = np.arange(0,xmax, 0.1)
        ax.plot(x,x,color = 'gray', linestyle = 'dashed', linewidth=1.0)
        ax.text(800, 1250, r"$m_{H^\pm} = m_H$", fontsize=10,rotation = 45)

    ax.set_xlabel(xaxislabel, fontsize=11)
    ax.set_ylabel(yaxislabel, fontsize=11)

    plt.tight_layout()
    plt.savefig('plots/'+outputFilename)

if __name__ == '__main__':
    make_contour_plot('C_HW_tataW_significances.txt', 'C_HW_tataW_mC_mH.pdf',
                      'mC', 'mH', 'bdt_significance', '$m_H^\pm$ (GeV)',
                      '$m_H$ (GeV)', 50, True, 0, 2000, 0, 1000)

    make_contour_plot('C_HW_tataW_fixed_deltaM_significances.txt',
                      'C_HW_tataW_mC_tb.pdf', 'mC', 'tb', 'bdt_significance',
                      '$m_H^\pm$ (GeV)', '$\\tan\\beta', 25, False, 0, 2000, 1,
                      50)

