import numpy as np


def _clean_ping_time(ping_time_old, local_win_len=100):
    ping_time_old_diff = np.diff(ping_time_old)
    neg_idx = np.argwhere(ping_time_old_diff < np.timedelta64(0, 'ns'))  # indices with negative diff
    if neg_idx.size !=0:
        ni = neg_idx[0][0]
        local_win = np.arange(-local_win_len, local_win_len)
        local_pt_diff = ping_time_old_diff[ni + local_win]
        local_pt_median = np.median(np.delete(local_pt_diff, local_win_len))  # median after removing negative element
        ping_time_new = np.hstack((
            ping_time_old[:ni + 1],
            ping_time_old[ni] + np.cumsum(
                np.hstack((local_pt_median, ping_time_old_diff[(ni + 1):]))
            )
        ))
        return _clean_ping_time(ping_time_new, local_win_len=local_win_len)
    else:
        return ping_time_old  # no negative diff


def coerce_increasing_ping_time(ds, local_win_len=100):
    """Coerce ``ping_time`` to always flow forward.

    This is to correct for problems sometimes observed in EK60 data
    where ``ping_time`` would suddenly go backward for one ping
    but with the rest of the pinging interval undisturbed.

    Parameters
    ----------
    ds : xr.Dataset
        a dataset with a ``ping_time`` dimension/coordinate
    local_win_len : int
        half length of the local window within which the median pinging interval
        is used to infer the correct next ping time

    Returns
    -------
    the input dataset but with ``ping_time`` coerced to flow forward
    """
    ds['ping_time'] = _clean_ping_time(ds['ping_time'].values, local_win_len=local_win_len)
    return ds
