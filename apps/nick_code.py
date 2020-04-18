def mode_function(energy, cal_a, regions, window=50, bins=150):
    energies = []
    modes = []
    errors = []
    for region in regions:
        sub_regions = list(range(region[0], region[1], window))
        for e_value in sub_regions[:-1]:
            n, bin_edges = np.histogram(cal_a[(energy > e_value) & (energy < e_value+window)], bins=bins)
            bin_centers = (bin_edges[1:] + bin_edges[:-1]) / 2
            max_bin = max(n)
            max_bin_loc = bin_centers[np.where(n == max_bin)[0]][0]
            centroid_energy_bins = bin_centers[n > max_bin/3]
            centroid_bin_heights = n[n > max_bin/3]
            factor = 4
            while((len(centroid_bin_heights) < 50) & (factor < 50)):
                centroid_energy_bins = bin_centers[n > max_bin/factor]
                centroid_bin_heights = n[n > max_bin/factor]
                factor = factor + 1
            try:
                coeffs, cov = curve_fit(gaussian, centroid_energy_bins, centroid_bin_heights, [max_bin, max_bin_loc, 0.05])
                centroid_mode = coeffs[1]
                energies.append((2*e_value+window)/2)
                modes.append(centroid_mode)
                errors.append(np.sqrt(np.diag(cov))[1])
            except (RuntimeError, TypeError):
                pass
    return np.array(energies), np.array(modes), np.array(errors) 
