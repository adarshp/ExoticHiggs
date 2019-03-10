import matplotlib
import numpy as np

matplotlib.use("pgf")
from matplotlib import pyplot as plt
import pandas as pd

matplotlib.style.use("ggplot")

figwidth = 6
# plt.rcParams['figure.figsize'] = (figwidth,figwidth/1.618)
plt.rcParams["figure.figsize"] = (figwidth, figwidth * 0.75)
plt.rcParams["font.family"] = "serif"
plt.rcParams["axes.axisbelow"] = False


def make_contour_plot(
    inputFilename,
    outputFilename,
    xlabel,
    ylabel,
    xaxislabel,
    yaxislabel,
    draw_line,
    plt_xmin,
    plt_xmax,
    plt_ymin,
    plt_ymax,
    meshplot = False,
):

    df = pd.read_table(inputFilename, delim_whitespace=True)
    df["deltaM"] = df["mC"] - df["mH"]

    df = df.replace("None", 0)
    x, y = df[xlabel], df[ylabel]
    zd = df["Zd"]
    ze = df["Ze"]

    xmin, xmax = plt_xmin, plt_xmax
    ymin, ymax = plt_ymin, plt_ymax

    # xmin, xmax = min(df[xlabel]), max(df[xlabel])
    # ymin, ymax = min(df[ylabel]), max(df[ylabel])
    resX = 100
    resY = 100
    # resX = (xmax - xmin) / len(set(x))
    # resY = (ymax - ymin) / len(set(y))
    xi = np.linspace(xmin, xmax, resX)
    yi = np.linspace(ymin, ymax, resY)
    X, Y = np.meshgrid(xi, yi)
    Zd = matplotlib.mlab.griddata(x, y, zd, xi, yi, interp="linear")
    Ze = matplotlib.mlab.griddata(x, y, ze, xi, yi, interp="linear")

    fig, ax = plt.subplots()
    if meshplot:
        meshplot = ax.pcolormesh(X, Y, Ze, cmap='viridis', vmin = 0, vmax = 2)
        clb = fig.colorbar(meshplot, ax=ax)
        clb.ax.set_title('$Z_e$')

    ax.grid(True, color="white", lw=1)
    ax.set_axisbelow(True)
    CS_d = ax.contour(X, Y, Zd, levels=[5])
    CS_e = ax.contour(X, Y, Ze, levels=[1.64])

    fmt_dict = lambda CS: {l: f"${l}\sigma$" for l in CS.levels}
    ax.clabel(CS_e, inline=1, fontsize=11, fmt=fmt_dict(CS_e))
    ax.clabel(CS_d, inline=1, fontsize=11, fmt=fmt_dict(CS_d))

    if not plt_xmax:
        plt_xmax = xmax
    if not plt_ymax:
        plt_ymax = ymax
    if not plt_xmin:
        plt_xmin = xmin
    if not plt_ymin:
        plt_ymin = ymin
    ax.set_xlim(plt_xmin, plt_xmax)
    ax.set_ylim(plt_ymin, plt_ymax)

    if draw_line:
        x = np.arange(0, xmax, 0.1)
        ax.plot(x, x, color="gray", linestyle="dashed", linewidth=1.0)
        ax.text(800, 1250, r"$m_{H^\pm} = m_H$", fontsize=10, rotation=45)

    ax.set_xlabel(xaxislabel, fontsize=11)
    ax.set_ylabel(yaxislabel, fontsize=11)

    plt.tight_layout()
    plt.savefig("plots/" + outputFilename)

def make_mC_mH_plot():
    make_contour_plot(
        "C_HW_tataW_mC_mH_significances.txt",
        "C_HW_tataW_mC_mH.pdf",
        "mC",
        "mH",
        "$m_H^\pm$ (GeV)",
        "$m_H$ (GeV)",
        True,
        400,
        2000,
        200,
        600,
        True,
    )
def make_mC_tb_plot():
    make_contour_plot(
        "C_HW_tataW_mC_tb_significances.txt",
        "C_HW_tataW_mC_tb.pdf",
        "mC",
        "tb",
        "$m_H^\pm$ (GeV)",
        "$\\tan\\beta",
        False,
        400,
        2000,
        1,
        50,
        True,
    )

def make_mC_deltaM_plot():
    make_contour_plot(
        "C_HW_tataW_mC_mH_significances.txt",
        # "C_HW_tataW_mC_deltaM_significances.txt",
        "C_HW_tataW_mC_deltaM.pdf",
        "mC",
        "deltaM",
        "$m_H^\pm$ (GeV)",
        "$\Delta M$",
        False,
        800,
        2000,
        100,
        600,
        True,
    )

if __name__ == "__main__":
    make_mC_mH_plot()
    make_mC_tb_plot()
    make_mC_deltaM_plot()
