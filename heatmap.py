import numpy as np
import matplotlib.pyplot as plt

def heatmap(points):

    fig, ax = plt.subplots()

    if not points:
        ax.text(0.5, 0.5, "No data", ha="center", va="center")
        ax.axis("off")
        return fig

    grid = np.zeros((60, 60))

    for x, y in points:

        gx = int((x / 640) * 60)
        gy = int((y / 360) * 60)

        gx = max(0, min(59, gx))
        gy = max(0, min(59, gy))

        grid[gy][gx] += 1

    ax.imshow(grid, cmap="hot")
    ax.axis("off")

    return fig