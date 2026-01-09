import pickle
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
from statsmodels.nonparametric.kde import KDEUnivariate


with open("plddt_values.pkl", "rb") as f:
    species_plddt = pickle.load(f)

print("Loaded species:", list(species_plddt.keys()))


def scipy_kde_curve(values, grid):
    kde = gaussian_kde(values)
    return kde.evaluate(grid)

plt.rcParams["figure.figsize"] = (10, 6)

# Create grid for KDE
all_values = np.concatenate([vals for vals in species_plddt.values() if len(vals) > 0])
grid = np.linspace(min(all_values), max(all_values), 400)


# FIGURE 1 — Histogram 
plt.figure()
for species, values in species_plddt.items():
    plt.hist(values, bins=40, histtype="step", density=True, label=species)

plt.title("pLDDT Histogram (All Species)")
plt.xlabel("Mean pLDDT")
plt.ylabel("Density")
plt.legend()
plt.tight_layout()
plt.savefig("plddt_hist_all_species.png", dpi=300)
plt.close()


# FIGURE 2 — StatsModels KDE 
plt.figure()
for species, values in species_plddt.items():
    kde = KDEUnivariate(values)
    kde.fit(bw="scott")
    plt.plot(kde.support, kde.density, label=species)

plt.title("pLDDT Density (StatsModels KDE)")
plt.xlabel("Mean pLDDT")
plt.ylabel("Density")
plt.legend()
plt.tight_layout()
plt.savefig("plddt_density_statsmodels_all_species.png", dpi=300)
plt.close()


# FIGURE 3 — SciPy KDE 
plt.figure()
for species, values in species_plddt.items():
    y = scipy_kde_curve(values, grid)
    plt.plot(grid, y, label=species)

plt.title("pLDDT Density (SciPy KDE)")
plt.xlabel("Mean pLDDT")
plt.ylabel("Density")
plt.legend()
plt.tight_layout()
plt.savefig("plddt_density_scipy_all_species.png", dpi=300)
plt.close()

