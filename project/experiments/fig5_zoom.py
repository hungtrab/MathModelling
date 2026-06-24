"""Reproduce Fig. 5: enlargements of Fig. 4 for G in [0, 0.5]."""

from experiments.fig4_tour_time import run

if __name__ == "__main__":
    run(G_min=0.0, G_max=0.5, n_G=501, xlim=(0.0, 0.5),
        out_name="fig5_zoom.png")
