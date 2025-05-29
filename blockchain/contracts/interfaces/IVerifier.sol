// SPDX-License-Identifier: CC-BY-SA-4.0
// File name: interfaces/IVerifier.sol
pragma solidity >= 0.5.0 < 0.9.0;

interface IVerifier {
    function verifyProof(
        uint[2] memory a,
        uint[2][2] memory b,
        uint[2] memory c,
        uint[] memory input
    ) external view returns (bool);
}