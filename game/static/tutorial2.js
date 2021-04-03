initialize("/game/api/startTutorial/", "POST", (game) => {

    // Initialization and globals
    "use strict";
    let maxUser;
    let startTime = performance.now();
    let endTime = performance.now();
    let giveThrMin = 8;
    let giveThrMax = 0.2;
    let maxTurns = 2;
    let tutorialGame = 1;
    let maxAgent;
    let agentTime = 2000;
    let animateTime = 1000;
    let quickTime = 500;
    let waitTime = 1000;
    let currentA = game.capital;
    let currentB = 0;
    let scoreA = 0;
    let scoreB = 0;
    let turn = 1;
    let complete = false
    let isSliding = false;
    let userGives = game.userGives;
    let userKeeps = game.userKeeps;
    let userRewards = game.userRewards;
    let agentGives = game.agentGives;
    let agentKeeps = game.agentKeeps;
    let agentRewards = game.agentRewards;
    maxUser = game.capital;
    maxAgent = 0;  // updated after user moves
    $("#loadGame").remove();
    $("#bar-area").show().children().fadeIn(quickTime);
    $("#imgA").fadeIn(quickTime)
    $("#imgB").fadeIn(quickTime)
    $("#imgA").attr('src', `/static/user${game.avatar}A.svg`);
    $("#ts-box").css('background-color', 'var(--myPink)');
    $("#ys-box").css('background-color', 'var(--myTeal)');
    $("#turn-box1").css('visibility', 'visible');
    $("#turn-text").css('visibility', 'visible');
    $("#bonus-box").css('visibility', 'visible');
    $("#turn-box").show().children().fadeIn(quickTime);
    $("#turn-text").show().fadeIn(quickTime);
    $("#ys-box").show().children().fadeIn(quickTime);
    $("#ts-box").show().children().fadeIn(quickTime);
    $("#bonus-box").show().children().fadeIn(quickTime);
    $(window).resize(resizeSlider);
    $(window).on('beforeunload', function(e) {return false;});
    $(document).mousemove(function(e) {moveSlide(e);});
    $(document).mouseup(function(e) {stopSlide(e);});
    let sliderLeft = document.getElementById("slider-left");
    let sliderThumb = document.getElementById("slider-thumb");
    let sliderRight = document.getElementById("slider-right");

    let notes = $(".note");
    for (let n=0; n<notes.length; n++) {
        notes.eq(n).hide();
        notes.eq(n).append(`<div id='n-nav${n}' class='n-nav'> </div>`);
        $(`#n-nav${n}`).append(`<p id='n-next${n}'class="next">next</p>`);
        $(`#n-next${n}`).click(function() {$(`#n${n}`).fadeOut(quickTime);});
    }

    // Tutorial Sequence
    $("#submit").click(callUpdate);
    $("#n-area").show();
    $("#n0").fadeIn(quickTime);
    $("#n-next0").text("Begin Game 1");
    $("#n-next2").text("Begin Game 2");
    $(`#n-next4`).click(function() {
        $(`#n5`).fadeIn(quickTime);
        $(`#headerG`).addClass('red');
        $(`#headerW`).addClass('green');
        $(`#cash-link`).addClass('black');
    });
    $(`#n-next5`).text("Finish");
    $(`#n-next5`).click(function() {
        $(window).off('beforeunload');
        let form = $("#form");
        let sendData = form.serialize();
        $.ajax({
            method: 'POST',
            url: '/game/api/finishTutorial/',
            data: sendData,
            dataType: 'json',
            success: function (returnData) {
                window.location.href=$("#n5").attr("href");
            }
        });
    });
    $("#n-next0").click(function() {
        $("#turn-box").fadeIn(quickTime);
        $("#ts-box").fadeIn(quickTime);
        $("#ys-box").fadeIn(quickTime);
        $("#bonus-box").fadeIn(quickTime);
        // $("#imgB").css('opacity', '0.5')
        animateTurn();
        executeMove("capital");
        setTimeout(function() {switchToUser();}, animateTime+waitTime);
    });
    $("#n-next2").click(function() {
        // switch players and reset
        tutorialGame = 2;
        game.userRole = "B";
        game.agentRole = "A";
        currentA = 0;
        currentB = 0;
        scoreA = 0;
        scoreB = 0;
        turn = 1;
        complete = false;
        // let wMin = parseInt($(":root").css('--boxWidthMin'));
        // $("#ts-box").css('width', wMin+"vw");
        // $("#ys-box").css('width', wMin+"vw");
        // $("#bonus-box").css('marginLeft', wMin+"vw");
        // $("#ts-num").text('0');
        // $("#ys-num").text('0');
        $("#turn-box1").css('opacity', '0.2');
        $("#turn-box2").css('opacity', '0.2');
        animateScoreA();
        animateScoreB();
        animateBonus();
        animateTurn();

        // animateBonus();
        maxAgent = game.capital;
        maxUser = 0;  // updated after agent moves
        giveThrMin = 0;
        // start a new game with the agent going first
        let form = $("#form");
        let sendData = form.serialize();
        $.ajax({
            method: 'POST',
            url: '/game/api/restartTutorial/',
            data: sendData,
            dataType: 'json',
            success: function (returnData) {
                // update globals
                userGives = returnData.userGives;
                userKeeps = returnData.userKeeps;
                userRewards = returnData.userRewards;
                agentGives = returnData.agentGives;
                agentKeeps = returnData.agentKeeps;
                agentRewards = returnData.agentRewards;
                executeMove("capital");
                setTimeout(function () {switchToAgent(1);}, animateTime);
            }
        });
        // reposition and recolor elements
        $("#imgA").attr('src', `/static/robotA.svg`);
        $("#imgB").attr('src', `/static/user${game.avatar}B.svg`);
        $("#ts-text").css('background-color', 'var(--myTeal)');
        $("#ts-box").css('background-color', 'var(--myTeal)');
        $("#ys-text").css('background-color', 'var(--myPink)');
        $("#ys-box").css('background-color', 'var(--myPink)');
        maxAgent = game.capital;
        maxUser = 0;
        $("#playerA").fadeIn(quickTime);
        $("#playerB").fadeIn(quickTime);
        $("#imgA").fadeIn(quickTime);
        $("#imgB").fadeIn(quickTime);
        clearLog();
        return false;
    });

    // Functions
    // slider 
    let getX = function(e) {
        if (!e) {e = window.event;}
        e.preventDefault();
        if (e.type=='mousemove' || e.type=='mouseup' || e.type=='mousedown') {return e.pageX;}
        if (e.type=='touchmove' || e.type=='touchstart') {return e.touches[0].clientX;}
        if (e.type=='touchend'){return e.changedTouches[0].clientX;}
    }
    let startSlide = function(e) {
        isSliding = true;
        $("#submit").prop('disabled', false);
        updateSliderMouse();
    }
    let moveSlide = function(e) {
        if (isSliding) {updateSliderMouse(e); return false;}
    }
    let stopSlide = function(e) {
        isSliding = false;
        let x = getX(e);
        let f = absToRel(x);
    }
    let absToRel = function(x) {
        let widthD = Number($(window).width());  // in px
        let widthW = parseInt($(":root").css('--widthSlider'));  // in vw
        let widthT = parseInt($(":root").css('--widthT'));  // in vw
        let wW = widthW / 100 * widthD;  // in px
        let wT = widthT / 100 * widthD;  // in px
        let leftEdge = $("#slider-wrapper").offset().left - wT/2;
        let rightEdge = $("#slider-wrapper").offset().left + wW - wT/2;
        // console.log(wW, wT);
        // console.log(leftEdge, rightEdge);
        // console.log(x);
        if ($("#slider-wrapper").hasClass('flipped')) {
            if (x <= leftEdge) {return 1;}
            else if (x >= rightEdge) {return 0;}
            else {return 1 - (x-leftEdge)/wW;}
        }
        else {
            if (x <= leftEdge) {return 0;}
            else if (x >= rightEdge) {return 1;}
            else {return (x-leftEdge)/wW;}            
        }
    }
    let updateSliderMouse = function(e) {
        let x = getX(e);
        let f = absToRel(x);
        updateSlider(f, maxUser, game.userRole);
    }
    let updateSlider = function(f, max, player) {
        let widthD = Number($(window).width());  // in px
        let widthW = parseInt($(":root").css('--widthSlider'));  // in vw
        let widthT = parseInt($(":root").css('--widthT'));  // in vw
        let wW = widthW / 100 * widthD;  // in px
        let wT = widthT / 100 * widthD;  // in px
        let leftEdge = $("#slider-wrapper").offset().left - wT/2;
        let rightEdge = $("#slider-wrapper").offset().left + wW - wT/2;
        let val = Math.round(f*max);
        let widthLNew = Math.max(0, f * wW - wT);
        let marginTNew = Math.max(0, f * wW - wT);
        let widthRNew = Math.min((1-f) * wW, wW-wT);
        let marginRNew = Math.max(wT, widthLNew+wT);
        if (player=="A"){
            let sendA = max-val;
            let sendB = val*game.match;
            for (let i=0; i<=game.capital*game.match; i++) {
                if (i<=sendA) {$("#c"+i+"a").css('opacity', '1');}
                else if (i<=max){$("#c"+i+"a").css('opacity', '0.3');}
                else {$("#c"+i+"a").css('opacity', '0');}
                if (i<=sendB) {$("#c"+i+"b").css('opacity', '0.3');}
                else {$("#c"+i+"b").css('opacity', '0');}
                if (game.userRole=="A"){
                    $("#sendA").text("Keep "+sendA);
                    $("#sendB").text("Send "+sendB);
                }
                else {
                    $("#sendA").text("Keep "+sendA);
                    $("#sendB").text("Send "+sendB);
                }
            }            
        }
        else {
            let sendA = val;
            let sendB = max-val;
            for (let i = 0; i <= currentB; i++) {
                if (i<=currentA) {$("#c"+i+"a").css('opacity', '1');}
                else if (i<=(currentA+sendA)){$("#c"+i+"a").css('opacity', '0.3');}
                else {$("#c"+i+"a").css('opacity', '0');}
                if (i<sendA) {$("#c"+(currentB-i)+"b").css('opacity', '0.3');}
                else if (i<=currentB){$("#c"+(currentB-i)+"b").css('opacity', '1');}
                else {$("#c"+i+"b").css('opacity', '0');}
                if (game.userRole=="B"){
                    $("#sendA").text("Send "+sendA);
                    $("#sendB").text("Keep "+sendB);
                }
                else {
                    $("#sendA").text("Send "+sendA);
                    $("#sendB").text("Keep "+sendB);
                }
            }
        }  
        $("#slider-wrapper").attr('val', Math.round(f*max));
        $("#slider-left").css('width', widthLNew);
        $("#slider-thumb").css('marginLeft', marginTNew);
        $("#slider-right").css('width', widthRNew);
        $("#slider-right").css('marginLeft', marginRNew);
    }
    // when user resizes window, resize slider appropriately
    function resizeSlider() {
        let widthD = Number($(window).width());  // in px
        let widthW = parseInt($(":root").css('--widthSlider'));  // in vw
        let widthT = parseInt($(":root").css('--widthT'));  // in vw
        let wW = widthW / 100 * widthD;  // in px
        let wT = widthT / 100 * widthD;  // in px
        let leftEdge = $("#sendB").offset().left - wT/2;
        let rightEdge = $("#sendB").offset().left + wW - wT/2;
        let val = Number($("#slider-wrapper").attr('val'));
        let max = Number($("#slider-wrapper").attr('max'));
        let f = val / max;
        let widthLNew = Math.max(0, f * wW - wT);
        let marginTNew = Math.max(0, f * wW - wT);
        let widthRNew = Math.min((1-f) * wW, wW-wT);
        let marginRNew = Math.max(wT, widthLNew+wT);
        $("#slider-left").css('width', widthLNew);
        $("#slider-thumb").css('marginLeft', marginTNew);
        $("#slider-right").css('width', widthRNew);
        $("#slider-right").css('marginLeft', marginRNew); 
    }

    // Change view after the user or agent moves
    function switchToAgent(userGive) {
        let agentGive = agentGives[agentGives.length-1];
        let agentKeep = agentKeeps[agentKeeps.length-1];
        if (userGive==0 & game.userRole=="A") {
            updateLog("B", 0, 0);
            finishTurn();
        }
        else {
            let skip = (agentGive==0);
            $("#loading").fadeIn(quickTime);
            setTimeout(function() {
                $("#loading").fadeOut(quickTime);
                showSlider(game.agentRole, agentGive, agentKeep, false);
                executeMove(game.agentRole, agentGive, agentKeep, skip);
            }, agentTime);
            setTimeout(function() {hideSlider();}, animateTime+agentTime+waitTime);
        }
        let wait;
        // if (userGive==0 & game.agentRole=="A") {wait = 5*animateTime;}  // userGive doesn't matter in this case
        if (userGive==0 & game.agentRole=="B") {wait = 2*animateTime;}  // agent is skipped
        else if (agentGive==0 & game.agentRole=="A") {wait = agentTime;}
        else if (agentGive==0 & game.agentRole=="B") {wait = 3*animateTime+agentTime;}
        else if (agentGive>0 & game.agentRole=="A") {wait = animateTime+agentTime+waitTime;}
        else if (agentGive>0 & game.agentRole=="B") {wait = 4*animateTime+agentTime;}
        if (!complete) {setTimeout(function() {switchToUser();}, wait);}
    }

    function switchToUser() {
        if (game.userRole=="B"){maxUser = game.match*agentGives[agentGives.length-1];}
        if (maxUser>0) {
            if (game.userRole=="A"){
                startTime = performance.now(); showSlider(game.userRole, 0, maxUser, true);
            }
            else {setTimeout(function () {
                startTime = performance.now(); showSlider(game.userRole, 0, maxUser, true);}, 1.5*quickTime);
            }
        }
        else {
            startTime = performance.now();
            $("#slider-wrapper").attr('val', 0); callUpdate();
        }
    }


    // Communicate with the server through AJAX (views.updateGame())
    function callUpdate() {
        let userGive = Number($("#slider-wrapper").attr('val'));
        let userKeep = maxUser - userGive;
        if (userGive<giveThrMin & tutorialGame==1) {
            hideSlider();
            $("#warning").text(`Please give at least ${giveThrMin*game.match}`);
            $("#warning").fadeIn(quickTime);
            setTimeout(function(){
                fastCoins(game.capital, "a");
                $("#warning").fadeOut(quickTime);
                showSlider(game.userRole, 0, maxUser, true);
            }, animateTime+waitTime);
            return;
        }
        if (userGive>giveThrMax*maxUser & tutorialGame==2) {
            hideSlider();
            $("#warning").text(`Please keep at least ${((1-giveThrMax)*maxUser).toFixed(0)}`);
            $("#warning").fadeIn(quickTime);
            setTimeout(function(){
                fastCoins(currentA, "a");
                fastCoins(currentB, "b");
                $("#warning").fadeOut(quickTime);
                showSlider(game.userRole, 0, maxUser, true);
            }, animateTime+waitTime);
            return;
        }
        let userTime = 0;
        userGives.push(userGive);
        userKeeps.push(userKeep);
        if (game.userRole == "A") {maxAgent = userGive * game.match} // update global
        $("#submit").hide();        
        setTimeout(function() {hideSlider();}, animateTime);
        let skip = (userGive==0);
        executeMove(game.userRole, userGive, userKeep, skip);
        let form = $("#form");
        let giveData = $('<input type="hidden" name="userGive"/>').val(userGive);
        let keepData = $('<input type="hidden" name="userKeep"/>').val(userKeep);
        let timeData = $('<input type="hidden" name="userTime"/>').val(userTime);
        form.append(giveData);
        form.append(keepData);
        form.append(timeData);
        let sendData = form.serialize();
        $.ajax({
            method: 'POST',
            url: '/game/api/updateTutorial/',
            data: sendData,
            dataType: 'json',
            success: function (returnData) {
                // update globals
                userGives = returnData.userGives;
                userKeeps = returnData.userKeeps;
                userRewards = returnData.userRewards;
                agentGives = returnData.agentGives;
                agentKeeps = returnData.agentKeeps;
                agentRewards = returnData.agentRewards;
                if (userGives.length >= maxTurns & agentGives.length >= maxTurns){complete = true;}
                if (!complete || game.userRole=="A") {
                    let wait;
                    if (userGive==0 & game.userRole=="A"){wait=0;}
                    else if (userGive==0 & game.userRole=="B"){wait=4*animateTime;}
                    else if (userGive>0 & game.userRole=="A"){wait=animateTime;}
                    else if (userGive>0 & game.userRole=="B") {wait=4*animateTime;}
                    setTimeout(function () {switchToAgent(userGive);}, wait+waitTime);
                }
            }
        });
        return false;
    }

    // Start new turn
    function finishTurn() {
        // todo: alignment check
        scoreA += currentA;
        scoreB += currentB;
        updateLog("score", currentA, currentB);
        animateCoins(0, currentA, -currentA, 'out', 'a');
        animateCoins(0, currentB, -currentB, 'out', 'b');
        animateScoreA();
        animateScoreB();
        animateBonus()
        currentA = 0;
        currentB = 0;
        turn++;
        if (complete) {
            setTimeout(()=> {finishGame();}, animateTime);
        }
        else {
            animateTurn();
            setTimeout(()=> {executeMove('capital');}, animateTime);
        }
    }

    // Animate coin appearing and disappearing
    function animateCoins(i, start, delta, direction, player) {
        let di;
        let opacity;
        if (direction=="in"){
            if (i>delta) {return;} // base case
            di = 1; // count up
            opacity = '1';  // become visible
        }
        else {
            if (i<=delta) {return;} // base case            
            di = -1;  // count down
            opacity = '0';  // become invisible
        }
        setTimeout(() => {
            $("#c"+(start+i)+player).css('opacity', opacity);
            animateCoins(i+di, start, delta, direction, player); // recursive call
        }, animateTime/Math.abs(delta));   
    }
    function fastCoins(delta, player) {
        for (let i=1; i<=game.capital*game.match; i++){
            if (i<=delta){$("#c"+i+player).css('opacity', "1");}
            else {$("#c"+i+player).css('opacity', "0");}
        }
    } 
    function executeMove(move, give=null, keep=null, skip=false){
        if (move=="capital") {
            updateLog("capital", game.capital, 0);
            animateCoins(0, 0, game.capital, 'in', 'a');
            currentA = game.capital;
        }
        if (move=="A"){
            updateLog("A", give, keep);
            if (!skip) {
                animateCoins(0, game.capital, -give, 'out', 'a');
                animateCoins(0, 0, give*game.match, 'in', 'b');
                currentA = keep;
                currentB = game.match*give;
            }
        }
        if (move=="B") {
            updateLog("B", give, keep);
            if (!skip) {
                animateCoins(0, currentB, -give, 'out', 'b');
                animateCoins(1, currentA, give, 'in', 'a');
                currentA += give;
                currentB -= give;
            }
            let wait = (skip) ? waitTime: animateTime+waitTime
            setTimeout(()=> {finishTurn();}, wait);
        }
    }

    function showSlider(player, give, keep, isUser) {
        if (isUser) {          
            $("#slider-thumb").mousedown(startSlide);
            $("#slider-left").mousedown(startSlide);
            $("#slider-right").mousedown(startSlide);
            sliderLeft.addEventListener("touchstart", startSlide, false);
            sliderLeft.addEventListener("touchmove", moveSlide, false);
            sliderLeft.addEventListener("touchend", stopSlide, false);
            sliderThumb.addEventListener("touchstart", startSlide, false);
            sliderThumb.addEventListener("touchmove", moveSlide, false);
            sliderThumb.addEventListener("touchend", stopSlide, false);
            sliderRight.addEventListener("touchstart", startSlide, false);
            sliderRight.addEventListener("touchmove", moveSlide, false);
            sliderRight.addEventListener("touchend", stopSlide, false);
            $("#submit").fadeIn(quickTime);
            $("#slider-wrapper").css('opacity', "1");
            $("#slider-thumb").css('background-color', "var(--myYellow)");
            $("#slider-left").hover(function() {$(this).css('cursor','pointer');});
            $("#slider-thumb").hover(function() {$(this).css('cursor','pointer');});
            $("#slider-right").hover(function() {$(this).css('cursor','pointer');});
        }
        else {
            $("#slider-wrapper").css('opacity', "0.7");
            $("#slider-thumb").css('background-color', "var(--myGray)");
            $("#slider-left").hover(function() {$(this).css('cursor','not-allowed');});
            $("#slider-thumb").hover(function() {$(this).css('cursor','not-allowed');});
            $("#slider-right").hover(function() {$(this).css('cursor','not-allowed');});
        }
        let max = give + keep;
        let f = give / max;
        $("#submit").prop('disabled', true);  // until slider moves
        $("#slider-wrapper").attr('min', 0);
        $("#slider-wrapper").attr('max', max);
        $("#slider-wrapper").attr('val', give);
        $("#slider-wrapper").fadeIn(quickTime);
        $("#sendA").fadeIn(quickTime);
        $("#sendB").fadeIn(quickTime);
        updateSliderDirection(player);
        updateSlider(f, max, player);
    }
    function hideSlider() {
        $("#submit").prop('disabled', true);
        $("#slider-thumb").off();  // unbinds mousedown event handler
        $("#slider-left").off();
        $("#slider-right").off();
        sliderLeft.removeEventListener("touchstart", startSlide);
        sliderLeft.removeEventListener("touchmove", moveSlide);
        sliderLeft.removeEventListener("touchend", stopSlide);
        sliderThumb.removeEventListener("touchstart", startSlide);
        sliderThumb.removeEventListener("touchmove", moveSlide);
        sliderThumb.removeEventListener("touchend", stopSlide);
        sliderRight.removeEventListener("touchstart", startSlide);
        sliderRight.removeEventListener("touchmove", moveSlide);
        sliderRight.removeEventListener("touchend", stopSlide);
        $("#slider-wrapper").fadeOut(quickTime);
        $("#submit").fadeOut(quickTime);
        $("#sendA").fadeOut(quickTime);
        $("#sendB").fadeOut(quickTime);
    }
    function updateSliderDirection(player) {
        if (player=="A") {
            $(":root").css('--colorLeft', 'var(--myPink');
            $(":root").css('--colorRight', 'var(--myTeal');
            $(":root").css('--imageLeft', 'var(--PinkLeft)');  // because slider-left is flipped
            $(":root").css('--imageRight', 'var(--TealLeft)');
            $("#slider-wrapper").removeClass('flipped');
        }
        else {
            $(":root").css('--colorLeft', 'var(--myTeal');
            $(":root").css('--colorRight', 'var(--myPink');
            $(":root").css('--imageLeft', 'var(--TealLeft)');  // because slider-left is flipped
            $(":root").css('--imageRight', 'var(--PinkLeft)');
            $("#slider-wrapper").addClass('flipped');
        }
    }

    // Update game log
    function updateLog(stage, give, keep) {
        let pronoun1a = (game.userRole=="A") ? "You" : "They";
        let pronoun1b = (game.userRole=="A") ? "They" : "You";
        let pronoun2 = (game.userRole=="A") ? "you" : "them";
        let currentUser = (game.userRole=="A") ? give : keep;
        let currentAgent = (game.userRole=="A") ? keep : give;
        if (stage=="capital") {
            $(`#c${turn}r1`).text(`Turn ${turn}`);
            $(`#c${turn}r2a`).text(pronoun1a).append("&nbsp;");
            $(`#c${turn}r2b`).text("received "+give).append("&nbsp;");
            $(`#c${turn}r2b`).addClass("teal");
            $(`#c${turn}r2c`).text("coins to start");
            $(`#l${turn}r1`).fadeIn(quickTime);
            $(`#c${turn}r2`).fadeIn(quickTime);
        }
        else if (stage=="A") {
            $(`#c${turn}r3a`).text(pronoun1a).append("&nbsp;");
            $(`#c${turn}r3b`).text("gave "+give).append("&nbsp;");
            $(`#c${turn}r3b`).addClass("pink");
            $(`#c${turn}r3c`).text("coins and").append("&nbsp;");
            $(`#c${turn}r3d`).text("kept "+keep).append("&nbsp;");
            $(`#c${turn}r3d`).addClass("teal");
            $(`#c${turn}r4a`).text(pronoun1b).append("&nbsp;");
            $(`#c${turn}r4b`).text("received "+give*game.match).append("&nbsp;");
            $(`#c${turn}r4b`).addClass("pink");
            $(`#c${turn}r4c`).text("coins from").append("&nbsp;").append(pronoun2);
            $(`#c${turn}r3`).fadeIn(quickTime);
            $(`#c${turn}r4`).fadeIn(quickTime);
        }
        else if (stage=="B") {
            $(`#c${turn}r5a`).text(pronoun1b).append("&nbsp;");
            $(`#c${turn}r5b`).text("gave "+give).append("&nbsp;");
            $(`#c${turn}r5b`).addClass("teal");
            $(`#c${turn}r5c`).text("coins and").append("&nbsp;");
            $(`#c${turn}r5d`).text("kept "+keep);
            $(`#c${turn}r5d`).addClass("pink");
            $(`#c${turn}r5`).fadeIn(quickTime);
        }
        else if (stage=="score") {
            $(`#c${turn}r6a`).text("Their score increased by").append("&nbsp;");
            $(`#c${turn}r6b`).text(currentAgent);
            if (game.userRole=="A") {$(`#c${turn}r6b`).addClass("pink");}
            else {$(`#c${turn}r6b`).addClass("teal");}
            $(`#c${turn}r7a`).text("Your score increased by").append("&nbsp;");
            $(`#c${turn}r7b`).text(currentUser);
            if (game.userRole=="A") {$(`#c${turn}r7b`).addClass("teal");}
            else {$(`#c${turn}r7b`).addClass("pink");}
            $(`#c${turn}r6`).fadeIn(quickTime);
            $(`#c${turn}r7`).fadeIn(quickTime);
        }
    }
    function clearLog() {
        $(`#c1r1`).text("");
        $(`#c1r2a`).text("");
        $(`#c1r2b`).text("");
        $(`#c1r2c`).text("");
        $(`#c1r3a`).text("");
        $(`#c1r3b`).text("");
        $(`#c1r3c`).text("");
        $(`#c1r3d`).text("");
        $(`#c1r4a`).text("");
        $(`#c1r4b`).text("");
        $(`#c1r4c`).text("");
        $(`#c1r5a`).text("");
        $(`#c1r5b`).text("");
        $(`#c1r5c`).text("");
        $(`#c1r5d`).text("");
        $(`#c1r6a`).text("");
        $(`#c1r6b`).text("");
        $(`#c1r7a`).text("");
        $(`#c1r7b`).text("");
        $(`#c1r6b`).removeClass('pink');
        $(`#c1r6b`).addClass('teal');
        $(`#c1r7b`).removeClass('teal');
        $(`#c1r7b`).addClass('pink');
        $(`#c2r1`).text("");
        $(`#c2r2a`).text("");
        $(`#c2r2b`).text("");
        $(`#c2r2c`).text("");
        $(`#c2r3a`).text("");
        $(`#c2r3b`).text("");
        $(`#c2r3c`).text("");
        $(`#c2r3d`).text("");
        $(`#c2r4a`).text("");
        $(`#c2r4b`).text("");
        $(`#c2r4c`).text("");
        $(`#c2r5a`).text("");
        $(`#c2r5b`).text("");
        $(`#c2r5c`).text("");
        $(`#c2r5d`).text("");
        $(`#c2r6a`).text("");
        $(`#c2r6b`).text("");
        $(`#c2r7a`).text("");
        $(`#c2r7b`).text("");
        $(`#c2r6b`).removeClass('pink');
        $(`#c2r6b`).addClass('teal');
        $(`#c2r7b`).removeClass('teal');
        $(`#c2r7b`).addClass('pink');
    }

    // Animate top bars increasing width and counting up
    function animateTurn() {
        let box = $("#turn-box"+turn);
        box.animate({'opacity': "1"}, animateTime);
    }
    function animateScoreA() {
        let box = (game.userRole=="A") ? $("#ys-box") : $("#ts-box");
        let num = (game.userRole=="A") ? $("#ys-num") : $("#ts-num");
        // let f = scoreA / (game.rounds*game.capital*game.match);  // theoretical max is never achieved
        let f = scoreA / (60);
        let w = f * parseInt($(":root").css('--boxWidth'))
        let wMin = parseInt($(":root").css('--boxWidthMin'));
        let wMax = parseInt($(":root").css('--boxWidth'));
        if (w>wMin & w<wMax) {box.animate({'width': w+"vw"}, animateTime);}
        else if (w<=wMin) {box.animate({'width': wMin+"vw"}, animateTime);}
        else if (w>=wMax) {box.animate({'width': wMax+"vw"}, animateTime);}
        $({count: num.text()}).animate(
                {count: scoreA},
                {duration: animateTime, step: function () {num.text(Number(this.count).toFixed());}}
        );
        setTimeout(function() {num.text(scoreA)}, animateTime); // fallback
    }
    function animateScoreB() {
        let box = (game.userRole=="B") ? $("#ys-box") : $("#ts-box");
        let num = (game.userRole=="B") ? $("#ys-num") : $("#ts-num");
        // let f = scoreA / (game.rounds*game.capital*game.match);  // theoretical max is never achieved
        let f = scoreB / (60);
        let w = f * parseInt($(":root").css('--boxWidth'))
        let wMin = parseInt($(":root").css('--boxWidthMin'));
        let wMax = parseInt($(":root").css('--boxWidth'));
        if (w>wMin & w<wMax) {console.log('animating'); box.animate({'width': w+"vw"}, animateTime);}
        else if (w<=wMin) {box.animate({'width': wMin+"vw"}, animateTime);}
        else if (w>=wMax) {box.animate({'width': wMax+"vw"}, animateTime);}
        $({count: num.text()}).animate(
                {count: scoreB},
                {duration: animateTime, step: function () {num.text(Number(this.count).toFixed());}}
        );
        setTimeout(function() {num.text(scoreB)}, animateTime); // fallback
    }
    function animateBonus() {
        let box = $("#bonus-box");
        let num = $("#bonus-num");
        let oldBonus = parseInt(num.text());
        let score = (game.userRole == "A") ? scoreA : scoreB;
        let newBonus = parseInt(Number(100*(game.bonus_min + score * game.bonus_rate)).toFixed());
        // let f = scoreA / (game.rounds*game.capital*game.match);  // theoretical max is never achieved
        let f = score / (60);
        let w = f * parseInt($(":root").css('--boxWidth'))
        let wMin = parseInt($(":root").css('--boxWidthMin'));
        let wMax = parseInt($(":root").css('--boxWidth'));
        if (w>wMin & w<wMax) {box.animate({'marginLeft': w+"vw"}, animateTime);}
        else if (w<=wMin) {box.animate({'marginLeft': wMin+"vw"}, animateTime);}
        else if (w>=wMax) {box.animate({'marginLeft': wMax+"vw"}, animateTime);}
        $({count: oldBonus}).animate(
                {count: newBonus},
                {duration: animateTime, step: function () {num.text(Number(this.count).toFixed()+"₵");}}
        );
        setTimeout(function() {num.text(newBonus+"₵")}, animateTime); // fallback
    }

    function finishGame() {
        let userScore = userRewards.reduce((a, b) => a + b, 0);
        let agentScore = agentRewards.reduce((a, b) => a + b, 0);
        $("#playerA").hide();
        $("#playerB").hide();
        $("#imgA").hide();
        $("#imgB").hide();
        if (tutorialGame==1){
            $("#s1a").text(scoreA);
            $("#s1b").text(scoreB);
            $(`#n-next1`).click(function() {$(`#n2`).fadeIn(quickTime);});
            $("#n1").fadeIn(quickTime);
        }
        else if (tutorialGame==2){
            $(`#n-next3`).click(function() {$(`#n4`).fadeIn(quickTime);});
            $("#n3").fadeIn(quickTime);
        }
    }
});
