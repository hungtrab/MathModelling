# Derivation of the dimensionless map (Eq. 5)

Starting from the dimensional bus equation in the paper:

$$
t_i(m+1) = t_i(m) + (\gamma + \eta) B_i(m) + \frac{2L}{V_i(m)},
\quad i = 1, \dots, M.
$$

with passenger count `B_i(m) = W_i(m) = μ (t_i(m) − t_{i'}(m'))` and bus
velocity `V_i(m) = V_0 + s_i (γ + η) B_i(m)`, substituting yields

$$
t_i(m+1) = t_i(m) + \mu(\gamma+\eta)\,(t_i(m) - t_{i'}(m'))
   + \frac{2L}{V_0 + s_i\,\mu(\gamma+\eta)\,(t_i(m) - t_{i'}(m'))}.
$$

Non-dimensionalise by

$$
T_i \equiv t_i \cdot \frac{V_0}{2L},
\qquad G \equiv \mu(\gamma+\eta),
\qquad S_i \equiv s_i \mu(\gamma+\eta) \cdot \frac{2L}{V_0^2}.
$$

The result is the map used throughout the code:

$$
T_i(m+1) = T_i(m) + G \cdot H_i(m) + \frac{1}{1 + S_i \cdot H_i(m)},
\quad H_i(m) \equiv T_i(m) - T_{i'}(m').
$$

## Tour time and headway

* **Tour time** of bus *i* at trip *m*: `ΔT_i(m) ≡ T_i(m+1) − T_i(m) = G·H + 1/(1+S_i·H)`.
* **Time headway** of bus *i* at trip *m*: `H_i(m) ≡ T_i(m) − T_{i'}(m')`.

Because buses overtake each other, the predecessor index `i′` and trip `m′`
are not fixed in advance — they are determined dynamically as the simulation
progresses. The implementation in `simulation.py` solves this with a
chronological event queue (min-heap on `T`).

## Why divergence at G = 2

The fixed point of the map under symmetric initial conditions
(`T_i(m) − T_{i'}(m') ≡ Δ`, all buses identical, `S_1 = S_2 = S`) satisfies

$$
\Delta = G \Delta + \frac{1}{1 + S \Delta} \;\Longleftrightarrow\;
(1 - G)\Delta (1 + S\Delta) = 1.
$$

For `G = 2` this fixed-point equation has no positive real root once
`Δ > 0` — hence the divergence reported in the paper.
