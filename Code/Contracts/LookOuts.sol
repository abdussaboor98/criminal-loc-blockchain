pragma solidity ^0.5.0;
import "./AllowedAuthorities.sol" as AllAuth;
import "./PassportData.sol" as Passports;

contract LookOuts {
    
    //create other Contract's instances
    AllAuth.AllowedAuthorities allauth;//Has the accounts that can submit the complaints
    Passports.PassportData passportdata;//Has the data of all the passportdata holding a passport
    
    //Variable declarations
    address adminAcc;
    enum Status {whitelist,greylist,blacklist}
    uint[] compIds;
    uint compCount;
    
    //Structure declaration
    struct complaint{
        string name;
        uint aadharNo;
        string passportNo;
        uint duration;
        uint submitTime;
        Status status;
        address account;
        string authority;
        uint compId;
        
    }
    
    //Events declarations
    event createdAlert(uint compId);
    event noSuchAadhar(uint aadharNo);
    event noSuchPassport(string ppNo);
    event passportAlert(uint aadharNo,string passportNo,address retAddr,string location,string status);
    event aadharAlert(uint aadharNo,string passportNo,address retAddr,string location,string status);
    event notAllowed(address illegalAccount);
    event detailsUpdated(uint compId);
    
    //Mapping that maps aadhar number to complaints
    mapping(uint => complaint) complaints;
    
    //Constructor definition. Pass in the addresses of the deployed contracts AllowedUser and Passports
    constructor(address usersAddr,address personsAddr) public{
        adminAcc = msg.sender;
        compCount = 1;
        //Link to other contracts
         allauth = AllAuth.AllowedAuthorities(usersAddr);
         passportdata = Passports.PassportData(personsAddr);
    }
    
    //Function for updating the status of complaint based on duration.
    //Call this function before checking any status
    function updateByDuration() public{
        for(uint i=0;i<compIds.length;i++)
        {   
            uint compId = compIds[i];
            if(now > (complaints[compId].submitTime + (complaints[compId].duration * 1 seconds))){
                complaints[compId].status = Status.whitelist;
            }
        }
    }
    
    //Returns the number of complaints saved 
    function getCompCount() public view returns(uint){
        return compCount;
    }
    
    //create a new LOC by Aadhar number
    //If Aadhar does not exists then throws an event noSuchAadhar(aadharNo)
    //On successful creation throws the event createdAlert(compId)
    function newByAadhar (uint _compId,uint _aadharNo,uint _duration, Status _status) public{
        if(allauth.checkAccess(msg.sender)){
            compIds.push(_compId);
            compCount++;
            complaints[_compId].compId = _compId;
            string memory _name = passportdata.getName(_aadharNo);
            complaints[_compId].name=_name;
            complaints[_compId].aadharNo=_aadharNo;
            complaints[_compId].duration=_duration;
            complaints[_compId].status=_status;
            complaints[_compId].submitTime = now;
            complaints[_compId].account = msg.sender;
            string memory _ppNo = passportdata.getPassportNo(_aadharNo);
            complaints[_compId].authority = allauth.getAuthority(msg.sender);
            complaints[_compId].passportNo = _ppNo;
            emit createdAlert(_compId);
        }
        else
            emit notAllowed(msg.sender);
    }
    
    //create a new LOC by Aadhar number
    //If Aadhar does not exists then throws an event noSuchPassport(passportNo)
    //On successful creation throws the event createdAlert(compId)
    function newByPassport(uint _compId,string memory _ppNo,uint _duration, Status _status) public {
        if(allauth.checkAccess(msg.sender)){
            compIds.push(_compId);
            compCount++;
            complaints[_compId].compId = _compId;
            uint _aadharNo = passportdata.getAadharNo(_ppNo);
            string memory _name = passportdata.getName(_aadharNo);
            complaints[_compId].name=_name;
            complaints[_compId].aadharNo=_aadharNo;
            complaints[_compId].duration=_duration;
            complaints[_compId].status=_status;
            complaints[_compId].submitTime = now;
            complaints[_compId].account = msg.sender;
            complaints[_compId].passportNo = _ppNo;
            complaints[_compId].authority = allauth.getAuthority(msg.sender);
            emit createdAlert(_compId);
        }
        else
            emit notAllowed(msg.sender);
    }

    //check if complaint id already exists before calling newByAadhar() or newByPassport() 
    //or updateById() or ststusById()
    function checkId(uint _compid) public view returns (bool){
        for(uint i=0;i<compIds.length;i++){
            if(_compid == compIds[i])
                return true;
        }
        return false;
    }
    
    //Check if the aadhar number exists in the Passport Data contract
    function aadharExists(uint _aadharNo) public view returns (bool){
        return passportdata.aadharExists(_aadharNo);
    }
    
    //Check if the passport number exists in the Passport Data contract
    function passportExists(string memory _passportNo) public view returns (bool){
        return passportdata.passportExists(_passportNo);
    }

    //Update the status of the LOC by using ID
    //Only the account who submitted the LOC can update the status
    //If the person is not allowed then the event notAllowed is raised
    function updateById(uint _compid,Status _status,uint _duration) public{
        if(complaints[_compid].account == msg.sender){
            complaints[_compid].status = _status;
            complaints[_compid].duration = _duration;
            complaints[_compid].submitTime = now;
            emit detailsUpdated(_compid);
        }
        else
            emit notAllowed(msg.sender);
        
    }

    //Retrieve all the info of the complaint by complaint no
    function statusById(uint _compid) view public returns(uint,string memory,uint,string memory,string memory,string memory){
        string memory _status = "Whitelist";
        if(complaints[_compid].status == Status.whitelist)
            _status = "Whitelist";
        else if(complaints[_compid].status == Status.greylist)
            _status = "Greylist";
        else if(complaints[_compid].status == Status.blacklist)
            _status = "Blacklist";
        return (complaints[_compid].compId,complaints[_compid].name,complaints[_compid].aadharNo,complaints[_compid].passportNo,complaints[_compid].authority,_status);
    }
    
    //returns the highest status on aadhar no if no LOC is found the returns Whitelist
    function statusByAadhar(uint _aadharNo) public view returns(string memory){
        Status _status = Status.whitelist;
        string memory ret_status;
        for(uint i=0;i<compIds.length;i++)
        {   
            uint _compid = compIds[i];
            if(complaints[_compid].aadharNo == _aadharNo)
            {
                if(complaints[_compid].status == Status.whitelist)
                    if(_status == Status.greylist || _status == Status.blacklist)
                        break;
                    else
                        _status = Status.whitelist;
                else if(complaints[_compid].status == Status.greylist)
                    if(_status == Status.blacklist)
                        break;
                    else
                        _status = Status.greylist;
                else if(complaints[_compid].status == Status.blacklist)
                    _status = Status.blacklist;
                
            }
        }
        if(_status == Status.whitelist)
            ret_status = "Whitelist";
        else if(_status == Status.greylist)
            ret_status = "Greylist";
        else if(_status == Status.blacklist)
            ret_status = "Blacklist";
        return ret_status;
    }
    
    //returns the highest status on passport no if no LOC is found the returns Whitelist
    function statusByPp(string memory _passportNo) public view returns(string memory){
        Status _status = Status.whitelist;
        string memory ret_status;
        for(uint i=0;i<compIds.length;i++)
        {   
            uint _compid = compIds[i];
            if(keccak256(abi.encodePacked(complaints[_compid].passportNo)) == keccak256(abi.encodePacked(_passportNo)))
            {
                if(complaints[_compid].status == Status.whitelist)
                    if(_status == Status.greylist || _status == Status.blacklist)
                        break;
                    else
                        _status = Status.whitelist;
                else if(complaints[_compid].status == Status.greylist)
                    if(_status == Status.blacklist)
                        break;
                    else
                        _status = Status.greylist;
                else if(complaints[_compid].status == Status.blacklist)
                    _status = Status.blacklist;
            }
        }
        if(_status == Status.whitelist)
            ret_status = "Whitelist";
        else if(_status == Status.greylist)
            ret_status = "Greylist";
        else if(_status == Status.blacklist)
            ret_status = "Blacklist";
        return ret_status;
    }
    
    //triggers an event when aadhar no is scanned
    function aadharScan(uint _aadharNo, string memory _location) public{
        address retAddr;
        for(uint i=0;i<compIds.length;i++)
        {   
            uint _compid = compIds[i];
            if(complaints[_compid].aadharNo == _aadharNo)
            {
                if(complaints[_compid].status != Status.whitelist)
                {
                    retAddr = complaints[_compid].account;
                    aadharAlertCall(_aadharNo,complaints[_compid].passportNo,retAddr,_location,complaints[_compid].status);
                }
            }
        }
    }
    
    //The call that raises the aadharAlert event
    function aadharAlertCall(uint _aadharNo,string memory passportNo,address _retAddr,string memory _location, Status _status) public{
        string memory status_;
        if(_status == Status.greylist)
            status_ = "Greylist";
        else if(_status == Status.blacklist)
            status_ = "Blacklist";
        emit aadharAlert(_aadharNo,passportNo,_retAddr,_location,status_);
    }
    
    //Returns the account that submitted the complaint
    function getAccount(uint _compId) public view returns(address){
        return complaints[_compId].account;
    }
    
    //Returns the aadhar number of the complaint id sent
    function getAadharByCompId(uint _compId)public view returns(uint){
        return complaints[_compId].aadharNo;
    }
    
    //Returns the passport number of the complaint id sent
    function getPassportByCompId(uint _compId)public view returns(uint){
        return complaints[_compId].aadharNo;
    }
}