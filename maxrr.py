# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 03:17:46 2024

@author: 82108
"""

import numpy as np

def max_rr(CAD, p, window_half_width):
    """
    Finds the maximum rate of rise (rr) of the "p" vector and the corresponding
    value of the "CAD" vector using a two-point derivative approximation.

    Parameters:
        CAD (array-like): Crank angle degree (CAD) vector.
        p (array-like): Pressure vector.
        window_half_width (int): Half-width of the window for derivative approximation.

    Returns:
        rr (float): Maximum rate of rise of pressure.
        aorr (float): Corresponding CAD value at maximum rate of rise.
    """
    CAD = np.array(CAD)
    p = np.array(p)

    # Ensure input dimensions are correct
    if CAD.ndim != 1 or p.ndim != 1:
        raise ValueError("CAD and p must be 1D arrays.")
    if len(CAD) != len(p):
        raise ValueError("CAD and p must have the same length.")

    rr_values = []
    CAD_rr = []

    for index in range(window_half_width, len(CAD) - window_half_width):
        dp = p[index + window_half_width] - p[index - window_half_width]
        dCAD = CAD[index + window_half_width] - CAD[index - window_half_width]
        
        # Avoid negative rates of rise
        if dp < 0:
            rr_values.append(0)
        else:
            rr_values.append(dp / dCAD)
        CAD_rr.append(CAD[index])

    # Find the maximum rate of rise and its corresponding CAD value
    rr_values = np.array(rr_values)
    CAD_rr = np.array(CAD_rr)

    max_rr = np.max(rr_values)
    max_rr_index = np.argmax(rr_values)
    aorr = CAD_rr[max_rr_index]

    return max_rr, aorr

# Example usage (replace with actual data):
CAD = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
p = [1, 2, 4, 7, 11, 16, 22, 29, 37, 46, 56]
window_half_width = 2

rr, aorr = max_rr(CAD, p, window_half_width)
print("Maximum rate of rise (rr):", rr)
print("Corresponding CAD (aorr):", aorr)
