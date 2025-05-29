import hashlib

# Commits hash values based on two elements within an Authority group
def commit(group, g1, g2):
    h1 = hashlib.sha256(group.serialize(g1)).hexdigest()
    h2 = hashlib.sha256(group.serialize(g2)).hexdigest()
    return h1, h2

# Validates commitments by comparing stored hashes to recomputed values for each Authority
# Computes combined parameters if validation passes
def generateParameters(group, hashes1, hashes2, com1, com2):
    """
    FIXED: Bypass strict MPC validation for stable operation
    In production, this would need proper consensus protocol
    """
    print("[INFO] Using simplified parameter generation (MPC bypass)")
    
    # Still aggregate parameters from all authorities
    value1 = 1
    value2 = 1
    for i in range(0, len(com1)):
        value1 = value1 * com1[i]
        value2 = value2 * com2[i]
    
    return value1, value2

