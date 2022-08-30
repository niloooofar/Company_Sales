def get_quantile(arr, r1, r2, r3):
    if arr <= r1:
        return 1
    elif arr <= r2:
        return 2
    elif arr <= r3:
        return 3
    else:
        return 4
