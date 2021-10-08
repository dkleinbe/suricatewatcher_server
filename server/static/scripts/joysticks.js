

var s = function (sel) { return document.querySelector(sel); };
var sId = function (sel) { return document.getElementById(sel); };
var removeClass = function (el, clss) {
    el.className = el.className.replace(new RegExp('\\b' + clss + ' ?\\b', 'g'), '');
}


var els = [];
var elDump = [];

function initJoysticks() {

    var joystickL = nipplejs.create({
        zone: document.getElementById('left'),
        mode: 'dynamic',
        position: { left: '20%', top: '50%' },
        shape: 'circle',
        restJoystick: false,
        color: 'green',
        size: 200
    });
    
    var joystickR = nipplejs.create({
        zone: document.getElementById('right'),
        mode: 'dynamic',
        position: { left: '80%', top: '50%' },
        color: 'red',
        size: 200
    });
    
    mapDebug(joystickL);
    mapDebug(joystickR);

    bindNipple(joystickL);
    bindNipple(joystickR);
}


function mapDebug(js) {
    var div_id = js.options.zone.id
    var elDebug = sId(div_id + '_debug');
    elDump[div_id] = elDebug.querySelector('.dump');
    els[div_id] = {
        position: {
            x: elDebug.querySelector('.position .x .data'),
            y: elDebug.querySelector('.position .y .data')
        },
        force: elDebug.querySelector('.force .data'),
        pressure: elDebug.querySelector('.pressure .data'),
        distance: elDebug.querySelector('.distance .data'),
        vector: {
            x: elDebug.querySelector('.vector .x .data'),
            y: elDebug.querySelector('.vector .y .data'),
        },
        angle: {
            radian: elDebug.querySelector('.angle .radian .data'),
            degree: elDebug.querySelector('.angle .degree .data')
        },
        direction: {
            x: elDebug.querySelector('.direction .x .data'),
            y: elDebug.querySelector('.direction .y .data'),
            angle: elDebug.querySelector('.direction .angle .data')
        }
    }
}

function bindNipple (joystick) {
    joystick.on('start end', function (evt, data) {
        dump(evt.type, joystick.options.zone.id);
        //debug(data, joystick.options.zone.id);
        joystick_state(evt, joystick.options.zone.id, data, );
    }).on('move', function (evt, data) {
        //debug(data, joystick.options.zone.id);
        joystick_move(data, joystick.options.zone.id);
    }).on('dir:up plain:up dir:left plain:left dir:down ' +
        'plain:down dir:right plain:right',
        function (evt, data) {
            //dump(evt.type, joystick.options.zone.id);
        }
    ).on('pressure', function (evt, data) {
        //debug({pressure: data});
    });
}
function joystick_state(evt, id, data) {
    setTimeout(function() {
        socket_cmd.emit('joystick_state', { evt : evt, joystick_id : id, data : data });
    }, 0);
}            
function joystick_move(data, id) {
    setTimeout(function() {
        socket_cmd.emit('joystick_move', { joystick_id : id, data : data });
    }, 0);
}

// Print data into elements
function debug (obj, zone_id) {
    function parseObj(sub, el) {
        for (var i in sub) {
            if (typeof sub[i] === 'object' && el) {
                parseObj(sub[i], el[i]);
            } else if (el && el[i]) {
                el[i].innerHTML = sub[i];
            }
        }
    }
    setTimeout(function () {
        parseObj(obj, els[zone_id]);
    }, 0);
}

var nbEvents = 0;

// Dump data
function dump (evt, id) {
    setTimeout(function () {
        if (elDump[id].children.length > 4) {
            elDump[id].removeChild(elDump[id].firstChild);
        }
        var newEvent = document.createElement('div');
        newEvent.innerHTML = '#' + nbEvents + ' : <span class="data">' +
            evt + '</span>';
            elDump[id].appendChild(newEvent);
        nbEvents += 1;
    }, 0);
}            
