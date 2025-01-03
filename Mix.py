import cantera as ct

def mix(T1, T2, P1, P2, X1, X2, m1, m2):
    # SOFC에 적합한 기체 모델 사용
    gas = ct.Solution('gri30.cti')  # SOFC 모델에서도 gri30 사용 가능
    M = gas.molecular_weights

    # 기체 1 초기 설정
    gas.TPX = T1, P1, X1
    h1 = gas.enthalpy_mass
    s1 = gas.entropy_mass
    H1 = m1 * h1
    S1 = m1 * s1
    M1 = gas.mean_molecular_weight

    # 기체 2 초기 설정
    gas.TPX = T2, P2, X2
    h2 = gas.enthalpy_mass
    s2 = gas.entropy_mass
    H2 = m2 * h2
    S2 = m2 * s2
    M2 = gas.mean_molecular_weight

    # 혼합된 기체 계산
    m3 = m1 + m2
    P3 = P1  # P1과 동일한 압력 가정
    H3 = H1 + H2
    h3 = H3 / m3
    X3 = (X1 * m1 / M1 + X2 * m2 / M2) / sum(X1 * m1 / M1 + X2 * m2 / M2)

    # 혼합 기체 상태 설정
    gas.HP = h3, P3
    gas.X = X3
    T3 = gas.T
    s3 = gas.entropy_mass
    S3 = m3 * s3

    return T3, P3, s3, h3, m3, X3
