from engine2 import *
BASE = dict(wave=-53, rsi=40, stretch=2.0, btcd=True, guard=True, cycle_exit=True, pullback=False, pb_wave=-30, pb_rsi=45, tp="std")
CFGS = []
def v(**k): c = dict(BASE); c.update(k); CFGS.append(c)
v()                                                     # current crypto rules
for tp in ("std", "mid", "fast"):
    for wave, rsi_, st in [(-53, 40, 2.0), (-45, 45, 1.5), (-40, 45, 1.0), (-35, 50, 1.0)]:
        v(wave=wave, rsi=rsi_, stretch=st, tp=tp)
        v(wave=wave, rsi=rsi_, stretch=st, tp=tp, pullback=True)
        v(wave=wave, rsi=rsi_, stretch=st, tp=tp, pullback=True, pb_wave=-20, pb_rsi=50)
if __name__ == "__main__":
    with mp.Pool(4) as p: rows = p.map(run, CFGS)
    R = pd.DataFrame(rows); R.to_csv("grid2.csv", index=False)
    pd.set_option("display.width", 320); pd.set_option("display.max_rows", 200)
    cols = ["wave", "rsi", "stretch", "pullback", "pb_wave", "pb_rsi", "tp", "IS_per_yr", "IS_pf", "IS_avg%", "IS_p10%", "IS_worst%", "OOS_per_yr", "OOS_pf", "OOS_avg%", "OOS_p10%", "OOS_worst%", "OOS_win", "OOS_hold"]
    print(R[cols].to_string(index=False))
