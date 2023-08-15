import re
import h5py
import numpy as np
import xarray as xr
import matplotlib
from matplotlib import rc
import matplotlib.pyplot as plt
from tabulate import tabulate
from numpy.linalg import norm
import scipy

# Define Functions
def h5_in_xarray(filepath, field):
    hf = h5py.File(filepath, 'r')
    data = hf.get('%s' % field)
    x1 = hf.get('x-coord')
    x2 = hf.get('y-coord')
    x3 = hf.get('z-coord')
    xr_data = xr.DataArray(
        np.array(data),
        dims = ("x", "y", "z"),
        coords = { "x" : np.array(x1),
                  "y" : np.array(x2),
                  "z" : np.array(x3)
        }   
    )
    return xr_data

def create_xarray(u):
    # This function creates an xarray that has same data size and coordinates aligned with the input xarray u
    new_array = xr.DataArray(
        np.empty(u.shape),
        dims = ("x", "y", "z"),
        coords = { "x" : u['x'],
              "y" : u['y'],
              "z" : u['z']
        }
    )
    
    return new_array

# Import Data
sim_list = [
  "chan_l6_4x12x24_4x4x8.h5",
  "chan_l6_4x12x24_6x6x12.h5",
  "chan_l6_4x12x24_8x8x16.h5"
]


f = {}
field_list = ['u', 'v', 'w', 'uu', 'uv', 'uw', 'vv', 'vw', 'ww']

for sim in sim_list:
  filepath = "/inputs/" + sim
  for field in field_list:
    f['%s%s' % (field, sim[4:-3])] = h5_in_xarray(filepath, field)

# Calculating Temperatuire
var_list = ['uu', 'uv', 'uw', 'vv', 'vw', 'ww']
temp = {}

for sim in sim_list:
  for v in var_list:
    temp["%s%s" % (v, sim[4:-3])] = f["%s%s" % (v, sim[4:-3])].mean(dim = ['x', 'y']) - (f["%s%s" % (v[0], sim[4:-3])] * f["%s%s" % (v[1], sim[4:-3])]).mean(dim = ['x', 'y'])


# Calculating Displacement
disp = {}

for sim in sim_list:
  for v in var_list:
    disp["%s%s" % (v, sim[4:-3])] = (f["%s%s" % (v[0], sim[4:-3])]*f["%s%s" % (v[1], sim[4:-3])]).mean(dim = ['x', 'y']) - f["%s%s" % (v[0], sim[4:-3])].mean(dim = ['x', 'y']) * f["%s%s" % (v[1], sim[4:-3])].mean(dim = ['x', 'y'])


# calculating total stress
stress = {}

for sim in sim_list:
  for v in var_list:
    stress["%s%s" % (v, sim[4:-3])] = temp["%s%s" % (v, sim[4:-3])] + disp["%s%s" % (v, sim[4:-3])]


rc('font',weight='bold',size=15)

fig1, axs = plt.subplots(nrows=1, ncols=3, figsize=(10, 3.5), sharey=True)

pack_den = "l6"
stats_list = ['u', 'uu', 'uw']
for index, stat in enumerate(stats_list):   
    key_list = list(f.keys())
    key_list = [match for match in key_list if pack_den in match and match.startswith("u_")]

    key_list.sort()
    namelist = ['a)', 'b)', 'c)']
    clist = ['r', 'b', 'k']
    for index1, key in enumerate(key_list):
        reso = re.search('.*_(\d+)x(\d+)x(\d+)', key)
        reso = (reso.group(3), reso.group(2), reso.group(1))
        if len(stat) == 2:
            axs[index].plot(stress['%s%s' % (stat, key[1:])], f['%s%s' % (stat, key[1:])]['z'], clist[index1], linewidth=2, label=r'$(%s, %s, %s)$' % (reso[2], reso[1], reso[0]))
        else:
            axs[index].plot(f['%s%s' % (stat, key[1:])].mean(dim=['x', 'y']), f['%s%s' % (stat, key[1:])]['z'], clist[index1], linewidth=2, label=r'$(N_1, N_2, N_3) = (%s, %s, %s)$' % (reso[2], reso[1], reso[0]))
    if index==1:
        plt.text(0.125, 0.9, namelist[index], horizontalalignment='center', transform=axs[index].transAxes,fontsize=15)
    else:
        plt.text(0.1, 0.9, namelist[index], horizontalalignment='center', transform=axs[index].transAxes,fontsize=15)
    axs[index].set_ylim(0, 4)
axs[2].legend(loc='center left', fontsize=12, bbox_to_anchor=(1.0, 0.5))
axs[0].set_xlabel(r'$\langle\overline{u}_1\rangle/u_\tau$', fontsize=15, labelpad=5)
axs[1].set_xlabel(r'$\langle\overline{u_1^\prime u_1^\prime}\rangle/u_\tau^2$', fontsize=15, labelpad=5)
axs[2].set_xlabel(r'$\langle\overline{u_1^\prime u_3^\prime}\rangle/u_\tau^2$', fontsize=15, labelpad=5)
fig1.text(0.065, 0.5, r'$x_3/h$', ha='center', va='center', rotation='horizontal', fontsize=15)
fig1.savefig('/outputs/figure_14.pdf', bbox_inches='tight')
#fig1.show()

# Computing errors for the plot above
def project_to_delta16(ddelta, d16):
    n = d16.size
    z_grid = np.linspace(ddelta['z'][0], ddelta['z'][-1], n)
    vel_intp = ddelta.interp(z = z_grid)
    return vel_intp

def compute_norms_domhimpact(pack_den):
    key_list = list(f.keys())
    key_list = [match for match in key_list if pack_den in match and match.startswith("u_")]
    key_list.sort()
    print(key_list)

    truth = f["%s" % key_list[-1]].mean(dim = ['x', 'y'])
    norms = [[], [], []]
    for index, key in enumerate(key_list[:-1]):
        norms[index].append(key)
        val = f["%s" % key].mean(dim = ['x', 'y'])
        val_intp = project_to_delta16(val, truth)
        error = val_intp.values - truth.values
        l2 = norm(error, ord=2) / norm(truth.values, ord=2)
        norms[index].append("%.4f" % l2)

    print(tabulate(norms, headers=["key", "error"]))
    return None

def compute_norms_domhimpact_stress(pack_den, var):
    key_list = list(f.keys())
    key_list = [match for match in key_list if pack_den in match and match.startswith("u_")]
    key_list.sort()
    print(key_list)

    truth = stress["%s%s" % (var, key_list[-1][1:])]
    norms = [[], [], []]
    for index, key in enumerate(key_list[:-1]):
        norms[index].append(key)
        val = stress["%s%s" % (var, key[1:])]
        val_intp = project_to_delta16(val, truth)
        error = val_intp.values - truth.values
        l2 = norm(error, ord=2) / norm(truth.values, ord=2)
        norms[index].append("%.4f" % l2)

    print(tabulate(norms, headers=["key", "error"]))
    return None

compute_norms_domhimpact("l6")
compute_norms_domhimpact_stress("l6", 'uu')
compute_norms_domhimpact_stress("l6", 'uw')
