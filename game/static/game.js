initialize("/game/api/startGame/", "POST", (game) => {

    // Initialization and globals
    "use strict";
    let maxUser;
    let maxAgent;
    let agentTime = 2000;
    let animateTime = 1000;
    let quickTime = 500;
    let waitTime = 1000;
    let startTime = performance.now();
    let endTime = performance.now();
    let currentA = game.capital;
    let currentB = 0;
    let scoreA = 0;
    let scoreB = 0;
    // let doneRequiredBool = (game.doneRequired !== null);
    let turn = 1;
    let complete = false
    let userGives = game.userGives;
    let userKeeps = game.userKeeps;
    let userRewards = game.userRewards;
    let agentGives = game.agentGives;
    let agentKeeps = game.agentKeeps;
    let agentRewards = game.agentRewards;
    let isMouseDown = false;
    let startMouseX;
    let widthW = parseInt($("#slider-wrapper").css('width'));
    let widthT = parseInt($("#slider-thumb").css('width'));
    // let leftEdge = $("#slider-wrapper").offset().left;
    let leftEdge = $("#sendB").offset().left - widthT/2;
    let rightEdge = $("#sendB").offset().left + widthW - widthT/2;
    if (game.userRole == "A") {
        maxUser = game.capital;
        maxAgent = 0;  // updated after user moves
        $("#nameB").text("Trustee");
        $("#nameA").text(game.username);
        $("#nameB").css('opacity', '0.5')
        $("#imgB").css('opacity', '0.5')
        $("#ts-text").css('background-color', 'var(--myPink)');
        $("#ts-box").css('background-color', 'var(--myPink)');
        $("#ys-text").css('background-color', 'var(--myTeal)');
        $("#ys-box").css('background-color', 'var(--myTeal)');
        setTimeout(function() {switchToUser();}, animateTime);
    }
    else {
        $("#nameB").text(game.username);
        $("#nameA").text("Investor");
        $("#nameA").css('opacity', '0.5')
        $("#imgA").css('opacity', '0.5')
        $("#ts-text").css('background-color', 'var(--myTeal)');
        $("#ts-box").css('background-color', 'var(--myTeal)');
        $("#ys-text").css('background-color', 'var(--myPink)');
        $("#ys-box").css('background-color', 'var(--myPink)');
        maxAgent = game.capital;
        maxUser = 0;  // updated after agent moves
        setTimeout(function() {switchToAgent(1);}, animateTime);
    }
    animateTurn();
    animateBonus();
    executeMove("capital");
    $("#submit").click(callUpdate);
    $(document).mousemove(function(e) {moveSlide(e);});
    $(document).mouseup(function(e) {stopSlide(e);});


    // Functions

    // slider 
    let getMouseX = function(e) {
        let event = e;
        if (!e) {event = window.event;}
        if (event.pageX) {return event.pageX;}
        // else if (event.clientX) {return event.clientX;}
        // return e.pageX;       
    }
    let startSlide = function(e) {
        isMouseDown = true;
        $("#submit").prop('disabled', false);
        startMouseX = getMouseX(e);
        updateSliderMouse();
        return false;
    }
    let moveSlide = function(e) {
        if (isMouseDown) {updateSliderMouse(e); return false;}
    }
    let stopSlide = function(e) {
        isMouseDown = false;
        let x = getMouseX(e);
        let f = absToRel(x);
    }
    let absToRel = function(x) {
        if ($("#slider-wrapper").hasClass('flipped')) {
            if (x <= leftEdge) {return 1;}
            else if (x >= rightEdge) {return 0;}
            else {return 1 - (x-leftEdge)/widthW;}
        }
        else {
            if (x <= leftEdge) {return 0;}
            else if (x >= rightEdge) {return 1;}
            else {return (x-leftEdge)/widthW;}            
        }
    }
    let updateSliderMouse = function(e) {
        let x = getMouseX(e);
        let f = absToRel(x);
        updateSlider(f, maxUser, game.userRole);
    }
    let updateSlider = function(f, max, player) {
        let val = Math.round(f*max);
        let widthLNew = Math.max(0, f * widthW - widthT);
        let marginTNew = Math.max(0, f * widthW - widthT);
        let widthRNew = Math.min((1-f) * widthW, widthW-widthT);
        let marginRNew = Math.max(widthT, widthLNew+widthT);
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
        endTime = performance.now() // track user response time
        let userGive = Number($("#slider-wrapper").attr('val'));
        let userKeep = maxUser - userGive;
        let userTime = (endTime-startTime);
        userGives.push(userGive);
        userKeeps.push(userKeep);
        if (game.userRole == "A") {maxAgent = userGive * game.match} // update global
        $("#submit").hide();
        setTimeout(function() {hideSlider();}, animateTime);
        let skip = (userGive==0);
        executeMove(game.userRole, userGive, userKeep, skip);
        // setTimeout(function() {hideForm();}, animateTime+waitTime);
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
            url: '/game/api/updateGame/',
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
                complete = returnData.complete;
                if (!complete || game.userRole=="A") {
                    let wait;
                    if (userGive==0 & game.userRole=="A"){wait=0;}
                    else if (userGive==0 & game.userRole=="B"){wait=3*animateTime;}
                    else if (userGive>0 & game.userRole=="A"){wait=animateTime;}
                    else if (userGive>0 & game.userRole=="B") {wait=4*animateTime;}
                    setTimeout(function () {switchToAgent(userGive);}, wait);
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
        }
        else {
            $("#slider-wrapper").css('opacity', "0.7");
            $("#slider-thumb").css('background-color', "var(--myGray)");
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

    // Animate top bars increasing width and counting up
    function animateTurn() {
        let box = $("#turn-box");
        let f = turn / game.rounds;
        let w = f * parseInt($(":root").css('--barBoxWidth'))
        let wMin = parseInt($(":root").css('--barBoxWidthMin'));
        if (w>wMin) {box.animate({'width': w+"vw"}, animateTime);}
        setTimeout(function() {box.text(turn+"/"+game.rounds)}, animateTime);
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

    // Final page after game is complete
    function finishGame() {
        let bonus;
        let userScore = userRewards.reduce((a, b) => a + b, 0);
        let agentScore = agentRewards.reduce((a, b) => a + b, 0);
        if (game.userRole == "A") {
            $("#aTotal").text("$"+userScore);
            $("#bTotal").text("$"+agentScore);
        }
        else {
            $("#aTotal").text("$"+agentScore);
            $("#bTotal").text("$"+userScore);
        }
        for (let i=0; i<game.bonus.length; i++) {
            if (userScore >= game.bonus[i][0]) {bonus = game.bonus[i][1];}
        }
        $("#headerW").text("Winnings — $"+Number(game.winnings).toFixed(2) + " + "+bonus);
        $("#headerG").text("Games Played — "+game.nGames+" + 1");
        $("#playerA").fadeOut(quickTime);
        $("#playerB").fadeOut(quickTime);
        $("#nameA").fadeOut(quickTime);
        $("#nameB").fadeOut(quickTime);
        $("#imgA").fadeOut(quickTime);
        $("#imgB").fadeOut(quickTime);
        $("#game-over-area").fadeIn(quickTime);
        $("#flair-text").fadeIn(quickTime);
        if (game.nGames+1 == game.required) {$("#flair-text").text("Required games complete!");}
        $("#game-over-text").fadeIn(quickTime);
        $("#play-again-text").fadeIn(quickTime);
    }
});
