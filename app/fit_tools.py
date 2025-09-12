from scipy.optimize import curve_fit
import numpy as np

def gaussian(x, A, mu, sigma):
    return A * np.exp(-(x - mu)**2/(2*sigma**2))

def fit_gaussian_zone(bin_centers, counts, bin_widths):
    A0 = counts.max()
    mu0 = np.sum(bin_centers*counts)/np.sum(counts)
    sigma0 = np.sqrt(np.sum(counts*(bin_centers - mu0)**2)/np.sum(counts))
    popt, _ = curve_fit(gaussian, bin_centers, counts, p0=[A0, mu0, sigma0], maxfev=5000)

    expected = gaussian(bin_centers, *popt)
    chi2 = np.sum((counts - expected)**2 / (expected + 1e-6))
    ndf = len(counts) - 3
    chi2_ndf = chi2 / ndf if ndf > 0 else np.nan
    integral = np.sum(expected * bin_widths)
    return popt, chi2_ndf, integral
