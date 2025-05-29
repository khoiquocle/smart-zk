pragma circom 2.2.2;

include "node_modules/circomlib/circuits/pedersen.circom";

template ProofOfProcessCompliance() {
    // All inputs (privacy controlled by main component declaration)
    signal input secret_for_stepA_attestation;  // Will be private
    signal input stepA_details;                 // Will be private
    signal input commitment_to_stepA_attestation; // Will be public
    signal input current_process_id;            // Will be public
    signal input claimed_current_step_id;       // Will be public
    signal input expected_previous_step_id;     // Will be public

    // Hash calculation for step attestation
    component hasher = Pedersen(2);
    hasher.in[0] <== stepA_details;
    hasher.in[1] <== secret_for_stepA_attestation;

    // Verify the commitment matches (use constraint assignment)
    commitment_to_stepA_attestation === hasher.out[0];

    // Verify process flow (current step follows previous step)
    claimed_current_step_id === expected_previous_step_id + 1;
}

component main {public [commitment_to_stepA_attestation, current_process_id, claimed_current_step_id, expected_previous_step_id]} = ProofOfProcessCompliance();