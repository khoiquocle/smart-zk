pragma circom 2.2.2;

include "node_modules/circomlib/circuits/pedersen.circom";
include "node_modules/circomlib/circuits/comparators.circom";

template ProofOfAttribute() {
    // Inputs - public/private determined by main component declaration
    signal input attr_secret; // Secret associated with the attribute
    signal input attr_value;  // Actual attribute value
    signal input authority_id; // Issuing authority ID
    signal input attr_type;    // Attribute type ID
    signal input expiry_date;  // Expiry date (YYYYMMDD format)
    
    signal input attr_commitment[2]; // Commitment to verify against (array for Pedersen output)
    signal input current_date;    // Current date for expiry check
    signal input expected_authority_id; // Authority constraint  
    signal input expected_attr_type;   // Attribute type constraint
    
    // Hash calculation for commitment
    component hasher = Pedersen(5);
    hasher.in[0] <== attr_secret;
    hasher.in[1] <== attr_value;
    hasher.in[2] <== authority_id;
    hasher.in[3] <== attr_type;
    hasher.in[4] <== expiry_date;
    
    // Verify the commitment matches
    attr_commitment[0] === hasher.out[0];
    attr_commitment[1] === hasher.out[1];
    
    // Verify attribute is not expired
    component lessThan = LessThan(64);
    lessThan.in[0] <== current_date;
    lessThan.in[1] <== expiry_date;
    lessThan.out === 1; // current_date < expiry_date
    
    // Verify authority and attribute type match expectations
    authority_id === expected_authority_id;
    attr_type === expected_attr_type;
}

// NO main component - this is just a template for inclusion