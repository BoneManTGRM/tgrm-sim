import argparse, random
from dataclasses import dataclass, asdict
from typing import Tuple

@dataclass
class Params:
    n: int = 1000
    err: float = 0.2
    fix_cost: int = 5
    m_cost: int = 1
    tau: float = 0.6
    e_max: int = 1000
    seed: int = 42
    repeats: int = 1

def std_pipeline(p: Params, rng: random.Random) -> int:
    return sum(p.fix_cost for _ in range(p.n) if rng.random() < p.err)

def tgrm_pipeline(p: Params, rng: random.Random) -> int:
    total, energy = 0, 0
    for _ in range(p.n):
        if rng.random() < p.err:
            size = rng.uniform(0, 1)
            if size < p.tau and energy < p.e_max:
                total += p.m_cost
                energy += p.m_cost
            else:
                total += p.fix_cost
                energy += 1
    return total

def run_once(p: Params) -> Tuple[int, int, float]:
    std = std_pipeline(p, random.Random(p.seed))
    tgrm = tgrm_pipeline(p, random.Random(p.seed))
    gain = (std - tgrm) / std * 100 if std else 0.0
    return std, tgrm, gain

def run(p: Params) -> dict:
    std_sum = tgrm_sum = gain_sum = 0.0
    for i in range(p.repeats):
        pi = Params(**{**asdict(p), "seed": p.seed + i})
        s, t, g = run_once(pi)
        std_sum += s; tgrm_sum += t; gain_sum += g
    return {"std": std_sum/p.repeats, "tgrm": tgrm_sum/p.repeats,
            "gain_pct": gain_sum/p.repeats, "params": asdict(p)}

def main():
    ap = argparse.ArgumentParser(description="Minimal TGRM micro-repair simulation")
    ap.add_argument("--n", type=int, default=1000)
    ap.add_argument("--err", type=float, default=0.2)
    ap.add_argument("--fix_cost", type=int, default=5)
    ap.add_argument("--m_cost", type=int, default=1)
    ap.add_argument("--tau", type=float, default=0.6)
    ap.add_argument("--e_max", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--repeats", type=int, default=1)
    p = Params(**vars(ap.parse_args()))
    out = run(p)
    print(f"Std: {out['std']:.0f}, TGRM: {out['tgrm']:.0f}, Gain: {out['gain_pct']:.1f}%")

if __name__ == "__main__":
    main()
