showHUD [false,false,false,false,false,false,false,false]
showHUD [true,true,true,true,true,true,true,true]

Sheep_random_F



["refreshPoints", "onEachFrame", 
{
    _nearestTargets = nearestObjects [_this select 0, ["Sheep_random_F"], 300]; 
     
    { 
        _sPos = worldToScreen(getPos _x); 
        _screenW = getResolution select 0; 
        _screenH = getResolution select 1; 
        _sPosX = _sPos select 0;
        _sPosY = _sPos select 1;

        _bX = ((_sposX - safeZoneXAbs) / (safeZoneWAbs)) * _screenW;
        _bY = ((_sposY - safeZoneY) / (safeZoneH)) * _screenH; 
        cutText [str([_bX, _bY]), "PLAIN", 0]; 
        diag_log str([_bX, _bY]);
    } forEach _nearestTargets; 
}, 
[player]] call BIS_fnc_addStackedEventHandler;

["refreshPoints", "onEachFrame"] call BIS_fnc_removeStackedEventHandler;


// this kind of works \/

_screenPos = worldToScreen position mySoldier;  
_screenX = _screenPos select 0;  
_screenY = _screenPos select 1;  
_myX = (_screenX - safeZoneXAbs) / (safeZoneWAbs); 
_myY = (_screenY - safeZoneY) / (safeZoneH); 


hint format [
    "X: %1 Y: %2",
    round (_myX * (getResolution select 0)),
    round (_myY * (getResolution select 1))
];


//---------------------


_result = "extDB3" callExtension "9:ADD_DATABASE:Database";

if(!(_result isEqualTo "[1]")) exitWith {diag_log "extDB3: Error with Database Connection";};


_result = "extDB3" callExtension "9:ADD_DATABASE_PROTOCOL:Database:SQL:SQL";
if(!(_result isEqualTo "[1]")) exitWith {diag_log "extDB3: Error with Database Connection";};


_ret = "extDB3" callExtension "0:SQL:SELECT * FROM frames";


"extDB3" callExtension "9:ADD_DATABASE:arma3";
"extDB3" callExtension "9:ADD_DATABASE_PROTOCOL:Database:SQL:SQL";
"extDB3" callExtension "0:SQL:SELECT * FROM frames";


//-----------------------

_result = "extDB3" callExtension "9:ADD_DATABASE:Database";

if(!(_result isEqualTo "[1]")) exitWith {diag_log "extDB3: Error with Database Connection";};


_result = "extDB3" callExtension "9:ADD_DATABASE_PROTOCOL:Database:SQL:SQL";
if(!(_result isEqualTo "[1]")) exitWith {diag_log "extDB3: Error with Database Connection";};

["refreshPoints", "onEachFrame", 
{
    _nearestTargets = nearestObjects [_this select 0, ["Sheep_random_F"], 10000]; 
    _positionsArr = [];

    { 
        _sPos = worldToScreen(getPos _x); 
        _screenW = getResolution select 0; 
        _screenH = getResolution select 1; 
        _sPosX = _sPos select 0;
        _sPosY = _sPos select 1;

        _bX = ((_sposX - safeZoneXAbs) / (safeZoneWAbs)) * _screenW;
        _bY = ((_sposY - safeZoneY) / (safeZoneH)) * _screenH; 
        _posArr = [_forEachIndex, _bX, _bY];

        _positionsArr pushBack _posArr;
        diag_log _positionsArr;
    } forEach _nearestTargets; 

    _fullStr = _positionsArr;
    _frameNo = round (diag_frameNo % diag_fps);

    _query = format ["2:SQL:INSERT INTO `arma3`.`frames` (`frame`, `objects`) VALUES (%1, '%2')", _frameno, _fullStr];
    "extDB3" callExtension _query;
}, 
[player]] call BIS_fnc_addStackedEventHandler;

[] spawn { 
	waitUntil {inputAction "pushToTalk" > 0};   
	["refreshPoints", "onEachFrame"] call BIS_fnc_removeStackedEventHandler; // REMOVE HANDLER AFTER ONE GO
};