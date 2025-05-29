const AttributeVerifier = artifacts.require("verifiers/Verifier_proof_of_attribute");
const PolicyVerifier = artifacts.require("verifiers/Verifier_proof_of_policy");
const ProcessVerifier = artifacts.require("verifiers/Verifier_proof_of_process");
const MARTZKEth = artifacts.require("MARTZKEth");

module.exports = async function (deployer) {
  // Deploy verifiers
  await deployer.deploy(AttributeVerifier);
  await deployer.deploy(PolicyVerifier);
  await deployer.deploy(ProcessVerifier);
  
  // Deploy main contract with verifier addresses
  await deployer.deploy(
    MARTZKEth, 
    AttributeVerifier.address, 
    PolicyVerifier.address, 
    ProcessVerifier.address
  );
  
  console.log("MARTZKEth deployed to:", MARTZKEth.address);
  console.log("AttributeVerifier deployed to:", AttributeVerifier.address);
  console.log("PolicyVerifier deployed to:", PolicyVerifier.address);
  console.log("ProcessVerifier deployed to:", ProcessVerifier.address);
};
