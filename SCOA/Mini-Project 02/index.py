# import asyncio
import panel as pn
import numpy as np

# Decreasing MF (L Function)


def openLeft(x, alpha, beta):
    if x < alpha:
        return 1
    if x > alpha and x <= beta:
        return (beta-x)/(beta-alpha)
    else:
        return 0

# Increasing MF (T Function)


def openRight(x, alpha, beta):
    if x < alpha:
        return 0
    if x > alpha and x <= beta:
        return (x-alpha)/(beta-alpha)
    else:
        return 1


# function for triangular fuzzification (^ function)
def triangular(x, a, b, c):
    return max(min((x-a)/(b-a), (c-x)/(c-b)), 0)


# fuzzy partition/MF generation
def partition(x):
    NL = 0
    NM = 0
    NS = 0
    ZE = 0
    PS = 0
    PM = 0
    PL = 0

    if x > 0 and x < 60:
        NL = openLeft(x, 30, 60)
    if x > 30 and x < 90:
        NM = triangular(x, 30, 60, 90)
    if x > 60 and x < 120:
        NS = triangular(x, 60, 90, 120)
    if x > 90 and x < 150:
        ZE = triangular(x, 90, 120, 150)
    if x > 120 and x < 180:
        PS = triangular(x, 120, 150, 180)
    if x > 150 and x < 210:
        PM = triangular(x, 150, 180, 210)
    if x > 180 and x < 240:
        PL = openRight(x, 180, 210)

    return NL, NM, NS, ZE, PS, PM, PL


# Rule base util function
def compare(TC1, TC2):
    TC = 0
    if TC1 > TC2 and TC1 != 0 and TC2 != 0:
        TC = TC2
    else:
        TC = TC1

    if TC1 == 0 and TC2 != 0:
        TC = TC2

    if TC2 == 0 and TC1 != 0:
        TC = TC1

    return TC

# Rule base


def rule(NLSD, NMSD, NSSD, ZESD, PSSD, PMSD, PLSD, NLAC, NMAC, NSAC, ZEAC, PSAC, PMAC, PLAC):
    PLTC1 = min(NLSD, ZEAC)
    PLTC2 = min(ZESD, NLAC)
    PLTC = compare(PLTC1, PLTC2)

    PMTC1 = min(NMSD, ZEAC)
    PMTC2 = min(ZESD, NMAC)
    PMTC = compare(PMTC1, PMTC2)

    PSTC1 = min(NSSD, PSAC)
    PSTC2 = min(ZESD, NSAC)
    PSTC = compare(PSTC1, PSTC2)

    NSTC = min(PSSD, NSAC)
    NLTC = min(PLSD, ZEAC)

    return PLTC, PMTC, PSTC, NSTC, NLTC


# defuzzification using Centre of Sum method
# function to return area of triangular region
def areaTR(mu, a, b, c):
    x1 = mu*(b-a) + a
    x2 = c - mu*(c-b)
    d1 = (c-a)
    d2 = x2-x1
    a = (0.5)*mu*(d1+d2)
    return a

# Area Open Left


def areaOL(mu, alpha, beta):
    xOL = beta-(beta-alpha)*mu
    return 0.5*mu*(beta+xOL), beta/2

# Area Open Right


def areaOR(mu, alpha, beta):
    xOR = (beta-alpha)*mu+alpha
    aOR = 0.5*mu*((240-alpha)+(240+xOR))
    return aOR, (240-alpha)/2+alpha


def defuzzyfication(PLTC, PMTC, PSTC, NSTC, NLTC):
    areaPL = 0
    areaPM = 0
    areaPS = 0
    areaNS = 0
    areaNL = 0
    cPL = 0
    cPM = 0
    cPS = 0
    cNS = 0
    cNL = 0

    if PLTC != 0:
        areaPL, cPL = areaOR(PLTC, 180, 210)

    if PMTC != 0:
        areaPM = areaTR(PMTC, 150, 180, 210)
        cPM = 180

    if PSTC != 0:
        areaPS = areaTR(PSTC, 120, 150, 180)
        cPS = 150

    if NSTC != 0:
        areaNS = areaTR(NSTC, 60, 90, 120)
        cNS = 90

    if NLTC != 0:
        areaNL, cNL = areaOL(NLTC, 30, 60)

    numerator = areaPL*cPL + areaPM*cPM + areaPS*cPS + areaNS*cNS + areaNL*cNL
    denominator = areaPL + areaPM + areaPS + areaNS + areaNL

    if denominator == 0:
        # print("No rules to give results")
        return 0
    else:
        crispOutput = numerator/denominator
        return crispOutput


# UI Setup
sd_slider = pn.widgets.IntSlider(
    start=0, end=240, name='Speed Difference', value=40)
acc_slider = pn.widgets.IntSlider(
    start=0, end=240, name='Acceleration', value=110)


def compute(speed, acceleration):
    NLSD, NMSD, NSSD, ZESD, PSSD, PMSD, PLSD = partition(speed)
    NLAC, NMAC, NSAC, ZEAC, PSAC, PMAC, PLAC = partition(acceleration)
    PLTC, PMTC, PSTC, NSTC, NLTC = rule(
        NLSD, NMSD, NSSD, ZESD, PSSD, PMSD, PLSD, NLAC, NMAC, NSAC, ZEAC, PSAC, PMAC, PLAC)
    crispOutputFinal = defuzzyfication(PLTC, PMTC, PSTC, NSTC, NLTC)
    return f'Throttle Control: {crispOutputFinal}'


bound = pn.bind(compute, sd_slider, acc_slider)

col = pn.Column(sd_slider, acc_slider, bound)

pn.io.pyodide.show(col, 'myplot')
