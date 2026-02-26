import math

import frcm.fireriskmodel.parameters as mp

"""Functions for computing saturation vapor pressure, and water concentrations"""
""" pw_sat -- cw_sat -- cw_in -- initial fmc """


# saturation vapor pressure at temperature Temp_c (celsius)
def calc_pwsat(temp_c: float) -> float:
    """Calculates the saturation vapor pressure at a given temperature."""
    pwsat = 610.78 * math.exp((17.2694 * temp_c) / (temp_c + 238.3))
    return pwsat


# saturation water concentration based on saturated vapor pressure (pwsat)
def calc_cwsat(pwsat: float, temp_c: float) -> float:
    """Calculates the saturation water concentration."""
    cwsat = (pwsat * mp.mol_weight) / (mp.gas_constant * (temp_c + 273.15))
    return cwsat


# actual water concentration in air
def calc_cw(rh: float, cwsat: float) -> float:
    """Calculates the actual water concentration in the air."""
    cw = rh / 100 * cwsat
    return cw


# computes initial fmc of wooden panels
# computes fmc from indoor rh (equilibrium state) rh must be given as a fraction,
# e.g., 0.35
def calc_fmc(rh: float) -> float:
    """Computes the initial fuel moisture content of wooden panels."""
    c_fmc = (
        0.0017
        + 0.2524 * rh
        - 0.1986 * math.pow(rh, 2)
        + 0.0279 * math.pow(rh, 3)
        + 0.167 * math.pow(rh, 4)
    )
    return c_fmc


""" Functions related to ventilation """
""" Air change per Hour -- Beta"""


# air change per hour (ach)
def calc_ach(temp_c_out: float, temp_c_in: float) -> float:
    """Calculates the air change per hour."""
    c_ach = mp.gamma * math.sqrt(
        (
            abs(1 / (temp_c_out + 273.15) - 1 / (temp_c_in + 273.15))
            / (temp_c_out + 273.15)
        )
    )
    return c_ach


# beta ventilation factor
def calc_beta(c_ach: float) -> float:
    """Calculates the beta ventilation factor."""
    c_beta = 1 - math.exp((-c_ach * mp.delta_t) / 3600)
    return c_beta


""" Updating variables post the modelling of wooden panel humidity transport """


# extrapolating wooden panel fmc to a surface value
def calc_surf(c1_t: float, c2_t: float) -> float:
    """Extrapolates the wooden panel fuel moisture content to a surface value."""
    c_surf = c1_t - 0.5 * (c2_t - c1_t)
    return c_surf


# water concentration difference between bulk air and wall boundary layer
# - inputs from previous timestep
def calc_deltac(rhin: float, rhwall: float, cwsatin: float) -> float:
    """Calculates the water concentration difference."""
    deltac = (rhwall - rhin) * cwsatin
    return deltac


# relative humidity at wooden panel surfaces - inputs surface fmc at equal timestep
def calc_rhwall(cfmc: float) -> float:
    """Calculates the relative humidity at the wooden panel surfaces."""
    rhwall = (
        0.0698
        - 1.258 * (cfmc / mp.rho_wood)
        + 125.35 * math.pow((cfmc / mp.rho_wood), 2)
        - 809.43 * math.pow((cfmc / mp.rho_wood), 3)
        + 1583.8 * math.pow((cfmc / mp.rho_wood), 4)
    )
    return rhwall


# indoor water concentration - input from previous timestep
def calc_cwin(
    cac: float, cwall: float, csupply: float, cwin: float, beta: float
) -> float:
    """Calculates the indoor water concentration."""
    cwin = (1 - beta) * cwin + cac + cwall + csupply
    return cwin


""" Calculation of wooden panel humidity transport """


# computing the fmc in layer 1 (c1_t+1) (facing interior of enclosure)
# by use of fmc values in layer 1 and layer 2
# inputs from previous timestep
def calc_layer1(
    rhin: float, rhwall: float, c1_t: float, c2_t: float, csatin: float
) -> float:
    """Computes the fuel moisture content in layer 1."""
    layer1 = c1_t + (mp.delta_t / mp.delta_x) * (
        (mp.D_W_a / mp.boundary_layer) * (rhin - rhwall) * csatin
        + (mp.D_w_s / mp.delta_x) * (c2_t - c1_t)
    )
    return layer1


# computing the fmc in layers 2 to N-1 (second last layer) at time t+1
# by second order central difference - inputs from previous timestep
def calc_middle_layers(cn_t: float, c_prev_n_t: float, c_post_n_t: float) -> float:
    """Computes the fuel moisture content in the middle layers."""
    middle_layer = cn_t + mp.fourier * (c_prev_n_t - 2 * cn_t + c_post_n_t)
    return middle_layer


# computing the fmc in the last layer (backside of wooden panels)
# based on fmc from layer N-1 and Layer N both from previous timestep
def calc_outer_layer(cn_t: float, c_pre_n_t: float) -> float:
    """Computes the fuel moisture content in the outer layer."""
    outer_layer = cn_t + mp.fourier * (c_pre_n_t - cn_t)
    return outer_layer


""" The main contributions to change in indoor water concentration """
""" Supply -- Air Change by Ventilation -- Humidity Exchange From Wooden Surfaces"""


def calc_csupply(sup: float) -> float:
    """Calculates the water concentration from supply."""
    csupply = sup / mp.Vol
    return csupply


def calc_cac(beta: float, cw_out: float, temp_c_out: float, temp_c_in: float) -> float:
    """Calculates the water concentration from air change."""
    cac = beta * cw_out * ((temp_c_out + 273.15) / (temp_c_in + 273.15))
    return cac


def calc_cwall(deltac: float) -> float:
    """Calculates the water concentration from the wall."""
    cwall = (mp.A_ex * mp.D_W_a * deltac * mp.delta_t / mp.boundary_layer) / mp.Vol
    return cwall
