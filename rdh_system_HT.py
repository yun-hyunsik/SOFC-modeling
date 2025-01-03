# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 03:55:24 2024

@author: 82108
"""

# SOFC용 Python 코드 변환
import numpy as np
from cantera import Solution

def sofc_system(t, X, gas):
    """
    ODE 시스템 설정
    :param t: 시간 [s]
    :param X: 상태 벡터
    :param gas: Cantera Solution 객체
    :return: 상태 미분 벡터 dXdt
    """
    global MASS, NSP, MW, FP, FD, ST, TW, SADH, HT, SFC, bore, stroke, con_len, RPM

    # 상태 변수 분해
    theta = X[0]  # 크랭크 각도 [rad]
    V = X[1]      # 가스 혼합물의 부피 [m^3]
    T = X[2]      # 온도 [K]
    k = X[3]      # 난류 운동 에너지 [m^2/s^2]
    Q = X[4]      # 열 전달 [J]
    Y = X[5:5+NSP]  # 각 종의 질량 분율

    # GAS 상태 설정
    gas.TDY = T, MASS / V, Y
    Rc = gas.constant('R') / gas.mean_molecular_weight

    # 화학 반응률 계산
    wdot = gas.net_production_rates  # [kmol/m^3/s]

    # 상태 미분 벡터 초기화
    dXdt = np.zeros_like(X)

    # 각도 변화율 계산
    dXdt[0] = RPM * (2 * np.pi) / 60  # rad/s

    # 부피 변화율 계산 (슬라이더-크랭크 메커니즘)
    a = stroke / 2  # 크랭크 반경 [m]
    num = a * np.sin(theta) * np.cos(theta)
    den = np.sqrt((con_len ** 2) - (a ** 2 * np.sin(theta) ** 2))
    dsdt = dXdt[0] * a * (-np.sin(theta) - num / den)
    dVdt = (np.pi / 4) * (bore ** 2) * (-dsdt)
    dXdt[1] = dVdt

    # 종 질량 분율 변화율 계산
    for i in range(NSP):
        dXdt[5 + i] = wdot[i] * MW[i] * V / MASS  # [1/s]

    # 난류 운동 에너지 변화율
    vp = dVdt / (np.pi * (bore / 2) ** 2)  # 피스톤 속도 [m/s]
    AV = 4 / bore  # 벽 면적 대 체적 비율 [1/m]
    turb_P = FP * AV * (abs(vp) ** 3) - (2 / 3) * k * (1 / V) * dVdt
    vt = np.sqrt(2 * k)  # 난류 속도 [m/s]
    turb_D = FD * k * vt / (V ** (1 / 3))
    dXdt[3] = turb_P - turb_D

    # 열 전달 계산
    Ac_sim = 2 * SADH + 2 * V / (bore / 2)
    Sp = 2 * (stroke * RPM / 60)
    p_instant = (MASS * Rc * T / V) / 1e5  # [bar]
    h_wos = 3.26 * (bore ** -0.2) * (p_instant * 100) ** 0.8 * T ** -0.55 * (2.28 * Sp) ** 0.8

    if HT == 0:
        dXdt[4] = 0
    elif HT == 1:
        dXdt[4] = SFC * Ac_sim * h_wos * (T - TW)
    elif HT == 2:
        cp = gas.cp_mass
        dXdt[4] = ST * vt * (MASS / V) * cp * Ac_sim * (T - TW)

    # 온도 변화율
    cv = gas.cv_mass
    if HT == 0:
        dXdt[2] = -1 / cv * ((gas.P * dVdt / MASS) + (Rc * T * np.dot(gas.partial_molar_enthalpies, dXdt[5:5 + NSP])))
    else:
        dXdt[2] = -1 / cv * ((gas.P * dVdt / MASS) + (1 / MASS) * dXdt[4] +
                             (Rc * T * np.dot(gas.partial_molar_enthalpies, dXdt[5:5 + NSP])))

    return dXdt

# 필요한 수정 사항은 기록 중...
