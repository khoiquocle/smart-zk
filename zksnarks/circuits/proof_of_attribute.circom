pragma circom 2.2.2;

include "node_modules/circomlib/circuits/comparators.circom";

template SimpleHash5() {
    signal input in[5];
    signal output out;
    
    // Very simple hash: weighted sum of inputs (no modulo operations)
    signal weighted[5];
    weighted[0] <== in[0];
    weighted[1] <== in[1] * 31;
    weighted[2] <== in[2] * 961;  // 31^2 = 961
    weighted[3] <== in[3] * 29791; // 31^3 = 29791
    weighted[4] <== in[4] * 923521; // 31^4 = 923521
    
    signal partial_sums[4];
    partial_sums[0] <== weighted[0] + weighted[1];
    partial_sums[1] <== partial_sums[0] + weighted[2];
    partial_sums[2] <== partial_sums[1] + weighted[3];
    partial_sums[3] <== partial_sums[2] + weighted[4];
    
    // Output the final sum directly (no modulo)
    out <== partial_sums[3];
}

template ProofOfAttribute() {
    // Inputs - public/private determined by main component declaration
    signal input attr_secret; // Secret associated with the attribute
    signal input attr_value;  // Actual attribute value
    signal input authority_id; // Issuing authority ID
    signal input attr_type;    // Attribute type ID
    signal input expiry_date;  // Expiry date (YYYYMMDD format)
    
    signal input attr_commitment; // Single commitment value to verify against
    signal input current_date;    // Current date for expiry check
    signal input expected_authority_id; // Authority constraint  
    signal input expected_attr_type;   // Attribute type constraint
    
    // Hash calculation for commitment using simple hash
    component hasher = SimpleHash5();
    hasher.in[0] <== attr_secret;
    hasher.in[1] <== attr_value;
    hasher.in[2] <== authority_id;
    hasher.in[3] <== attr_type;
    hasher.in[4] <== expiry_date;
    
    // Verify the commitment matches
    attr_commitment === hasher.out;
    
    // Verify attribute is not expired
    component lessThan = LessThan(64);
    lessThan.in[0] <== current_date;
    lessThan.in[1] <== expiry_date;
    lessThan.out === 1; // current_date < expiry_date
    
    // Verify authority and attribute type match expectations
    authority_id === expected_authority_id;
    attr_type === expected_attr_type;
}

// Main component for standalone compilation
component main {public [attr_commitment, current_date, expected_authority_id, expected_attr_type]} = ProofOfAttribute();