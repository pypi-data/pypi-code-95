def marginal(ve, h, t, ellip):
    return (((ve[:h] + [ellip] + ve[-t:]) if ellip else (ve[:h] + ve[-t:]))
            if t
            else ve[:h]) if h else ((([ellip] + ve[-t:]) if ellip else ve[-t:])
                                    if t
                                    else [])
