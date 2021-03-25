initialize("/game/api/startTutorial/", "POST", (game) => {

    // Initialization and globals
    "use strict";
    let maxUser;
    let startTime = performance.now();
    let endTime = performance.now();
    let giveThrMin = 7;
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
    $("#nameA").fadeIn(quickTime)
    $("#nameB").fadeIn(quickTime)
    $("#imgA").fadeIn(quickTime)
    $("#imgB").fadeIn(quickTime)
    $("#nameA").text(game.username);
    $("#nameB").text("Instructor");
    $("#ts-text").css('background-color', 'var(--myPink)');
    $("#ts-box").css('background-color', 'var(--myPink)');
    $("#ys-text").css('background-color', 'var(--myTeal)');
    $("#ys-box").css('background-color', 'var(--myTeal)');
    $(window).resize(resizeSlider);
    $(window).on('beforeunload', function(e) {return false;});
    $(document).mousemove(function(e) {moveSlide(e);});
    $(document).mouseup(function(e) {stopSlide(e);});
    let sliderLeft = document.getElementById("slider-left");
    let sliderThumb = document.getElementById("slider-thumb");
    let sliderRight = document.getElementById("slider-right");
    sliderLeft.addEventListener("touchstart", function(e) {startSlide(e);}, false);
    sliderLeft.addEventListener("touchmove", function(e) {moveSlide(e);}, false);
    sliderLeft.addEventListener("touchend", function(e) {stopSlide(e);}, false);
    sliderThumb.addEventListener("touchstart", function(e) {startSlide(e);}, false);
    sliderThumb.addEventListener("touchmove", function(e) {moveSlide(e);}, false);
    sliderThumb.addEventListener("touchend", function(e) {stopSlide(e);}, false);
    sliderRight.addEventListener("touchstart", function(e) {startSlide(e);}, false);
    sliderRight.addEventListener("touchmove", function(e) {moveSlide(e);}, false);
    sliderRight.addEventListener("touchend", function(e) {stopSlide(e);}, false);

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
        $("#nameB").css('opacity', '0.5')
        $("#imgB").css('opacity', '0.5')
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
        let wMin = parseInt($(":root").css('--barBoxWidthMin'));
        $("#ts-box").css('width', wMin+"vw");
        $("#ts-box").text('0');
        $("#ys-box").css('width', wMin+"vw");
        $("#ys-box").text('0');
        $("#turn-box").css('width', wMin+"vw");
        // animateScoreA();
        // animateScoreB();
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
        $("#nameA").text("Instructor");
        $("#nameB").text(game.username);
        $("#nameB").css('opacity', '1');
        $("#imgB").css('opacity', '1');
        $("#nameA").css('opacity', '0.5')
        $("#imgA").css('opacity', '0.5')
        $("#ts-text").css('background-color', 'var(--myTeal)');
        $("#ts-box").css('background-color', 'var(--myTeal)');
        $("#ys-text").css('background-color', 'var(--myPink)');
        $("#ys-box").css('background-color', 'var(--myPink)');
        maxAgent = game.capital;
        maxUser = 0;
        $("#playerA").fadeIn(quickTime);
        $("#playerB").fadeIn(quickTime);
        $("#nameA").fadeIn(quickTime);
        $("#nameB").fadeIn(quickTime);
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
        let leftEdge = $("#sendB").offset().left - wT/2;
        let rightEdge = $("#sendB").offset().left + wW - wT/2;
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
        let leftEdge = $("#sendB").offset().left - wT/2;
        let rightEdge = $("#sendB").offset().left + wW - wT/2;
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
                    $("#sendA").text("You keep "+sendA+" coins");
                    $("#sendB").text("They get "+sendB+" coins");
                }
                else {
                    $("#sendA").text("They keep "+sendA+" coins");
                    $("#sendB").text("You get "+sendB+" coins");
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
                    $("#sendA").text("They get "+sendA+" coins");
                    $("#sendB").text("You keep "+sendB+" coins");
                }
                else {
                    $("#sendA").text("You get "+sendA+" coins");
                    $("#sendB").text("They keep "+sendB+" coins");
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
            $("#warning").text(`Please give at least ${giveThrMin}`);
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
            $("#log-area").append(`<div hidden id='l${turn}w1' class='lc${turn} lr1'></div>`);
            $(`#l${turn}w1`).append(`<p hidden id='l${turn}t' class='log-turn-text'></p>`);
            $("#log-area").append(`<div hidden id='l${turn}w2' class='lc${turn} lr2'></div>`);
            $(`#l${turn}w2`).append(`<p hidden id='l${turn}a1' class='log-text'></p>`);
            $(`#l${turn}w2`).append(`<p hidden id='l${turn}a2' class='log-text'></p>`);
            $(`#l${turn}w2`).append(`<p hidden id='l${turn}a3' class='log-text'></p>`);
            $(`#l${turn}t`).text("Turn "+turn);
            $(`#l${turn}a1`).text(pronoun1a).append("&nbsp;");
            $(`#l${turn}a2`).text("received "+give).append("&nbsp;");
            $(`#l${turn}a2`).addClass("teal");
            $(`#l${turn}a3`).text("coins to start");
            $(`#l${turn}t`).fadeIn(quickTime);
            $(`#l${turn}a1`).fadeIn(quickTime);
            $(`#l${turn}a2`).fadeIn(quickTime);
            $(`#l${turn}a3`).fadeIn(quickTime);
        }
        else if (stage=="A") {
            $("#log-area").append(`<div id='l${turn}w3' class='lc${turn} lr3'></div>`);
            $("#log-area").append(`<div id='l${turn}w4' class='lc${turn} lr4'></div>`);
            $(`#l${turn}w3`).append(`<p hidden id='l${turn}b1' class='log-text'></p>`);
            $(`#l${turn}w3`).append(`<p hidden id='l${turn}b2' class='log-text'></p>`);
            $(`#l${turn}w3`).append(`<p hidden id='l${turn}b3' class='log-text'></p>`);
            $(`#l${turn}w3`).append(`<p hidden id='l${turn}b4' class='log-text'></p>`);
            $(`#l${turn}w4`).append(`<p hidden id='l${turn}c1' class='log-text'></p>`);
            $(`#l${turn}w4`).append(`<p hidden id='l${turn}c2' class='log-text'></p>`);
            $(`#l${turn}w4`).append(`<p hidden id='l${turn}c3' class='log-text'></p>`);
            $(`#l${turn}b1`).text(pronoun1a).append("&nbsp;");
            $(`#l${turn}b2`).text("gave "+give).append("&nbsp;");
            $(`#l${turn}b2`).addClass("pink");
            $(`#l${turn}b3`).text("coins and").append("&nbsp;");
            $(`#l${turn}b4`).text("kept "+keep).append("&nbsp;");
            $(`#l${turn}b4`).addClass("teal");
            $(`#l${turn}c1`).text(pronoun1b).append("&nbsp;");
            $(`#l${turn}c2`).text("received "+give*game.match).append("&nbsp;");
            $(`#l${turn}c2`).addClass("pink");
            $(`#l${turn}c3`).text("coins from").append("&nbsp;").append(pronoun2);
            $(`#l${turn}b1`).fadeIn(quickTime);
            $(`#l${turn}b2`).fadeIn(quickTime);
            $(`#l${turn}b3`).fadeIn(quickTime);
            $(`#l${turn}b4`).fadeIn(quickTime);
            $(`#l${turn}c1`).fadeIn(quickTime);
            $(`#l${turn}c2`).fadeIn(quickTime);
            $(`#l${turn}c3`).fadeIn(quickTime);
        }
        else if (stage=="B") {
            $("#log-area").append(`<div id='l${turn}w5' class='lc${turn} lr5'></div>`);
            $(`#l${turn}w5`).append(`<p hidden id='l${turn}d1' class='log-text'></p>`);
            $(`#l${turn}w5`).append(`<p hidden id='l${turn}d2' class='log-text'></p>`);
            $(`#l${turn}w5`).append(`<p hidden id='l${turn}d3' class='log-text'></p>`);
            $(`#l${turn}w5`).append(`<p hidden id='l${turn}d4' class='log-text'></p>`);
            $(`#l${turn}d1`).text(pronoun1b).append("&nbsp;");
            $(`#l${turn}d2`).text("gave "+give).append("&nbsp;");
            $(`#l${turn}d2`).addClass("teal");
            $(`#l${turn}d3`).text("coins and").append("&nbsp;");
            $(`#l${turn}d4`).text("kept "+keep);
            $(`#l${turn}d4`).addClass("pink");
            $(`#l${turn}d1`).fadeIn(quickTime);
            $(`#l${turn}d2`).fadeIn(quickTime);
            $(`#l${turn}d3`).fadeIn(quickTime);
            $(`#l${turn}d4`).fadeIn(quickTime);
        }
        else if (stage=="score") {
            $("#log-area").append(`<div id='l${turn}w6' class='lc${turn} lr6'></div>`);
            $("#log-area").append(`<div id='l${turn}w7' class='lc${turn} lr7'></div>`);
            $(`#l${turn}w6`).append(`<p hidden id='l${turn}e1' class='log-text'></p>`);
            $(`#l${turn}w6`).append(`<p hidden id='l${turn}e2' class='log-text'></p>`);
            $(`#l${turn}w7`).append(`<p hidden id='l${turn}f1' class='log-text'></p>`);
            $(`#l${turn}w7`).append(`<p hidden id='l${turn}f2' class='log-text'></p>`);
            $(`#l${turn}e1`).text("Their score increased by").append("&nbsp;");
            $(`#l${turn}e2`).text(currentAgent);
            if (game.userRole=="A") {$(`#l${turn}e2`).addClass("pink");}
            else {$(`#l${turn}e2`).addClass("teal");}
            $(`#l${turn}f1`).text("Your score increased by").append("&nbsp;");
            $(`#l${turn}f2`).text(currentUser);
            if (game.userRole=="A") {$(`#l${turn}f2`).addClass("teal");}
            else {$(`#l${turn}f2`).addClass("pink");}
            $(`#l${turn}e1`).fadeIn(quickTime);
            $(`#l${turn}e2`).fadeIn(quickTime);
            $(`#l${turn}f1`).fadeIn(quickTime);
            $(`#l${turn}f2`).fadeIn(quickTime);
        }
    }
    function clearLog() {$("#log-area").empty();}

    // Animate top bars increasing width and counting up
    function animateTurn() {
        let box = $("#turn-box");
        let f = turn / maxTurns;
        let w = f * parseInt($(":root").css('--barBoxWidth'))
        let wMin = parseInt($(":root").css('--barBoxWidthMin'));
        if (w>wMin) {box.animate({'width': w+"vw"}, animateTime);}
        setTimeout(function() {box.text(turn+"/"+maxTurns)}, animateTime);
    }
    function animateScoreA() {
        let box = (game.userRole=="A") ? $("#ys-box") : $("#ts-box");
        let f = scoreA / (game.rounds*game.capital*game.match);
        let w = f * parseInt($(":root").css('--barBoxWidth'))
        let wMin = parseInt($(":root").css('--barBoxWidthMin'));
        if (w>wMin) {box.animate({'width': w+"vw"}, animateTime);}
        $({count: box.text()}).animate(
                {count: scoreA},
                {duration: animateTime, step: function () {box.text(Number(this.count).toFixed());}}
        );
        setTimeout(function() {box.text(scoreA)}, animateTime); // fallback
    }
    function animateScoreB() {
        let box = (game.userRole=="B") ? $("#ys-box") : $("#ts-box");
        let f = scoreB / (game.rounds*game.capital*game.match);
        let w = f * parseInt($(":root").css('--barBoxWidth'))
        let wMin = parseInt($(":root").css('--barBoxWidthMin'));
        if (w>wMin) {box.animate({'width': w+"vw"}, animateTime);}
        $({count: box.text()}).animate(
                {count: scoreB},
                {duration: animateTime, step: function () {box.text(Number(this.count).toFixed());}}
        );
        setTimeout(function() {box.text(scoreB)}, animateTime); // fallback
    }
    function animateBonus() {
        let box = $("#bonus-box");
        let f = 0;
        let bonus = 0;
        let score = (game.userRole == "A") ? scoreA : scoreB;
        for (let i=0; i<game.bonus.length; i++) {
            if (score>=game.bonus[i][0]) {
                f = game.bonus[i][0] / (game.rounds*game.capital*game.match);
                bonus = game.bonus[i][1];
            }
        }
        let w = f * parseInt($(":root").css('--barBoxWidth'))
        let wMin = parseInt($(":root").css('--barBoxWidthMin'));
        if (w>wMin) {box.animate({'width': w+"vw"}, animateTime);}
        setTimeout(function() {box.text(Number(100*bonus).toFixed()+"₵")}, animateTime); // fallback
    }

    function finishGame() {
        let userScore = userRewards.reduce((a, b) => a + b, 0);
        let agentScore = agentRewards.reduce((a, b) => a + b, 0);
        $("#playerA").hide();
        $("#playerB").hide();
        $("#nameA").hide();
        $("#nameB").hide();
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
