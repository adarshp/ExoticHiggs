import pandas as pd
import matplotlib
import numpy as np

matplotlib.use('pgf')

from matplotlib import pyplot as plt

plt.rcParams['font.family'] = "serif"
plt.style.use('ggplot')
# df = pd.read_table('../benchmark_planes/BP_IIB_tb_1.5.txt', delim_whitespace=True)
# df = df[df['mH'] == 925.09]
# print(df.columns)
# plt.plot(df['mC'], df['BR(C>HW)'])
# plt.ylabel(r'$BR(H^{\pm}\rightarrow HW^{\pm})$')
# plt.xlabel(r'$m_{H^\pm}$ (GeV)')
# plt.savefig('plots/br_plot.pdf')

def get_XYZ_grid(df, res):
    df = df.replace('None',0)
    x = df['mC']
    y = df['mH']
    z = df['BR(C>HW)']

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
    # meshplot = ax.pcolormesh(X, Y, Z, cmap='viridis')
    # ax.grid(True, color='white', lw=1)
    # ax.set_axisbelow(True)
    # fig.colorbar(meshplot, ax=ax)
    CS = ax.contour(X, Y, Z)

    plt.clabel(CS, inline=1, colors='white', fontsize=11)

    xmin, xmax = min(df['mC']), max(df['mC'])
    ymin, ymax = min(df['mH']), max(df['mH'])
    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)

    # plt.text(1600, 1900, r"$m_{H^\pm} = m_H$", fontsize=10,rotation = 35)

    plt.xlabel('$m_H^\pm$ (GeV)', fontsize=11)
    plt.ylabel('$m_H$ (GeV)', fontsize=11)

    plt.tight_layout()
    plt.savefig('plots/br_plot.pdf')

if __name__ == '__main__':
    make_contour_plot('../benchmark_planes/BP_IIB_tb_1.5.txt', 100)
