initialize("/game/api/startGame/", "POST", (game) => {
    "use strict";

    // Initialization and globals
    let maxUser;
    let maxAgent;
    let agentTime = 1500;
    let animateTime = 100;
    let waitTime = 1000;
    let startTime = performance.now();
    let endTime = performance.now();
    let currentA = game.capital;
    let currentB = 0;
    let scoreA = 0;
    let scoreB = 0;
    let receiveAText = "";
    let sendAUserText = "";
    let sendBUserText = "";
    let sendAAgentText = "";
    let sendBAgentText = "";
    // let doneRequiredBool = (game.doneRequired !== null);
    let turn = 1;
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
        // if (doneRequiredBool) {
        //     $("#nameA").text(game.username);
        //     $("#nameB").text("???");
        // }
        // else {
        $("#nameA").text(game.username);
        $("#nameB").text(game.agentname);
        // }
        receiveAText = "you get "+game.capital+" coins to start";
        sendAUserText = "you keep ";
        sendBUserText = "they get ";
        sendAAgentText = "you get ";
        sendBAgentText = "they keep ";
        $("#ts-progress").css('background-color', 'var(--myPink)');
        $("#ys-progress").css('background-color', 'var(--myTeal)');
        $("#ts-num").css('color', 'var(--myPink)');
        $("#ys-num").css('color', 'var(--myTeal)');
        $("#submit").prop('disabled', true);
        $("#loading").hide();
    }
    else {
        // if (doneRequiredBool) {
        //     $("#nameA").text("???");
        //     $("#nameB").text(game.username);
        // }
        // else {
        $("#nameA").text(game.agentname);
        $("#nameB").text(game.username);
        // }
        receiveAText = "they get "+game.capital+" coins to start";
        sendAUserText = "you get ";
        sendBUserText = "they keep ";
        sendAAgentText = "they keep ";
        sendBAgentText = "you get ";
        $("#ts-progress").css('background-color', 'var(--myTeal)');
        $("#ys-progress").css('background-color', 'var(--myPink)');
        $("#ts-num").css('color', 'var(--myTeal)');
        $("#ys-num").css('color', 'var(--myPink)');
        maxAgent = game.capital;
        maxUser = 0;  // updated after agent moves
        $("#cash").hide();
        $("#form").hide();
        $("#submit").hide();
        $("#loading").show();
        // $("#submit").css('visibility', 'hidden');
        // $("#loading").css('visibility', 'visible');
    }
    var slideFunction = function () {
        var i;
        let max = maxUser;
        let val = $("#slider").val();
        let sendA = (max-val);
        let sendB = (game.userRole=="A") ? val*game.match : val;
        $("#submit").prop('disabled', false);
        $("#receiveA").css('visibility', 'hidden');
        $("#sendA").css('visibility', 'visible');
        $("#sendB").css('visibility', 'visible');
        $("#sendA").text(sendAUserText+sendA+" coins");
        $("#sendB").text(sendBUserText+sendB+" coins");
        for (i = 0; i <= game.capital*game.match; i++) {
            if (i<=sendA) {$("#c"+i+"a").css('opacity', '1');}
            else if (i<=max){$("#c"+i+"a").css('opacity', '0.5');}
            else {$("#c"+i+"a").css('opacity', '0');}
            if (i<=sendB) {$("#c"+i+"b").css('opacity', '0.5');}
            else {$("#c"+i+"b").css('opacity', '0');}
        }
    }
    $("#slider").on('change', slideFunction);
    $("#slider").on('input', slideFunction);
    $("#gameOver").hide();
    $("#finalScore").hide();
    $("#home").hide();
    $("#flair").hide();
    $("#play-again").hide();
    $("#slider").prop("disabled", true);
    $("#sendA").css('visibility', 'hidden');
    $("#sendB").css('visibility', 'hidden');
    $("#slider").prop('max', game.capital);
    $("#slider").prop('value', game.capital/2);
    animateCoins("capital");
    // switch after animation time
    setTimeout(function() {
        if (game.userRole == "A") {switchToUser();}
        else {switchToAgent();}
    }, animateTime);

    $("#submit").click(callUpdate()};

    // Change view after the user or agent moves
    function switchToUser() {
        $("#loading").hide();
        $("#cash").show();
        $("#form").show();
        $("#submit").show();
        $("#form").css('visibility', 'visible');
        $("#slider").css('visibility', 'visible');      
        $("#submit").css('visibility', 'visible');
        $("#slider").prop("disabled", false);
        if (game.userRole=="B"){
            maxUser = game.match*agentGives[agentGives.length-1];
        }
        if (maxUser>0) {
            $("#submit").prop('disabled', true);
            $("#sendA").css('visibility', 'hidden');
            $("#sendB").css('visibility', 'hidden');
            $("#slider").prop('min', 0);
            $("#slider").prop('max', maxUser);
            $("#slider").prop('value', maxUser/2);
        }
        else {
            $("#submit").prop('disabled', false);
            $("#sendA").css('visibility', 'visible');
            $("#sendB").css('visibility', 'visible');
            $("#sendA").text(sendAUserText+"0 coins");
            $("#sendB").text(sendBUserText+"0 coins");
            $("#slider").prop('min', 0);
            $("#slider").prop('max', 0);
            $("#slider").prop('value', 0);  
        }
        startTime = performance.now()  // track user response time
    }

    function switchToAgent() {
        $("#loading").hide();
        $("#cash").show();
        $("#form").show();
        $("#submit").show();
        $("#sendA").css('visibility', 'visible');
        $("#sendB").css('visibility', 'visible');
        let agentRole = "A";
        let agentGive = agentGives[agentGives.length-1];
        let agentKeep = agentKeeps[agentKeeps.length-1]
        if (game.userRole == "A") {
            $("#sendA").text(sendAAgentText+agentGive+" coins");
            $("#sendB").text(sendBAgentText+agentKeep);
            $("#slider").prop('value', agentKeeps[agentKeeps.length-1]);
            agentRole = "B";
        }
        else {
            $("#sendA").text(sendAAgentText+agentKeep+" coins");
            $("#sendB").text(sendBAgentText+agentGive+" coins");
            $("#slider").css('value', agentGives[agentGives.length-1]);
        }
        $("#slider").css('max', maxAgent);
        $("#slider").prop("disabled", true);
        $("#form").css('visibility', 'visible');            
        $("#slider").css('visibility', 'visible');      
        $("#submit").css('visibility', 'hidden');
        animateCoins(agentRole, agentGive, agentKeep)
        // switch to user after animation time
        let wait = (game.userRole=="A") ? 2*animateTime : animateTime;
        setTimeout(function() {switchToUser();}, wait);
    }

    function switchToLoading() {
        $("#loading").show();
        $("#cash").hide();
        $("#form").hide();
        $("#submit").hide();
    }

    function getUserMove() {
        let slideVal = $("#slider").val();
        let userGive;
        let userKeep;
        if (game.userRole == "A") {
            userGive = slideVal;
            userKeep = maxUser - userGive;
            maxAgent = userGive * game.match // update global
        }
        else {
            userGive = maxUser - slideVal;
            userKeep = maxUser - userGive;
        }
        userGives.push(userGive);
        userKeeps.push(userKeep);
        return [userGive, userKeep];
    }


    // Communicate with the server through AJAX (views.updateGame())
    function callUpdate() {
        endTime = performance.now() // track user response time
        let moves = getUserMove();
        $("#submit").prop('disabled', true);
        $("#submit").css('visibility', 'hidden');
        $("#sendA").css('visibility', 'hidden');
        $("#sendB").css('visibility', 'hidden');
        let userGive = moves[0];
        let userKeep = moves[1];
        let userTime = (endTime-startTime);
        if (game.userRole=="A") {
            $("#aNow").text("$"+userKeep+" — Available A");
            $("#bNow").text("Available B — $"+(game.match*userGive));
        }
        else {
            $("#aNow").text("$"+(agentKeeps[agentKeeps.length-1]+userGive)+" — Available A");
            $("#bNow").text("Available B — $"+userKeep);
        }
        animateCoins(game.userRole, userGive, userKeep);
        // switch immediately to loading
        switchToLoading();
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
                let wait = (game.userRole=="A") ? animateTime+agentTime : 2*animateTime+agentTime;
                setTimeout(function () {switchToAgent();}, wait);
            }
        });
        return false;
    }

    // Animations
    function animateCapital(i) {
        if (i>game.capital){return;} // base case
        setTimeout(() => {
            $("#c"+i+"a").css('opacity', '1');
            animateCapital(i+1); // recursive call
        }, animateTime/game.capital);   
    }
    function animateGiveA(i, AtoB) {
        if (i>=AtoB){return;} // base case
        setTimeout(() => {
            $("#c"+(game.capital-i)+"a").css('opacity', '0');
            animateGiveA(i+1, AtoB); // recursive call
        }, animateTime/AtoB);   
    }
    function animateGetB(i, AtoB) {
        if (i>AtoB*game.match){return;} // base case
        setTimeout(() => {
            $("#c"+i+"b").css('opacity', '1');
            animateGetB(i+1, AtoB); // recursive call
        }, animateTime/(3*AtoB);   
    }
    function animateGiveB(i, BtoA, bNow) {
        console.log(bNow);
        if (i>(BtoA-1)){return;} // base case
        setTimeout(() => {
            $("#c"+(bNow-i)+"b").css('opacity', '0');
            animateGiveB(i+1, BtoA, bNow); // recursive call
        }, animateTime/BtoA);   
    }
    function animateGetA(i, BtoA, aNow) {
        if (i>BtoA){return;} // base case
        setTimeout(() => {
            $("#c"+(aNow+i)+"a").css('opacity', '1');
            animateGetA(i+1, BtoA, aNow); // recursive call
        }, animateTime/BtoA);   
    }
    function animateEmptyA(i, aOut) {
        if (i>aOut){return;} // base case
        setTimeout(() => {
            $("#c"+(aOut-i)+"a").css('opacity', '0');
            animateEmptyA(i+1, aOut); // recursive call
        }, animateTime/aOut);
    }
    function animateEmptyB(i, bOut) {
        if (i>bOut){return;} // base case
        setTimeout(() => {
            $("#c"+(bOut-i)+"b").css('opacity', '0');
            animateEmptyB(i+1, bOut); // recursive call
        }, animateTime/bOut);
    }
    function animateScoreA() {
        if (scoreA==0){return;}
        let widthA = (100-20)*scoreA/(5*game.capital*game.match)
        let scoreBar = (game.userRole=="A") ? $("#ys-progress") : $("#ts-progress");
        let scoreNum = (game.userRole=="A") ? $("#ys-num") : $("#ts-num");
        scoreNum.css('color', 'var(--myWhite)');
        scoreBar.animate({
            'width': widthA+"%",
            }, animateTime);
        $({countNum: scoreNum.text()}).animate({
            countNum: scoreA},
            {
                duration: animateTime,
                easing: 'linear',
                step: function () {
                    scoreNum.text(Number(this.countNum).toFixed());
                }
            });        
    }
    function animateScoreB() {
        if (scoreA==0){return;}
        let widthB = (100-20)*scoreB/(5*game.capital*game.match)
        let scoreBar = (game.userRole=="A") ? $("#ts-progress") : $("#ys-progress");
        let scoreNum = (game.userRole=="A") ? $("#ts-num") : $("#ys-num");
        scoreNum.css('color', 'var(--myWhite)');
        scoreBar.animate({
            'width': widthB+"%",
            }, animateTime);
        $({countNum: scoreNum.text()}).animate({
            countNum: scoreB},
            {
                duration: animateTime,
                easing: 'linear',
                step: function () {
                    // scoreNum.text(Math.round(this.countNum));
                    scoreNum.text(Number(this.countNum).toFixed());
                }
            });               
    }
    function animateCoins(move, give=null, keep=null){
        if (move=="capital") {
            $("#receiveA").text(receiveAText);
            animateCapital(1);
            currentA = game.capital;
        }
        if (move=="A"){
            animateGiveA(0, give);
            animateGetB(0, give);
            currentA = keep;
            currentB = game.match*give;
        }
        if (move=="B") {
            animateGiveB(0, give, currentB);
            animateGetA(1, give, currentA);
            currentA += give;
            currentB -= give;
            setTimeout(()=> {finishTurn(animateTime);}, animateTime);
        }
    }

    function animateBonus() {
        let score = (game.userRole=="A") ? scoreA : scoreB;
        let width = 0;
        let winnings = 0.0;
        for (let thr=0; thr<game.bonus.length; thr++) {
            if (score>=game.bonus[thr][0]) {
                width=(100-20)*game.bonus[thr][0]/(game.rounds*game.capital*game.match);
                winnings=game.bonus[thr][1];
            }
        }      
        let bonusBar = $("#bonus-progress");
        let bonusNum = $("#bonus-num");
        bonusBar.animate({
            'width': width+"%",
            }, animateTime);
        $({countNum: bonusNum.text()}).animate({
            countNum: winnings},
            {
                duration: animateTime,
                easing: 'linear',
                step: function () {
                    let num = (Math.round(100*Number(this.countNum))/100);
                    bonusNum.text("$"+num);
                }
            });           
    }

    function animateTurn() {
        let width = (100-20)*turn/game.rounds;
        $("#turn-progress").animate({
            'width': width+"%",
            }, animateTime);
        $({countNum: $("#turn-num").text()}).animate({
            countNum: turn},
            {
                duration: animateTime,
                easing: 'linear',
                step: function () {
                    let num = Math.max(turn-1, Math.round(Number(this.countNum)))
                    $("#turn-num").text(num+"/"+game.rounds);
                }
            });           
    }
    function finishTurn() {
        turn++;
        if (game.userRole=="A"){
            scoreA = userRewards.reduce((a, b) => a + b, 0);
            scoreB = agentRewards.reduce((a, b) => a + b, 0);
        }
        else {
            scoreA = agentRewards.reduce((a, b) => a + b, 0);
            scoreB = userRewards.reduce((a, b) => a + b, 0);
        }
        setTimeout(()=> {
            console.log('current A finishTurn', currentA);
            console.log('current B finishTurn', currentB);
            animateEmptyA(0, currentA);
            animateEmptyB(0, currentB);
            animateScoreA();
            animateScoreB();
            animateBonus();
            animateTurn();
        }, animateTime);
        setTimeout(()=> {
            currentA = 0;
            currentB = 0;
            animateCoins('capital');
        }, 2*animateTime+waitTime);
    }

    // Final page after game is complete

    function finishGame() {
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
        $("#loading").remove();
        $("#cash").remove();
        $("#form").remove();
        $("#currently").hide();
        $("#sendA").remove();
        $("#sendB").remove();
        $("#submit").remove();
        $("#slider").remove();
        $("#aNow").remove();
        $("#bNow").remove();
        $("#gameOver").show();
        $("#finalScore").show();
        $("#home").show();
        $("#flair").show();
        $("#play-again").show();
    }
});
