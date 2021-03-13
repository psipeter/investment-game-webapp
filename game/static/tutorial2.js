initialize("/game/api/startTutorial/", "POST", (game) => {

    // Initialization and globals
    "use strict";
    let maxUser;
    let giveThrMin = 8;
    let giveThrMax = 0.3;
    let maxTurns = 1;
    let tutorialGame = 1;
    let maxAgent;
    let agentTime = 2000;
    let animateTime = 1000;
    let waitTime = 500;
    let currentA = game.capital;
    let currentB = 0;
    let scoreA = 0;
    let scoreB = 0;
    let turn = 1;
    let complete = false
    let userGives = game.userGives;
    let userKeeps = game.userKeeps;
    let userRewards = game.userRewards;
    let agentGives = game.agentGives;
    let agentKeeps = game.agentKeeps;
    let agentRewards = game.agentRewards;
    maxUser = game.capital;
    maxAgent = 0;  // updated after user moves
    $("#nameA").text(game.username);
    $("#nameB").text("Instructor");
    $("#nameB").css('opacity', '0.5')
    $("#imgB").css('opacity', '0.5')
    $("#ts-progress").css('background-color', 'var(--myPink)');
    $("#ys-progress").css('background-color', 'var(--myTeal)');
    $("#slider").css('--sliderColor1', 'var(--myTeal');
    $("#slider").css('--sliderColor2', 'var(--myPink');
    $("#slider").css('--coinImg', 'var(--coinImg1');
    $("#greedyA").text("You kept everything!");
    $("#greedyB").text("They kept everything!");

    let notes = $(".note");
    for (let n=0; n<notes.length; n++) {
        notes.eq(n).hide();
        notes.eq(n).append(`<div id='n-nav${n}' class='n-nav'> </div>`);
        $(`#n-nav${n}`).append(`<p id='n-next${n}'class="next">next</p>`);
        $(`#n-next${n}`).click(function() {$(`#n${n}`).hide();});
    }

    // Tutorial Sequence
    $("#submit").click(callUpdate);
    $("#n-area").show();
    $(".note").eq(0).show();
    $("#n-next0").text("Begin Game 1");
    $("#n-next2").text("Begin Game 2");
    $(`#n-next4`).click(function() {
        $(`#n5`).show();
        $(`#headerG`).addClass('red');
        $(`#headerW`).addClass('yellow');
        $(`#cash-link`).addClass('black');
    });
    $(`#n-next5`).text("Finish");
    $(`#n-next5`).click(function() {
        let form = $("#form");
        let sendData = form.serialize();
        $.ajax({
            method: 'POST',
            url: '/game/api/finishTutorial/',
            data: sendData,
            dataType: 'json',
        });
        window.location.href=$("#n5").attr("href");
    });
    $("#n-next0").click(function() {
        animateBar('turn', game.userRole);
        addThresholds();
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
        maxAgent = game.capital;
        maxUser = 0;  // updated after agent moves
        giveThrMin = 0;
        giveThrMax = 0.3;
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
                setTimeout(function () {flipArrow(); switchToAgent(1);}, animateTime+waitTime);
            }
        });
        // reposition and recolor elements
        $("#nameA").text("Instructor");
        $("#nameB").text(game.username);
        $("#nameA").css('opacity', '0.5')
        $("#nameB").css('opacity', '1')
        $("#imgA").css('opacity', '0.5')
        $("#imgB").css('opacity', '1')
        $("#ts-progress").css('background-color', 'var(--myTeal)');
        $("#ys-progress").css('background-color', 'var(--myPink)');
        $("#slider").css('--sliderColor1', 'var(--myPink');
        $("#slider").css('--sliderColor2', 'var(--myTeal');
        $("#slider").addClass('flipped');
        $("#slider").css('--coinImg', 'var(--coinImg2');
        $("#greedyA").text("They kept everything!");
        $("#greedyB").text("You kept everything!");
        $("#playerA").show();
        $("#playerB").show();
        $("#nameA").show();
        $("#nameB").show();
        $("#imgA").show();
        $("#imgB").show();
        // start game with agent
        $("#ys-progress").width("0");
        $("#ts-progress").width("0");
        $("#ys-num").text("");
        $("#ts-num").text("");
        $("#turn-progress").width("0");
        clearLog();
        flipArrow(); 
        animateBar('turn', game.userRole);
        return false;
    });

    // Functions
    var slideFunction = function () {
        $("#sendA").show();
        $("#sendB").show();
        let max = maxUser;
        let slideVal = Number($("#slider").val());
        $("#submit").prop('disabled', false);
        if (game.userRole=="A"){
            let sendA = max-slideVal;
            let sendB = slideVal*game.match;
            for (let i = 0; i <= game.capital*game.match; i++) {
                if (i<=sendA) {$("#c"+i+"a").css('opacity', '1');}
                else if (i<=max){$("#c"+i+"a").css('opacity', '0.3');}
                else {$("#c"+i+"a").css('opacity', '0');}
                if (i<=sendB) {$("#c"+i+"b").css('opacity', '0.3');}
                else {$("#c"+i+"b").css('opacity', '0');}
            $("#sendA").text("You keep "+sendA+" coins");
            $("#sendB").text("They get "+sendB+" coins");
            }            
        }
        else {
            let sendA = slideVal;  // compensate for rotated slider
            let sendB = max-slideVal;  // compensate for rotated slider
            // $("#sendA").text("they get "+sendA+" coins");
            // $("#sendB").text("you keep "+sendB+" coins");
            for (let i = 0; i <= currentB; i++) {
                if (i<=currentA) {$("#c"+i+"a").css('opacity', '1');}
                else if (i<=(currentA+sendA)){$("#c"+i+"a").css('opacity', '0.3');}
                else {$("#c"+i+"a").css('opacity', '0');}
                if (i<sendA) {$("#c"+(currentB-i)+"b").css('opacity', '0.3');}
                else if (i<=currentB){$("#c"+(currentB-i)+"b").css('opacity', '1');}
                else {$("#c"+i+"b").css('opacity', '0');}
            }            
            $("#sendA").text("They get "+sendA+" coins");
            $("#sendB").text("You keep "+sendB+" coins");
        }    
    }
    $("#slider").on('change', slideFunction);
    $("#slider").on('input', slideFunction);

    function switchToUser() {
        hideLoading();
        hideForm();
        if (game.userRole=="B"){maxUser = game.match*agentGives[agentGives.length-1];}
        if (maxUser==0) { // forced turn skip
            resetSlider();
            callUpdate();
        }
        else {
            showForm();
            showInputs();
            resetSlider();
            $("#arrow").css('visibility', 'visible');
            $("#submit").prop('disabled', true);  // until slider moves
            $("#sendA").hide();  // until slider moves
            $("#sendB").hide();  // until slider moves
        }
    }

    function switchToAgent(userGive) {
        let agentGive = agentGives[agentGives.length-1];
        let agentKeep = agentKeeps[agentKeeps.length-1];
        hideForm();
        hideInputs();
        flipArrow();
        showLoading();
        setTimeout(function() {
            hideLoading();
            showForm();
            updateSendAgent(agentGive, agentKeep);
            executeMove(game.agentRole, agentGive, agentKeep);
        }, agentTime);
        setTimeout(function() {hideForm();}, animateTime+agentTime+waitTime);
        let wait;
        // if (userGive==0 & game.agentRole=="A") {wait = 5*animateTime;}  // userGive doesn't matter in this case
        if (userGive==0 & game.agentRole=="B") {wait = 5*animateTime;}  // agent is skipped
        else if (agentGive==0 & game.agentRole=="A") {wait = agentTime;}
        else if (agentGive==0 & game.agentRole=="B") {wait = 4*animateTime+agentTime;}
        else if (agentGive>0 & game.agentRole=="A") {wait = animateTime+agentTime;}
        else if (agentGive>0 & game.agentRole=="B") {wait = 5*animateTime+agentTime;}
        if (!complete) {setTimeout(function() {flipArrow(); switchToUser();}, wait+waitTime);}
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
    function executeMove(move, give=null, keep=null, finish=true){
        if (move=="capital") {
            updateLog("capital", game.capital, 0);
            animateCoins(0, 0, game.capital, 'in', 'a');
            currentA = game.capital;
        }
        if (move=="A"){
            updateLog("A", give, keep);
            animateCoins(0, game.capital, -give, 'out', 'a');
            animateCoins(0, 0, give*game.match, 'in', 'b');
            currentA = keep;
            currentB = game.match*give;
        }
        if (move=="B") {
            updateLog("B", give, keep);
            animateCoins(0, currentB, -give, 'out', 'b');
            animateCoins(1, currentA, give, 'in', 'a');
            currentA += give;
            currentB -= give;
            if (finish) {setTimeout(()=> {finishTurn();}, animateTime+waitTime);}
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
            $("#log-area").append(`<div id='l${turn}w1' class='lc${turn} lr1'></div>`);
            $(`#l${turn}w1`).append(`<p id='l${turn}t' class='log-turn-text'></p>`);
            $("#log-area").append(`<div id='l${turn}w2' class='lc${turn} lr2'></div>`);
            $(`#l${turn}w2`).append(`<p id='l${turn}a1' class='log-text'></p>`);
            $(`#l${turn}w2`).append(`<p id='l${turn}a2' class='log-text'></p>`);
            $(`#l${turn}w2`).append(`<p id='l${turn}a3' class='log-text'></p>`);
            $(`#l${turn}t`).text("Turn "+turn);
            $(`#l${turn}a1`).text(pronoun1a).append("&nbsp;");
            $(`#l${turn}a2`).text("received "+give).append("&nbsp;");
            $(`#l${turn}a2`).addClass("teal");
            $(`#l${turn}a3`).text("coins to start");
        }
        else if (stage=="A") {
            $("#log-area").append(`<div id='l${turn}w3' class='lc${turn} lr3'></div>`);
            $("#log-area").append(`<div id='l${turn}w4' class='lc${turn} lr4'></div>`);
            $(`#l${turn}w3`).append(`<p id='l${turn}b1' class='log-text'></p>`);
            $(`#l${turn}w3`).append(`<p id='l${turn}b2' class='log-text'></p>`);
            $(`#l${turn}w3`).append(`<p id='l${turn}b3' class='log-text'></p>`);
            $(`#l${turn}w3`).append(`<p id='l${turn}b4' class='log-text'></p>`);
            $(`#l${turn}w4`).append(`<p id='l${turn}c1' class='log-text'></p>`);
            $(`#l${turn}w4`).append(`<p id='l${turn}c2' class='log-text'></p>`);
            $(`#l${turn}w4`).append(`<p id='l${turn}c3' class='log-text'></p>`);
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
        }
        else if (stage=="B") {
            $("#log-area").append(`<div id='l${turn}w5' class='lc${turn} lr5'></div>`);
            $(`#l${turn}w5`).append(`<p id='l${turn}d1' class='log-text'></p>`);
            $(`#l${turn}w5`).append(`<p id='l${turn}d2' class='log-text'></p>`);
            $(`#l${turn}w5`).append(`<p id='l${turn}d3' class='log-text'></p>`);
            $(`#l${turn}w5`).append(`<p id='l${turn}d4' class='log-text'></p>`);
            $(`#l${turn}d1`).text(pronoun1b).append("&nbsp;");
            $(`#l${turn}d2`).text("gave "+give).append("&nbsp;");
            $(`#l${turn}d2`).addClass("teal");
            $(`#l${turn}d3`).text("coins and").append("&nbsp;");
            $(`#l${turn}d4`).text("kept "+keep);
            $(`#l${turn}d4`).addClass("pink");
        }
        else if (stage=="score") {
            $("#log-area").append(`<div id='l${turn}w6' class='lc${turn} lr6'></div>`);
            $("#log-area").append(`<div id='l${turn}w7' class='lc${turn} lr7'></div>`);
            $(`#l${turn}w6`).append(`<p id='l${turn}e1' class='log-text'></p>`);
            $(`#l${turn}w6`).append(`<p id='l${turn}e2' class='log-text'></p>`);
            $(`#l${turn}w7`).append(`<p id='l${turn}f1' class='log-text'></p>`);
            $(`#l${turn}w7`).append(`<p id='l${turn}f2' class='log-text'></p>`);
            $(`#l${turn}e1`).text("Their score increased by").append("&nbsp;");
            $(`#l${turn}e2`).text(currentAgent);
            if (game.userRole=="A") {$(`#l${turn}e2`).addClass("pink");}
            else {$(`#l${turn}e2`).addClass("teal");}
            $(`#l${turn}f1`).text("Your score increased by").append("&nbsp;");
            $(`#l${turn}f2`).text(currentUser);
            if (game.userRole=="A") {$(`#l${turn}f2`).addClass("teal");}
            else {$(`#l${turn}f2`).addClass("pink");}
        }
    }
    function clearLog() {
        $("#log-area").empty();
    }

    // Animate top bars increasing width and counting up
    function animateBar(barName, player){
        let bar;
        let num;
        let widthNow;
        let widthFrac = 0;
        let widthNew = 0;
        let widthText = parseInt($("#turn-text").css('width'));
        let widthTotal = parseInt($("#turn-wrapper").css('width'));
        let score = (player=="A") ? scoreA : scoreB;
        let winnings = 0.0;
        if (barName=="scoreA" || barName=="scoreB") {
            bar = (game.userRole==player) ? $("#ys-progress") : $("#ts-progress");
            num = (game.userRole==player) ? $("#ys-num") : $("#ts-num");
            widthFrac = score/(game.rounds*game.capital*game.match);
            widthNew = (widthTotal-widthText) * widthFrac;
            widthNow = parseInt(bar.css('width'));
            if (widthNew > widthNow){bar.animate({'width': widthNew}, animateTime);}
            $({count: num.text()}).animate(
                {count: score},
                {duration: animateTime, easing: 'linear', step: function () {
                    num.text(Number(this.count).toFixed());
                }}
            );            
        }
        else if (barName=="bonus") {
            bar = $("#bonus-progress");
            num = $("#bonus-num");
            for (let i=0; i<game.bonus.length; i++) {
                if (score>=game.bonus[i][0]) {
                    $(`#thr${i+1}`).css('background-color', 'var(--myYellow');
                }
            }
        }
        else if (barName=="turn") {
            bar = $("#turn-progress");
            num = $("#turn-num");
            widthFrac = turn/maxTurns;
            widthNew = (widthTotal-widthText) * widthFrac;
            widthNow = parseInt(bar.css('width'));
            if (widthNew > widthNow){bar.animate({'width': widthNew}, animateTime);}
            $({count: num.text()}).animate(
                {count: turn-1},
                {duration: animateTime, easing: 'linear', step: function () {
                    let newTurn = Math.max(turn, Math.round(Number(this.count)));
                    // don't display NaN on first steps
                    if (!isNaN(newTurn)){num.text(newTurn+"/"+maxTurns);}
                }}
            );              
        }
    }

    function flipArrow() {
        if ($("#arrow").hasClass('flipped')) {$("#arrow").removeClass('flipped');}
        else ($("#arrow").addClass('flipped'))
    }
    function hideForm() {
        $("#arrow").hide();
        $("#sendA").hide();
        $("#sendB").hide();
    }
    function showForm() {
        $("#arrow").show();
        $("#sendA").show();
        $("#sendB").show();        
    }
    function hideInputs() {
        $("#submit").prop('disabled', true);
        $("#submit").hide();
        $("#slider").hide();
    }
    function showInputs() {
        $("#slider").prop('disabled', false);
        $("#submit").show();
        $("#slider").show();
    }
    function showGreedy(player){
        if (player=="A") {$("#greedyA").show();}
        else {$("#greedyB").show();}
    }
    function hideGreedy(player){
        if (player=="A") {$("#greedyA").hide();}
        else {$("#greedyB").hide();}
    }
    function showLoading() {
        $("#loading").show();
    }
    function hideLoading() {
        $("#loading").hide();
    }
    function resetSlider() {
        $("#slider").prop('min', 0);
        $("#slider").prop('max', maxUser);
        $("#slider").prop('value', giveThrMin);
    }

    function updateSendAgent(agentGive, agentKeep){
        if (game.userRole == "A") {
            $("#sendA").text("You get "+agentGive+" coins");
            $("#sendB").text("They keep "+agentKeep);
        }
        else {
            $("#sendA").text("They keep "+agentKeep+" coins");
            $("#sendB").text("You get " +agentGive*game.match+" coins");
        }
    }

    function addThresholds(){
        let thrBar = $("#thr-wrapper");
        let widthText = parseInt($("#thr-text").css('width'));
        let widthTotal = parseInt($("#thr-wrapper").css('width'));
        for (let i=1; i<game.bonus.length; i++) {
            let reward = game.bonus[i-1][1];
            let widthFrac = (game.bonus[i][0] - game.bonus[i-1][0]) /(game.rounds*game.capital*game.match);
            let widthNew = (widthTotal-widthText) * widthFrac;
            let heightNew = parseInt($("#thr-wrapper").css('height'));
            thrBar.append(`<div id='thr${i}' class='thr'></div>`);
            $(`#thr${i}`).css("width", widthNew);  
            $(`#thr${i}`).css("height", heightNew);  
            if (i<game.bonus.length-1) {$(`#thr${i}`).css("borderRight", "1pt solid black");}
            $(`#thr${i}`).addClass("thr");  
            $(`#thr${i}`).append(`<h2 class="text">$${reward}</h2>`);
            if (i==1) {$(`#thr${i}`).css('background-color', 'var(--myYellow');}
        }
    }


    // Communicate with the server through AJAX (views.updateGame())
    function callUpdate() {
        let userGive = Number($("#slider").val());
        let userKeep = maxUser - userGive;
        if (userGive<giveThrMin & tutorialGame==1) {
            hideInputs();
            $("#greedyA").text(`Please give at least ${giveThrMin}`);
            showGreedy(game.userRole)
            setTimeout(function(){
                fastCoins(game.capital, "a");
                hideGreedy(game.userRole);
                switchToUser();
            }, animateTime+waitTime);
            return;
        }
        if (userGive>giveThrMax*maxUser & tutorialGame==2) {
            hideInputs();
            $("#greedyB").text(`Please keep at least ${((1-giveThrMax)*maxUser).toFixed(0)}`);
            showGreedy(game.userRole)
            setTimeout(function(){
                fastCoins(currentA, "a");
                fastCoins(currentB, "b");
                hideGreedy(game.userRole);
                switchToUser();
            }, animateTime+waitTime);
            return;
        }
        let userTime = 0;
        userGives.push(userGive);
        userKeeps.push(userKeep);
        if (game.userRole == "A") {maxAgent = userGive * game.match} // update global
        hideInputs();
        showForm();
        executeMove(game.userRole, userGive, userKeep);
        setTimeout(function() {hideForm();}, animateTime+waitTime);
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

    function finishTurn() {
        // todo: alignment check
        scoreA += currentA;
        scoreB += currentB;
        updateLog("score", currentA, currentB);
        animateCoins(0, currentA, -currentA, 'out', 'a');
        animateCoins(0, currentB, -currentB, 'out', 'b');
        animateBar('scoreA', "A");
        animateBar('scoreB', "B");
        animateBar('bonus', game.userRole);
        currentA = 0;
        currentB = 0;
        turn++;
        if (complete) {
            setTimeout(()=> {finishGame();}, animateTime+waitTime);
        }
        else {
            setTimeout(()=> {animateBar('turn', game.userRole);}, animateTime+waitTime);
            setTimeout(()=> {executeMove('capital');}, 2*animateTime+waitTime);
        }
    }

    function finishGame() {
        let userScore = userRewards.reduce((a, b) => a + b, 0);
        let agentScore = agentRewards.reduce((a, b) => a + b, 0);
        hideLoading()
        hideInputs();
        hideForm();
        $("#playerA").hide();
        $("#playerB").hide();
        $("#nameA").hide();
        $("#nameB").hide();
        $("#imgA").hide();
        $("#imgB").hide();
        if (tutorialGame==1){
            $("#s1a").text(scoreA);
            $("#s1b").text(scoreB);
            $(`#n-next1`).click(function() {$(`#n2`).show();});
            $("#n1").show();
        }
        else if (tutorialGame==2){
            $(`#n-next3`).click(function() {$(`#n4`).show();});
            $("#n3").show();
        }
    }
});
