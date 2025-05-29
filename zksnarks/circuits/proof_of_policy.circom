pragma circom 2.2.2;

include "./proof_of_attribute_template.circom";

// Example for policy: (AttrType1@Auth1 AND AttrType2@Auth2)
template ProofOfPolicy() {
    // Inputs - public/private determined by main component declaration
    signal input commitment1[2];  // Array for Pedersen hash output
    signal input commitment2[2];  // Array for Pedersen hash output
    signal input current_date;
    signal input policy_id;

    // Private inputs (not listed in public array)
    signal input secret1;
    signal input value1;
    signal input auth_id1;
    signal input type1;
    signal input expiry1;
    
    signal input secret2;
    signal input value2;
    signal input auth_id2;
    signal input type2;
    signal input expiry2;

    // Instantiate attribute proof circuits
    component attr_proof1 = ProofOfAttribute();
    component attr_proof2 = ProofOfAttribute();

    // Wire inputs for first attribute proof
    attr_proof1.attr_secret <== secret1;
    attr_proof1.attr_value <== value1;
    attr_proof1.authority_id <== auth_id1;
    attr_proof1.attr_type <== type1;
    attr_proof1.expiry_date <== expiry1;
    attr_proof1.attr_commitment[0] <== commitment1[0];
    attr_proof1.attr_commitment[1] <== commitment1[1];
    attr_proof1.current_date <== current_date;
    attr_proof1.expected_authority_id <== 1; // Auth1 ID
    attr_proof1.expected_attr_type <== 1;    // Type1 ID

    // Wire inputs for second attribute proof
    attr_proof2.attr_secret <== secret2;
    attr_proof2.attr_value <== value2;
    attr_proof2.authority_id <== auth_id2;
    attr_proof2.attr_type <== type2;
    attr_proof2.expiry_date <== expiry2;
    attr_proof2.attr_commitment[0] <== commitment2[0];
    attr_proof2.attr_commitment[1] <== commitment2[1];
    attr_proof2.current_date <== current_date;
    attr_proof2.expected_authority_id <== 2; // Auth2 ID
    attr_proof2.expected_attr_type <== 2;    // Type2 ID
}

component main {public [commitment1, commitment2, current_date, policy_id]} = ProofOfPolicy();