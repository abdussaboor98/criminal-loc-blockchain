pragma solidity ^0.5.0;

contract AllowedAuthorities{
    address adminAcc;
    
    constructor() public{
        adminAcc = msg.sender;
    }
    address[] allowed;
    mapping (address => string) authorities;
    
    function checkAccess(address _address) public view returns(bool){
        uint len = allowed.length;
        for(uint i=0;i<len;i++){
            if(_address == allowed[i] || _address == adminAcc){
                return true;
            }
        }
        return false;
    }
    
    function addUserAcc(string memory _authority) public{
        allowed.push(msg.sender);
        authorities[msg.sender] = _authority;
    }
    
    function getAuthority(address _account) view public returns(string memory){
        return authorities[_account];
    }
}