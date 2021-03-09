initialize("/game/api/startGame/", "POST", (game) => {

    // Initialization and globals
    "use strict";
    let maxUser;
    let maxAgent;
    let agentTime = 2000;
    let animateTime = 1000;
    let waitTime = 1000;
    let startTime = performance.now();
    let endTime = performance.now();
    let currentA = game.capital;
    let currentB = 0;
    let scoreA = 0;
    let scoreB = 0;
    // let doneRequiredBool = (game.doneRequired !== null);
    let turn = 0;
    let complete = false
    let userGives = game.userGives;
    let userKeeps = game.userKeeps;
    let userRewards = game.userRewards;
    let agentGives = game.agentGives;
    let agentKeeps = game.agentKeeps;
    let agentRewards = game.agentRewards;
    if (game.userRole == "A") {
        maxUser = game.capital;
        maxAgent = 0;  // updated after user moves
        // $("#nameA").text("YOU");
        // $("#nameB").text("them");
        $("#nameA").text(game.username);
        $("#nameB").text(game.agentname);
        $("#nameB").css('opacity', '0.5')
        $("#imgB").css('opacity', '0.5')
        $("#ts-progress").css('background-color', 'var(--myPink)');
        $("#ys-progress").css('background-color', 'var(--myTeal)');
        $("#slider").css('--sliderColor1', 'var(--myTeal');
        $("#slider").css('--sliderColor2', 'var(--myPink');
        $("#slider").css('--coinImg', 'var(--coinImg1');
    }
    else {
        $("#nameA").text(game.agentname);
        $("#nameB").text(game.username);
        // $("#nameB").text("YOU");
        // $("#nameA").text("them");
        $("#nameA").css('opacity', '0.5')
        $("#imgA").css('opacity', '0.5')
        $("#ts-progress").css('background-color', 'var(--myTeal)');
        $("#ys-progress").css('background-color', 'var(--myPink)');
        $("#slider").css('--sliderColor1', 'var(--myPink');
        $("#slider").css('--sliderColor2', 'var(--myTeal');
        $("#slider").addClass('flipped');
        $("#slider").css('--coinImg', 'var(--coinImg2');
        maxAgent = game.capital;
        maxUser = 0;  // updated after agent moves
    }
    $("#loading").hide();
    $("#arrow").hide();
    $("#game-over-area").hide();
    animateBar('turn', game.userRole);
    addThresholds();
    turn++;
    executeMove("capital");
    // switch after animation time
    setTimeout(function() {
        if (game.userRole == "A") {switchToUser();}
        else {flipArrow(); switchToAgent();}
    }, animateTime);
    $("#submit").click(callUpdate);



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


    // Change view after the user or agent moves
    function switchToAgent() {
        $("#loading").show();
        $("#arrow").hide();
        $("#submit").hide();
        // $("#form").hide();
        $("#slider").hide();
        setTimeout(function() {
            $("#loading").hide();
            flipArrow();
            $("#arrow").show();
            $("#sendA").show();
            $("#sendB").show();
            let agentRole = (game.userRole=="A") ? "B": "A";
            let agentGive = agentGives[agentGives.length-1];
            let agentKeep = agentKeeps[agentKeeps.length-1];
            if (game.userRole == "A") {
                $("#sendA").text("You get "+agentGive+" coins");
                $("#sendB").text("They keep "+agentKeep);
            }
            else {
                $("#sendA").text("They keep "+agentKeep+" coins");
                $("#sendB").text("You get " +agentGive*game.match+" coins");
            }    
            executeMove(agentRole, agentGive, agentKeep)
            let wait = (game.userRole=="A") ? 3*animateTime : animateTime;
            setTimeout(function() {
                flipArrow();
                switchToUser();
            }, wait);
        }, agentTime);
    }

    function switchToUser() {
        $("#loading").hide();
        // $("#cash").show();
        // $("#form").show();
        $("#submit").show();
        $("#slider").show();      
        $("#submit").show();
        $("#arrow").show();
        $("#slider").prop("disabled", false);
        if (game.userRole=="A"){
            //pass
        }
        else {
            maxUser = game.match*agentGives[agentGives.length-1];
        }
        if (maxUser>0) {
            $("#submit").prop('disabled', true);
            $("#sendA").hide();
            $("#sendB").hide();
            $("#slider").prop('min', 0);
            $("#slider").prop('max', maxUser);
            $("#slider").prop('value', 0);
        }
        else {
            $("#submit").prop('disabled', false);
            $("#sendA").show();
            $("#sendB").show();
            if (game.userRole=="A"){
                $("#sendA").text("Keep 0 coins");
                $("#sendB").text("Give them 0 coins");
            }
            else {
                $("#sendA").text("Give them 0 coins");
                $("#sendB").text("Keep 0 coins");                
            }
            $("#slider").prop('min', 0);
            $("#slider").prop('max', 0);
            $("#slider").prop('value', 0);  
        }
        startTime = performance.now()  // track user response time
    }

    // Communicate with the server through AJAX (views.updateGame())
    function callUpdate() {
        endTime = performance.now() // track user response time
        let userGive = Number($("#slider").val());
        let userKeep = maxUser - userGive;
        let userTime = (endTime-startTime);
        userGives.push(userGive);
        userKeeps.push(userKeep);
        if (game.userRole == "A") {maxAgent = userGive * game.match} // update global
        $("#submit").prop('disabled', true);
        $("#submit").hide();
        $("#slider").hide();
        executeMove(game.userRole, userGive, userKeep);
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
                let wait = (game.userRole=="A") ? animateTime : 3*animateTime;
                if (!complete || game.userRole=="A"){setTimeout(function () {switchToAgent();}, wait);}
            }
        });
        return false;
    }

    // Start new turn
    function finishTurn() {
        // if (game.userRole=="A"){
        //     scoreA = userRewards.reduce((a, b) => a + b, 0);
        //     scoreB = agentRewards.reduce((a, b) => a + b, 0);
        // }
        // else {
        //     scoreA = agentRewards.reduce((a, b) => a + b, 0);
        //     scoreB = userRewards.reduce((a, b) => a + b, 0);
        // }
        // todo: alignment check
        scoreA += currentA;
        scoreB += currentB;
        setTimeout(()=> {
            updateLog("score", currentA, currentB);
            animateCoins(0, currentA, -currentA, 'out', 'a');
            animateCoins(0, currentB, -currentB, 'out', 'b');
            animateBar('scoreA', "A");
            animateBar('scoreB', "B");
            animateBar('bonus', game.userRole);
        }, animateTime);
        if (complete) {
            setTimeout(()=> {
                finishGame();
            }, 2*animateTime);
        }
        else {
            setTimeout(()=> {
                animateBar('turn', game.userRole);
            }, animateTime);
            setTimeout(()=> {
                turn++;
                currentA = 0;
                currentB = 0;
                executeMove('capital');
            }, 2*animateTime);
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
    function executeMove(move, give=null, keep=null){
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
            setTimeout(()=> {$("#arrow").hide(); $("#sendA").hide(); $("#sendB").hide();}, animateTime);
        }
        if (move=="B") {
            updateLog("B", give, keep);
            animateCoins(0, currentB, -give, 'out', 'b');
            animateCoins(0, currentA, give, 'in', 'a');
            currentA += give;
            currentB -= give;
            setTimeout(()=> {$("#arrow").hide(); $("#sendA").hide(); $("#sendB").hide();}, animateTime);
            setTimeout(()=> {finishTurn();}, animateTime);
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
            $(`#l${turn}e2`).addClass("pink");
            $(`#l${turn}f1`).text("Your score increased by").append("&nbsp;");
            $(`#l${turn}f2`).text(currentUser);
            $(`#l${turn}f2`).addClass("teal");
        }
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
            widthFrac = (turn+1)/game.rounds;
            widthNew = (widthTotal-widthText) * widthFrac;
            widthNow = parseInt(bar.css('width'));
            if (widthNew > widthNow){bar.animate({'width': widthNew}, animateTime);}
            $({count: num.text()}).animate(
                {count: turn},
                {duration: animateTime, easing: 'linear', step: function () {
                    let newTurn = Math.max(turn, Math.round(Number(this.count)));
                    // don't display NaN on first steps
                    if (!isNaN(newTurn)){num.text(newTurn+"/"+game.rounds);}
                }}
            );              
        }
    }

    function animateWinnings(){
        let reward;
        let score = (game.userRole=="A") ? scoreA : scoreB;
        for (let i=0; i<game.bonus.length; i++) {
            if (score >= game.bonus[i][0]) {reward = game.bonus[i][1];}
        }
        let winObj = $("#headerW");
        let playedObj = $("#headerG");
        let win = Number(game.winnings);  // str to number
        $({count: win}).animate(
                {count: win+reward},
                {duration: animateTime, easing: 'linear', step: function () {
                    let winNew = Math.round(100*Number(this.count))/100;
                    if (!isNaN(winNew)){winObj.text("Winnings — $"+winNew.toFixed(2))};
                }}
            );
        playedObj.text("Games Played — "+(game.nGames+1));
    }

    function flipArrow() {
        if ($("#arrow").hasClass('flipped')) {$("#arrow").removeClass('flipped');}
        else ($("#arrow").addClass('flipped'))
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

    // Final page after game is complete
    function finishGame() {
        let userScore = userRewards.reduce((a, b) => a + b, 0);
        let agentScore = agentRewards.reduce((a, b) => a + b, 0);
        animateWinnings();
        if (game.userRole == "A") {
            $("#aTotal").text("$"+userScore);
            $("#bTotal").text("$"+agentScore);
        }
        else {
            $("#aTotal").text("$"+agentScore);
            $("#bTotal").text("$"+userScore);
        }
        $("#loading").hide();
        $("#submit").hide();
        $("#arrow").hide();
        $("#slider").hide();
        $("#playerA").hide();
        $("#playerB").hide();
        $("#nameA").hide();
        $("#nameB").hide();
        $("#imgA").hide();
        $("#imgB").hide();
        $("#game-over-area").show();
        $("#flair-text").show();
        if (game.nGames+1 == game.required) {
            $("#flair-text").text("Required games complete!");
        }
        $("#game-over-text").show();
        $("#play-again-text").show();
    }
});
