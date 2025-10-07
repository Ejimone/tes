// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

contract Whatsapp {
    address public sender;
    address public receiver;
    uint256 constant DAY_IN_SECONDS = 86400;
    
    struct Message {
        address sender;
        string content;
        uint256 timestamp;
        bool isRead;
        bool isDeleted;
        bool isMedia;
    }
    constructor() {
        sender = msg.sender;
    }
    struct Chat {
        address sender;
        address receiver;
        Message[] messages;
    }

    struct User {
        string name;
        string status;
        string profilePicture;
        address userAddress;
        uint256 statusExpiry;
    }

    struct Group {
        string groupName;
        address[] members;
        bytes32 groupId;
        string groupDescription;
        address admin;
    }
    struct Archive {
        bytes32 chatId;
        bool isArchived;
    }


    mapping(address => User) private users;
    mapping(bytes32 => Chat) private chats;
    mapping(bytes32 => Archive) private archives;
    mapping(address => Group[]) private userGroups;
    mapping(bytes32 => Message[]) private groupMessages;

    event UserRegistered(address indexed userAddress, string name);
    event MessageSent(bytes32 indexed chatId, address indexed sender, string content, uint256 timestamp);
    event MessageRead(bytes32 indexed chatId, address indexed reader, uint256 messageIndex);
    event MessageDeleted(bytes32 indexed chatId, address indexed deleter, uint256 messageIndex);
    event GroupCreated(string groupName, address[] members);
    event UserStatusUpdated(address indexed userAddress, string newStatus);
    event UserProfilePictureUpdated(address indexed userAddress, string newProfilePicture);
    event ChatArchived(bytes32 indexed chatId, address indexed userAddress, bool isArchived);




    function userRegistration(address userAddress, string memory name) external {
        require(users[userAddress].userAddress == address(0), "User already registered");
        require(bytes(name).length > 0, "Name cannot be empty");
        users[userAddress] = User(name, "", "", userAddress, 0);
        emit UserRegistered(userAddress, name);
    }

    function checkUserExists(address userAddress) external view returns (bool) {
        return users[userAddress].userAddress != address(0);
    }

    function deleteUser(address userAddress) external {
        require(users[userAddress].userAddress != address(0), "User not found");
        delete users[userAddress];
    }

    function blockUser(address userAddress) external {
        require(users[userAddress].userAddress != address(0), "User not found");
        delete users[userAddress];
    }

    function sendMessage(address _sender, address _receiver, string memory content, bool isMedia) external {
        require(users[_sender].userAddress != address(0), "Sender not registered");
        require(users[_receiver].userAddress != address(0), "Receiver not registered");
        bytes32 chatId = keccak256(abi.encodePacked(_sender, _receiver));
        chats[chatId].messages.push(Message(_sender, content, block.timestamp, false, false, isMedia));
        emit MessageSent(chatId, _sender, content, block.timestamp);
        if (chats[chatId].messages.length == 1) {
            chats[chatId].sender = _sender;
            chats[chatId].receiver = _receiver;
        }
    }

    function readMessage(bytes32 chatId, uint256 messageIndex) external {
        require(chats[chatId].messages.length > messageIndex, "Message index out of bounds");
        require(chats[chatId].receiver == msg.sender || chats[chatId].sender == msg.sender, "Not a participant in this chat");
        chats[chatId].messages[messageIndex].isRead = true;
        emit MessageRead(chatId, msg.sender, messageIndex);
    }


    function deleteMessage(bytes32 chatId, uint256 messageIndex, address deleter) external {
        require(chats[chatId].messages.length > messageIndex, "Message index out of bounds");
        if (chats[chatId].messages[messageIndex].sender == deleter) {
            chats[chatId].messages[messageIndex].isDeleted = true;
            emit MessageDeleted(chatId, deleter, messageIndex);
        } else if (chats[chatId].receiver == deleter || chats[chatId].sender == deleter) {
            chats[chatId].messages[messageIndex].isDeleted = true;
            emit MessageDeleted(chatId, deleter, messageIndex);
        } else {
            revert("only sender or receiver can delete this message");
        }
    }

    function createGroup(string memory groupName, address[] memory members, string memory groupDescription, address admin) external {
        require(bytes(groupName).length > 0, "Group name cannot be empty");
        require(members.length > 1, "A group must have at least two members");
        require(users[admin].userAddress != address(0), "Admin must be a registered user");
        for (uint256 i = 0; i < members.length; i++) {
            require(users[members[i]].userAddress != address(0), "All members must be registered users");
        }
        bytes32 groupId = keccak256(abi.encodePacked(groupName, members, block.timestamp));
        Group memory newGroup = Group(groupName, members, groupId, groupDescription, admin);
        for (uint256 i = 0; i < members.length; i++) {
            userGroups[members[i]].push(newGroup);
        }
        emit GroupCreated(groupName, members);
    }
    // leave group
    function leaveGroup(bytes32 groupId, address member) external {
        bool isMember = false;
        Group[] storage groups = userGroups[member];
        for (uint256 i = 0; i < groups.length; i++) {
            if (groups[i].groupId == groupId) {
                isMember = true;
                // Remove member from group
                groups[i] = groups[groups.length - 1];
                groups.pop();
                break;
            }
        }
        require(isMember, "Member not found in the group");
        userGroups[member] = groups;
    }


    // create a new admin,this will be done by the current admin
    function createNewAdmin(bytes32 groupId, address newAdmin, address currentAdmin) external {
        bool isMember = false;
        Group[] storage groups = userGroups[currentAdmin];
        for (uint256 i = 0; i < groups.length; i++) {
            if (groups[i].groupId == groupId) {
                isMember = true;
                require(groups[i].admin == currentAdmin, "Only current admin can create new admin");
                groups[i].admin = newAdmin;
                break;
            }
        }
        require(isMember, "Current admin not found in the group");
        userGroups[currentAdmin] = groups;
    }



    // change group admin
    function changeGroupAdmin(bytes32 groupId, address newAdmin, address currentAdmin) external {
        bool isMember = false;
        Group[] storage groups = userGroups[currentAdmin];
        for (uint256 i = 0; i < groups.length; i++) {
            if (groups[i].groupId == groupId) {
                isMember = true;
                require(groups[i].admin == currentAdmin, "Only current admin can change admin");
                groups[i].admin = newAdmin;
                break;
            }
        }
        require(isMember, "Current admin not found in the group");
        userGroups[currentAdmin] = groups;
    }





    function sendGroupMessage(bytes32 groupId, address  _sender, string memory content, bool isMedia) external {
        bool isMember = false;
        Group[] memory groups = userGroups[_sender];
        for (uint256 i = 0; i < groups.length; i++) {
            if (groups[i].groupId == groupId) {
                isMember = true;
                break;
            }
        }
        require(isMember, "Sender is not a member of the group");
        groupMessages[groupId].push(Message(_sender, content, block.timestamp, false, false, isMedia));
        emit MessageSent(groupId, _sender, content, block.timestamp);
    }

    function deleteGroup(bytes32 groupId, address admin) external {
        bool isAdmin = false;
        Group[] storage groups = userGroups[admin];
        for (uint256 i = 0; i < groups.length; i++) {
            if (groups[i].groupId == groupId) {
                isAdmin = true;
                require(groups[i].admin == admin, "Only admin can delete the group");
                // Remove group from all members
                for (uint256 j = 0; j < groups[i].members.length; j++) {
                    address member = groups[i].members[j];
                    Group[] storage memberGroups = userGroups[member];
                    for (uint256 k = 0; k < memberGroups.length; k++) {
                        if (memberGroups[k].groupId == groupId) {
                            memberGroups[k] = memberGroups[memberGroups.length - 1];
                            memberGroups.pop();
                            break;
                        }
                    }
                    userGroups[member] = memberGroups;
                }
                break;
            }
        }
        require(isAdmin, "Admin not found in the group");
        userGroups[admin] = groups;
        delete groupMessages[groupId];
    }

    function deleteGroupMessage(bytes32 groupId, uint256 messageIndex, address deleter) external {
        require(groupMessages[groupId].length > messageIndex, "Message index out of bounds");
        bool isMember = false;
        Group[] memory groups = userGroups[deleter];
        for (uint256 i = 0; i < groups.length; i++) {
            if (groups[i].groupId == groupId) {
                isMember = true;
                break;
            }
        }
        require(isMember, "Deleter is not a member of the group");
        if (groupMessages[groupId][messageIndex].sender == deleter) {
            groupMessages[groupId][messageIndex].isDeleted = true;
            emit MessageDeleted(groupId, deleter, messageIndex);
        } else {
            revert("only sender can delete this message");
        }
    }

    function markGroupMessageAsRead(bytes32 groupId, uint256 messageIndex, address reader) external {
        require(groupMessages[groupId].length > messageIndex, "Message index out of bounds");
        bool isMember = false;
        Group[] memory groups = userGroups[reader];
        for (uint256 i = 0; i < groups.length; i++) {
            if (groups[i].groupId == groupId) {
                isMember = true;
                break;
            }
        }
        require(isMember, "Reader is not a member of the group");
        groupMessages[groupId][messageIndex].isRead = true;
        emit MessageRead(groupId, reader, messageIndex);
    }

    function getGroupMessages(bytes32 groupId) external view returns (Message[] memory) {
        return groupMessages[groupId];
    }

    function getUserGroups(address userAddress) external view returns (Group[] memory) {
        return userGroups[userAddress];
    }

    function getChatMessages(bytes32 chatId) external view returns (Message[] memory) {
        return chats[chatId].messages;
    }


    function userStatus(address userAddress, string memory newStatus, uint256 _time) external {
        require(users[userAddress].userAddress != address(0), "User not found");
        _time = block.timestamp + (_time * DAY_IN_SECONDS);
        users[userAddress].status = newStatus;
        users[userAddress].statusExpiry = _time;
        if (bytes(newStatus).length == 0) {
            users[userAddress].statusExpiry = 0;
            revert("Status cannot be empty");
        } else {
            users[userAddress].statusExpiry = _time;
        }
        emit UserStatusUpdated(userAddress, newStatus);
    }


    function updateProfilePicture(address userAddress, string memory newProfilePicture) external {
        require(users[userAddress].userAddress != address(0), "User not found");
        users[userAddress].profilePicture = newProfilePicture;
        emit UserProfilePictureUpdated(userAddress, newProfilePicture);
    }
    function archiveChat(bytes32 chatId, address userAddress, bool isArchived) external {
        require(chats[chatId].sender == userAddress || chats[chatId].receiver == userAddress, "Not a participant in this chat");
        archives[chatId] = Archive(chatId, isArchived);
        emit ChatArchived(chatId, userAddress, isArchived);
    }

    function getUser(address userAddress) external view returns (User memory) {
        require(users[userAddress].userAddress != address(0), "User not found");
        return users[userAddress];
    }

    function deleteAccount(address _userAddress, string memory _reason) private returns (string memory) {
        require(users[_userAddress].userAddress != address(0), "User not found");
        delete users[_userAddress];
        return _reason;
    }
}