"""Reproduce Fig. 3: enlargements of Fig. 2 panels for G in [0, 0.5]."""

from experiments.fig2_time_headway import run

if __name__ == "__main__":
    run(
        G_min=0.0,
        G_max=0.5,
        n_G=501,
        xlim=(0.0, 0.5),
        out_name="fig3_zoom.png",
    )
