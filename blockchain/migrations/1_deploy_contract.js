// File name: 1_deploy_contract.js
var MARTSIAEth = artifacts.require("MARTSIAEth");
// const AttributeVerifier = artifacts.require("AttributeVerifier");
module.exports = function(deployer) {
    deployer.deploy(MARTSIAEth);
};