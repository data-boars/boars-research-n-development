showHUD [false,false,false,false,false,false,false,false]
showHUD [true,true,true,true,true,true,true,true]


//-----------------------


_result = "extDB3" callExtension "9:ADD_DATABASE:Database";

if(!(_result isEqualTo "[1]")) exitWith {diag_log "extDB3: Error with Database Connection";};


_result = "extDB3" callExtension "9:ADD_DATABASE_PROTOCOL:Database:SQL:SQL";
if(!(_result isEqualTo "[1]")) exitWith {diag_log "extDB3: Error with Database Connection";};


// Method #1 - capturing using external software
// ----------------------------------------------------------

[] spawn { 
    _nearestTargets = nearestObjects [player, ["Sheep_random_F"], 10000]; 
	waitUntil {inputAction "pushToTalk" > 0};
    ["refreshPoints", "onEachFrame", 
    {
        _positionsArr = [];
        _nearestTargets = _this select 1;

        hint str(_nearestTargets);
        { 
            _sPos = worldToScreen(getPos _x); 
            _bX = -9000;
            _bY = -9000; 
            if (count _sPos > 1) then { // If target 
                hint "a";
                _screenW = getResolution select 0; 
                _screenH = getResolution select 1; 
                _sPosX = _sPos select 0;
                _sPosY = _sPos select 1;

                _bX = ((_sposX - safeZoneXAbs) / (safeZoneWAbs)) * _screenW;
                _bY = ((_sposY - safeZoneY) / (safeZoneH)) * _screenH; 
            };

            _posArr = [_forEachIndex, _bX, _bY];

            _positionsArr pushBack _posArr;
            diag_log _positionsArr;
        } forEach _nearestTargets; 

        _fullStr = _positionsArr;
        _frameNo = round (diag_frameNo % diag_fps);

        _query = format ["2:SQL:INSERT INTO `arma3`.`frames` (`frame`, `objects`) VALUES (%1, '%2')", _frameno, _fullStr];
        "extDB3" callExtension _query;
    }, 
    [player, _nearestTargets]] call BIS_fnc_addStackedEventHandler;

    sleep 1;
    waitUntil {inputAction "pushToTalk" > 0};
    ["refreshPoints", "onEachFrame"] call BIS_fnc_removeStackedEventHandler; // REMOVE HANDLER AFTER ONE GO
};


// Method #2 - capturing screenshots directly from ArmA
// ----------------------------------------------------------

[] spawn { 
    _nearestTargets = nearestObjects [player, ["Sheep_random_F", "C_man_hunter_1_F", "C_man_polo_1_F"], 10000]; 
    waitUntil {inputAction "pushToTalk" > 0};
    ["refreshPoints", "onEachFrame", 
    {
        _positionsArr = [];
        _nearestTargets = _this select 1;

        hint str(_nearestTargets);
        { 
            _sPos = worldToScreen(getPos _x); 
            _bX = -9000;
            _bY = -9000; 
            if (count _sPos > 1) then { // If target 
                hint "a";
                _screenW = getResolution select 0; 
                _screenH = getResolution select 1; 
                _sPosX = _sPos select 0;
                _sPosY = _sPos select 1;

                _bX = ((_sposX - safeZoneXAbs) / (safeZoneWAbs)) * _screenW;
                _bY = ((_sposY - safeZoneY) / (safeZoneH)) * _screenH; 
            };

            _posArr = [_forEachIndex, _bX, _bY, typeOf _x];

            _positionsArr pushBack _posArr;
            diag_log _positionsArr;
        } forEach _nearestTargets; 

        _fullStr = _positionsArr;
        // _frameNo = round (diag_frameNo % diag_fps);
        _frameNo = str diag_frameNo;

        _query = format ["2:SQL:INSERT INTO `arma3`.`frames` (`frame`, `objects`) VALUES (%1, '%2')", _frameno, _fullStr];
        "extDB3" callExtension _query;
        screenshot (_frameNo + ".png");    
    }, 
    [player, _nearestTargets]] call BIS_fnc_addStackedEventHandler;

    sleep 1;
    waitUntil {inputAction "pushToTalk" > 0};
    ["refreshPoints", "onEachFrame"] call BIS_fnc_removeStackedEventHandler; // REMOVE HANDLER AFTER ONE GO
};
