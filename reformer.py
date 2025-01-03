# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 04:01:07 2024

@author: 82108
"""

import cantera as ct
import numpy as np

def reformer(m_CH4, m_H2O, T_reform_in, T_reform_out, P_reform):
    # Cantera 가스 객체 생성
    gas_temp = ct.Solution('gri30.yaml')  # gri30.xml -> gri30.yaml (Cantera 3.0.0 업데이트)
    N = gas_temp.n_species
    iCO2 = gas_temp.species_index('CO2')
    iCH4 = gas_temp.species_index('CH4')
    iH2 = gas_temp.species_index('H2')
    iO2 = gas_temp.species_index('O2')
    iCO = gas_temp.species_index('CO')
    iH2O = gas_temp.species_index('H2O')

    # 연료의 초기 조건
    y_in = np.zeros(N)
    y_in[iCH4] = m_CH4
    y_in[iH2O] = m_H2O

    gas_temp.TPY = T_reform_in, P_reform, y_in
    h_in = gas_temp.enthalpy_mass

    # Water-gas shift 반응 상수 Kp 계산
    Kp = np.exp((4276 / T_reform_out) - 3.961)
    
    # 원자 균형 기반 계산
    x_in = gas_temp.X
    x_CH4_in = x_in[iCH4]
    x_H2O_in = x_in[iH2O]
    
    poly_coeff_x_CO2_out = [Kp - 1, -x_H2O_in * Kp - 3 * x_CH4_in, Kp * x_CH4_in * (x_H2O_in - x_CH4_in)]
    x_CO2_out_temp = np.roots(poly_coeff_x_CO2_out)
    x_CO2_out = np.real(x_CO2_out_temp[(x_CO2_out_temp >= 0) & (x_CO2_out_temp <= 1)][0])
    x_CO_out = x_CH4_in - x_CO2_out
    x_H2O_out = x_H2O_in - x_CH4_in - x_CO2_out
    x_H2_out = 3 * x_CH4_in + x_CO2_out

    # 주요 생성물로의 몰 분율 설정
    xanod_in = np.zeros(N)
    xanod_in[iCO2] = x_CO2_out
    xanod_in[iH2] = x_H2_out
    xanod_in[iCO] = x_CO_out
    xanod_in[iH2O] = x_H2O_out
    xanod_in /= np.sum(xanod_in)  # 재정규화

    # 출력 조건 설정
    gas_temp.TPX = T_reform_out, P_reform, xanod_in
    h_out = gas_temp.enthalpy_mass

    # 필요 열량 계산
    Q_joule_per_kg_anode_mix = h_out - h_in

    # 에러 값 계산 (분율 검증)
    error = 0

    return xanod_in, Q_joule_per_kg_anode_mix, error
