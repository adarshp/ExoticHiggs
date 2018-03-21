import matplotlib
import numpy as np

matplotlib.use('pgf')

from matplotlib import pyplot as plt
import pandas as pd

matplotlib.style.use('ggplot')
figwidth = 6.12
plt.rcParams['figure.figsize'] = (figwidth,figwidth*3/4)

def get_XYZ_grid(df, res):
    df = df.replace('None',0)
    x = df['mC']
    y = df['mH']
    z = df['significance']

    xmin, xmax = min(df['mC']), max(df['mC'])
    ymin, ymax = min(df['mH']), max(df['mH'])
    resX = res; resY = res
    xi = np.linspace(0, 2500, resX)
    yi = np.linspace(0, 2500, resY)
    X, Y = np.meshgrid(xi, yi)
    Z = matplotlib.mlab.griddata(x,y,z,xi,yi,interp='nn')
    return X,Y,Z

def make_contour_plot(filename, res):
    df = pd.read_table(filename, delim_whitespace=True)
    X, Y, Z = get_XYZ_grid(df, res)
    plt.pcolormesh(X, Y, Z, cmap='viridis', alpha=0.8)
    CS = plt.contour(X, Y, Z, levels = [1.96, 5], cmap='viridis')

    fmt = {}
    fmt[CS.levels[0]] = r'1.96$\sigma$'
    fmt[CS.levels[1]] = r'5$\sigma$'

    manual_locations = [(1500,1000),(2100, 1300)]

    plt.clabel(CS, inline=1, colors='white', fontsize=13, fmt=fmt,
        manual=manual_locations)

    xmin, xmax = min(df['mC']), max(df['mC'])
    ymin, ymax = min(df['mH']), max(df['mH'])
    plt.xlim(xmin, 2500)
    plt.ylim(ymin, 2500)
    plt.xlabel('$m_H^\pm$', fontsize=13)
    plt.ylabel('$m_H$', fontsize=13)
    plt.tight_layout()
    plt.savefig('plots/C_HW_tataW.pgf')

if __name__ == '__main__':
    make_contour_plot('significances.txt', 100)
