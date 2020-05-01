pragma solidity ^0.5.0;

contract PassportData{
    address adminAcc;
    uint[] aadharNos;
    string[] passportNos;
    //Creat a structure for storing the passport details
    struct Person{
        string name;
        string passportNo;
        uint aadharNo;
        bytes facecode;//For storing face byte code
        uint locCount;
        string[] location;//The array of scanned locations
    }
    
    //Map the person structure to the aadhar numbers
    mapping (uint => Person) people;
    
    //Event that is raised when a new person is added
    event personAdded(string name, string passportNo, uint aadharNo);
    
    constructor() public{
        adminAcc = msg.sender;
    }
    
    modifier onlyAdmin{
        require(msg.sender == adminAcc);
        _;
    }
    
    //Add a new passport detail
    function addPerson(string memory _name, string memory _ppNo, uint _aadharNo, bytes memory _facecode) public{
        people[_aadharNo].name = _name;
        people[_aadharNo].passportNo = _ppNo;
        people[_aadharNo].aadharNo = _aadharNo;
        people[_aadharNo].facecode = _facecode;
        people[_aadharNo].locCount = 0;
        aadharNos.push(_aadharNo);
        passportNos.push(_ppNo);
        emit personAdded(_name,_ppNo,_aadharNo);
    }
    
    //Returns if the passport exists or nor
    function passportExists(string memory _ppNo) public view returns(bool){
        for(uint i=0;i<passportNos.length;i++)
        {   
            if(keccak256(abi.encodePacked(passportNos[i])) == keccak256(abi.encodePacked(_ppNo)))
            {
                return true;
            }
        }
            return false;
    }
    
    //Returns if the aadhar number exists or not
    function aadharExists(uint _aadharNo) public view returns(bool){
        for(uint i=0;i<aadharNos.length;i++)
        {   
            if(aadharNos[i] == _aadharNo)
            {
                return true;
            }
        }
            return false;
    }
    
    //Retrieve the passport number for the given aadhar number
    function getPassportNo(uint _aadharNo) view public returns(string memory){
        return people[_aadharNo].passportNo;
    }
    
    //Retrieve the aadhar number for the given passport number
    function getAadharNo(string memory _ppNo) view public returns(uint){
        for(uint i=0;i<aadharNos.length;i++)
        {   
            uint _aadharNo = aadharNos[i];
            if(keccak256(abi.encodePacked(people[_aadharNo].passportNo)) == keccak256(abi.encodePacked(_ppNo)))
            {
                return _aadharNo;
            }
        }
    }
    
    //Retrieve the name associated with given aadhar number
    function getName(uint _aadharNo) view public returns(string memory){
        return people[_aadharNo].name;
    }
    
    //Retrieve the face encoding associated with the given aadhar number
    function getFaceCode(uint _aadharNo) public view returns(bytes memory){
        return people[_aadharNo].facecode;
    }

    //Add the location to the scanned locations for the aadhar number
    function addLocation(uint _aadharNo, string memory _location) public{
        people[_aadharNo].location.push(_location);
        people[_aadharNo].locCount++;
    }
    
    //Returns the locations count for the aadhar number
    //Only the admin can access this method
    function getLocCount(uint _aadharNo) public view onlyAdmin returns(uint) {
        return people[_aadharNo].locCount;
    }
    
    //Returns the location at the index for the aadhar number
    //Only the admin can access this method
    function getLocation(uint _aadharNo, uint index) public view onlyAdmin returns(string memory) {
        return people[_aadharNo].location[index];
    }
}