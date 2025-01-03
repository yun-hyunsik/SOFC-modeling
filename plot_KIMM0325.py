# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 03:41:15 2024

@author: 82108
"""

import matplotlib.pyplot as plt
import numpy as np
from cantera import IdealGasMix, one_atm

# SOFC 모델링을 위한 초기 설정
gas = IdealGasMix('gri60.xml')  # SOFC 연료 특성에 맞는 xml 파일로 변경
N = gas.n_species
iH2 = gas.species_index('H2')
iO2 = gas.species_index('O2')

# 초기 연료 혼합 비율 설정
T1 = 30 + 273.15
P1 = one_atm
m_H2 = 0.02  # SOFC 연료 유량 [kg/s]
m_O2 = 0.04  # 산화제 유량 [kg/s]
m1 = m_H2 + m_O2  # 총 유량 [kg/s]

y_fuel = np.zeros(N)
y_fuel[iH2] = m_H2
y_fuel[iO2] = m_O2

gas.TPY = T1, P1, y_fuel
LHV_cell = gas.enthalpy_mole / gas.molecular_weights[iH2]  # 추정값 (예제용)
LHV_fuel = LHV_cell * m1 / 1000  # [kW]

# Plot 데이터
down_heatno = [100, 95, 90, 85, 80, 75, 70, 65, 60, 55]
down_heat = [100, 93, 88, 83, 79, 74, 70, 67, 63, 60]

Ppeak_heatno = [30, 40, 60, 90, 120, 150, 180, 210, 240, 270]
Ppeak_heat = [28, 38, 58, 85, 115, 145, 175, 200, 230, 260]

Tpeak_heatno = [1800, 1750, 1700, 1650, 1600, 1550, 1500, 1450, 1400, 1350]
Tpeak_heat = [1750, 1720, 1680, 1620, 1580, 1540, 1490, 1440, 1390, 1340]

# 데이터 시각화
plt.figure(1)
plt.plot(down_heatno, down_heat, 'b-o', linewidth=2)
plt.title('SOFC Downsizing Ratio', fontsize=14, fontweight='bold')
plt.xlabel('Compression Ratio', fontsize=12, fontweight='bold')
plt.ylabel('Downsizing Ratio (%)', fontsize=12, fontweight='bold')
plt.grid(True)
plt.legend(['Heat Transfer Included'])

plt.figure(2)
plt.plot(Ppeak_heatno, Ppeak_heat, 'r-s', linewidth=2)
plt.title('SOFC Peak Pressure', fontsize=14, fontweight='bold')
plt.xlabel('Compression Ratio', fontsize=12, fontweight='bold')
plt.ylabel('Peak Pressure (bar)', fontsize=12, fontweight='bold')
plt.grid(True)

plt.figure(3)
plt.plot(Tpeak_heatno, Tpeak_heat, 'g-^', linewidth=2)
plt.title('SOFC Peak Temperature', fontsize=14, fontweight='bold')
plt.xlabel('Compression Ratio', fontsize=12, fontweight='bold')
plt.ylabel('Peak Temperature (K)', fontsize=12, fontweight='bold')
plt.grid(True)

plt.show()
