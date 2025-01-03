# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 03:21:57 2024

@author: 82108
"""

# SOFC 모델링 코드 (MCFC에서 변환)
import numpy as np
from cantera import Solution, one_atm

def sofc_model(m_CH4, m_H2O, m_ca_in, T_reform_in, T_reform_out, P_reform, x_ca_in):
    """
    SOFC 모델링 함수
    - 입력: 연료 성분, 초기 조건, 온도 및 압력
    - 출력: 시스템 효율, 스택 온도, 전기 화학적 파라미터
    """
    gas = Solution('gri30.yaml')  # gri30.xml -> gri30.yaml
    
    # 기체 구성 요소 인덱스
    iCO2 = gas.species_index('CO2')
    iCH4 = gas.species_index('CH4')
    iH2 = gas.species_index('H2')
    iH2O = gas.species_index('H2O')
    iO2 = gas.species_index('O2')
    
    # 총 유량
    m_tot = m_CH4 + m_H2O  # [kg/s]

    # Reformer 계산
    x_an_in, Q_an_mix = reformer(gas, m_CH4, m_H2O, T_reform_in, T_reform_out, P_reform)

    # 연료의 낮은 발열량(LHV)
    gas.Y = {"CH4": m_CH4, "H2O": m_H2O}
    LHV_fuel = gas.enthalpy_mass  # 단위: [J/kg]

    # SOFC 조건 초기화
    V = 0.8  # 초기 전지 전압 [V]
    num_stacks = 300  # 스택 수
    A_tot = 12000  # 전극 면적 [cm^2]
    util = 0.75  # 연료 활용도
    
    # 온도 및 압력 설정
    T_fc = T_reform_out  # 연료 전지 초기 온도 [K]
    P_an = one_atm
    P_ca = one_atm

    # 계산 반복
    for iteration in range(100):
        # 가스 상태 업데이트
        gas.TPX = T_fc, P_an, x_an_in

        # 전기화학적 계산
        delta_G = 242000 - 45.8 * T_fc  # 기브스 자유 에너지 변화 [J/mol]
        E = delta_G / (2 * 96487)  # Nernst 전압 [V]
        R_tot = 0.1  # 내부 저항 [Ohm*cm^2], 추정값
        j = (E - V) / R_tot  # 전류 밀도 [A/cm^2]
        
        # 연료 활용도 및 효율 업데이트
        util_calc = 1 - (LHV_fuel * (1 - util) / LHV_fuel)
        if abs(util_calc - util) < 0.01:
            break
        V += 0.01 if util_calc < util else -0.01

    # 출력 결과 계산
    W_tot = j * A_tot * num_stacks  # 총 전력 [W]
    eff_cell = W_tot / (LHV_fuel * m_tot)  # 시스템 효율

    return W_tot, T_fc, eff_cell

def reformer(gas, m_CH4, m_H2O, T_in, T_out, P):
    """
    개질기 (Reformer) 계산 함수
    - 가스 및 연료 유량 초기화
    - 출력: 개질된 연료 조성
    """
    # 입력 상태 설정
    gas.TPX = T_in, P, {"CH4": m_CH4, "H2O": m_H2O}
    # 화학적 균형 계산
    gas.equilibrate('TP')
    x_out = gas.X
    Q_an_mix = gas.enthalpy_mass
    return x_out, Q_an_mix
