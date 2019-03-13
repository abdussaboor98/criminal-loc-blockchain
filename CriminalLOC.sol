pragma solidity ^0.5.0;

contract LookOut {
    
    address adminAcc;
    enum Status {submit,open,close,reject}
    enum Lists {grey,black}
    
    struct complaint{
        string name;
        uint aadharNo;
        string passportNo;
        uint duration;
        uint submitTime;
        Status status;
        string authority;
        Lists category;
        address account;
    } 
    
    mapping(uint => complaint) complaints;
    
    constructor() public{
        adminAcc = msg.sender;
    }
    
    
    
}