import pandas
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy.spatial.qhull import Delaunay

from .sources import ImageSource


savefig_keys = [
    "dpi", "format", "metadata", "bbox_inches", 
    "pad_inches", "facecolor", "edgecolor",
    "backend"
]


def feature_plot(imagefile: str,
                 feat: pandas.DataFrame,
                 tri: Delaunay = None,
                 outputfile: str = None,
                 show=False,
                 **kwargs):

    image = ImageSource().transform(imagefile)

    fig, ax = plt.subplots(1, 1, figsize=(20, 14))

    ax.imshow(image, cmap=plt.cm.Greys_r)

    for i, x in feat.iterrows():
        if x["text"] != x["text"]:
            continue
        if len(x["text"].replace(" ", "")):
            rect = Rectangle(
                        (x["left"], x["top"]), x["width"], x["height"],
                        fill=True, alpha=.2, color="r")
            ax.add_patch(rect)

    if tri is not None:
        ax.triplot(feat["x"], feat["y"],
                    tri.simplices, "--k",
                    alpha=0.5, lw=0.5)

    if show:
        plt.show()

    savefig_kwargs = {}
    for key in list(kwargs):
        if key in savefig_keys:
            savefig_kwargs[key] = kwargs.pop(key)
    
    if outputfile:
        fig.savefig(outputfile, **savefig_kwargs)

    return fig
