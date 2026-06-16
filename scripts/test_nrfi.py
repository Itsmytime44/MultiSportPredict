#!/usr/bin/env python
"""Quick smoke test for the NRFI CLI module."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.nrfi_yrfi_cli import NRFIResult, PitcherSplit, BatterSplit, calc_nrfi_edge

r = NRFIResult(home_team="NYY", away_team="BOS")
r.home_pitcher = PitcherSplit("Gerrit Cole", "NYY", 3.20, 6.5, 14.2, 28.0, 1.2, 6.0)
r.away_pitcher = PitcherSplit("Brayan Bello", "BOS", 4.50, 9.8, 9.5, 20.0, 1.4, 6.0)
r.home_top3_batters = [
    BatterSplit("Aaron Judge", "NYY", 165, 18.2, 0.310, 24),
    BatterSplit("Juan Soto", "NYY", 155, 14.0, 0.280, 18),
    BatterSplit("Giancarlo Stanton", "NYY", 130, 16.5, 0.260, 28),
]
r.away_top3_batters = [
    BatterSplit("Rafael Devers", "BOS", 145, 15.0, 0.270, 20),
    BatterSplit("Wilyer Abreu", "BOS", 112, 10.2, 0.190, 22),
    BatterSplit("Triston Casas", "BOS", 128, 12.8, 0.230, 25.5),
]
r.park_hr_factor = 1.08
r.market_nrfi_price = -115

r = calc_nrfi_edge(r)

print("=" * 60)
print("NRFI / YRFI TEST: BOS @ NYY")
print("=" * 60)
print(f"  Lean:          {r.lean}")
print(f"  Confidence:    {r.model_prob:.1f}%")
print(f"  Market NRFI:   {r.market_nrfi_price:+,d}")
print(f"  Park HR:       {r.park_hr_factor:.2f}")
print()
print("  Pitchers (1st-inning splits):")
print(f"    BOS  xFIP={r.away_pitcher.xfip_1st:.2f}  BB%={r.away_pitcher.bb_pct_1st:.1f}  SwStr%={r.away_pitcher.swstr_pct:.1f}  K%={r.away_pitcher.k_pct:.1f}")
print(f"    NYY  xFIP={r.home_pitcher.xfip_1st:.2f}  BB%={r.home_pitcher.bb_pct_1st:.1f}  SwStr%={r.home_pitcher.swstr_pct:.1f}  K%={r.home_pitcher.k_pct:.1f}")
print()
print("  Top-3 Batters wRC+:")
print(f"    BOS: {[b.wrc_plus for b in r.away_top3_batters]}")
print(f"    NYY: {[b.wrc_plus for b in r.home_top3_batters]}")
print()
print(f"  Summary: {r.summary}")
print("=" * 60)

# Verify rich display
try:
    from scripts.nrfi_yrfi_cli import print_result
    print_result(r)
except Exception as e:
    print(f"Rich display skipped: {e}")

sys.exit(0 if r.lean != "PASS" else 0)