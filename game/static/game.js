initialize("/game/api/startGame/", "POST", (game) => {
    "use strict";

    // Initialization and globals
    let maxUser;
    let maxAgent;
    let agentTime = 2000*Math.random();
    let animateTime = 1500;
    let startTime = performance.now();
    let endTime = performance.now();
    let doneGames = false
    let message = null
    let lastKeep = 0;
    let sendAUserText = "";
    let sendBUserText = "";
    let sendAAgentText = "";
    let sendBAgentText = "";
    let doneRequiredBool = (game.doneRequired !== null);
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
        if (doneRequiredBool) {
            $("#nameA").text("A ("+game.userName+")");
            $("#nameB").text("B [hidden]");
        }
        else {
            $("#nameA").text("A ("+game.userName+")");
            $("#nameB").text("B ("+game.agentName+")");
        }
        sendAUserText = "Keep $";
        sendBUserText = "Give $";
        sendAAgentText = "Give $";
        sendBAgentText = "Keep $";
        $("#submit").prop('disabled', true);
        $("#loading").hide();
    }
    else {
        if (doneRequiredBool) {
            $("#nameA").text("A [hidden]");
            $("#nameB").text("B ("+game.userName+")");
        }
        else {
            $("#nameA").text("A ("+game.agentName+")");
            $("#nameB").text("B ("+game.userName+")");
        }
        sendAUserText = "Give $";
        sendBUserText = "Keep $";
        sendAAgentText = "Keep $";
        sendBAgentText = "Give $";
        maxAgent = game.capital;
        maxUser = 0;  // updated after agent moves
        $("#cash").hide();
        $("#form").hide();
        $("#submit").hide();
        $("#loading").show();
        // $("#submit").css('visibility', 'hidden');
        // $("#loading").css('visibility', 'visible');
    }
    $("#slider").on('change', function () {
        // let preA = (game.userRole=="A") ? "Send $" : "Keep $";
        // let preB = (game.userRole=="A") ? "Send $" : "Keep $";
        let max = maxUser;
        let val = $("#slider").val();
        $("#submit").prop('disabled', false);
        $("#sendA").css('visibility', 'visible');
        $("#sendB").css('visibility', 'visible');
        $("#sendA").text(sendAUserText+(max-val));
        $("#sendB").text(sendBUserText+val);
    });
    $("#slider").on('input', function () {
        let max = maxUser;
        let val = $("#slider").val();
        $("#submit").prop('disabled', false);
        $("#sendA").css('visibility', 'visible');
        $("#sendB").css('visibility', 'visible');
        $("#sendA").text(sendAUserText+(max-val));
        $("#sendB").text(sendBUserText+val);
    });
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
    animateAvailable("capital");
    // switch after animation time
    setTimeout(function() {
        if (game.userRole == "A") {switchToUser();}
        else {switchToAgent();}
    }, animateTime);


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
            $("#sendA").text(sendAUserText+"0");
            $("#sendB").text(sendBUserText+"0");
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
            $("#sendA").text(sendAAgentText+agentGive);
            $("#sendB").text(sendBAgentText+agentKeep);
            $("#slider").prop('value', agentKeeps[agentKeeps.length-1]);
            agentRole = "B";
        }
        else {
            $("#sendA").text(sendAAgentText+agentKeep);
            $("#sendB").text(sendBAgentText+agentGive);
            $("#slider").css('value', agentGives[agentGives.length-1]);
        }
        $("#slider").css('max', maxAgent);
        $("#slider").prop("disabled", true);
        $("#form").css('visibility', 'visible');            
        $("#slider").css('visibility', 'visible');      
        $("#submit").css('visibility', 'hidden');
        animateAvailable(agentRole, agentGive, agentKeep)
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
    $("#submit").click(function callUpdate() {
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
        animateAvailable(game.userRole, userGive, userKeep);
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
                doneGames = returnData.doneGames;
                message = returnData.message;
                agentTime = 2000*Math.random();
                let wait = (game.userRole=="A") ? animateTime+agentTime : 2*animateTime+agentTime;
                setTimeout(function () {switchToAgent();}, wait);
            }
        });
        return false;
    });


    // Animate numbers and images changing
    function animateAvailable(move, give=null, keep=null){
        if (move=="capital") {
            $("#aNow").text("$"+game.capital+" — Available A");
            $("#bNow").text("Available B — $0");
            let cap = $("#aNow").clone();
            cap.attr("id", "cap");
            cap.text("$"+game.capital)
            cap.appendTo("body");
            cap.css("position", "relative");
            cap.css("left", "-=10%");
            cap.animate({
                left : "+=10%",
                'opacity': 0,
                }, animateTime,
                function() {cap.remove();});
        }
        if (move=="A"){
            lastKeep = keep;
            let toB = $("#aNow").clone();
            let width = $("#bNow").width();
            let matchB = $("#bNow").clone();
            $("#aNow").text("$"+keep+" — Available A");
            $("#bNow").text("Available B — $"+game.match*give);
            toB.text("$"+give);
            toB.attr("id", "toB2");
            toB.css("position", "relative");
            toB.appendTo("body");
            toB.animate({
                left: "+="+width,
                width: "-="+width, // prevent empty space on right
                'color': $("#bNow").css('color'),
                'opacity': 0,
                }, animateTime,
                function() {toB.remove()});
            matchB.attr("id", "matchB");
            matchB.css("position", "relative");
            matchB.css("left", "+=10%");
            // matchB.width("5%");
            matchB.text("$"+2*give);
            matchB.appendTo("body");
            matchB.animate({
                left: "-=10%",
                'opacity': 0,
                }, animateTime,
                function() {matchB.remove();});
        }
        if (move=="B") {
            console.log('move B');
            let width = $("#bNow").width();
            $("#aNow").text("$"+(lastKeep+give)+" — Available A");
            let toA = $("#bNow").clone();
            $("#bNow").text("Available B — $"+keep);
            toA.attr("id", "toA2");
            toA.text("$"+give);
            toA.css("position", "relative");
            toA.appendTo("body");
            toA.animate({
                left: "-="+width,
                'color': $("#aNow").css('color'),
                'opacity': 0,
                }, animateTime,
                function() {
                    toA.remove();
                    animateTotal((lastKeep+give), keep);
                    if (complete) {setTimeout(function() {
                        gameOver();}, animateTime);}
                    else {setTimeout(function() {
                        turn += 1;
                        $("#turn").text("Turn "+turn+"/5");
                        animateAvailable('capital');}, animateTime);}
                });
        }
    }

    function animateTotal(a,b) {
        let upA = $("#aNow").clone();
        let upB = $("#bNow").clone();
        let mTotal = parseInt($("#aTotal").offset().top);
        let mNow = parseInt($("#aNow").offset().top);
        let dY = mNow - mTotal;
        let userScore = userRewards.reduce((a, b) => a + b, 0);
        let agentScore = agentRewards.reduce((a, b) => a + b, 0);
         if (game.userRole == "A") {
            $("#aTotal").text("$"+userScore+" — Total A");
            $("#bTotal").text("Total B — $"+agentScore);
        }
        else {
            $("#aTotal").text("$"+agentScore+" — Total A");
            $("#bTotal").text("Total B — $"+userScore);
        }
        $("#aNow").text("$0 — Available A");
        $("#bNow").text("Available B — $0");
        upA.attr("id", "upA");
        upA.css("position", "relative");
        upA.text("$"+a);
        upA.appendTo("body");
        upA.animate({
            top: "-="+dY,
            'opacity': 0,
            }, animateTime,
            function() {upA.remove();});        
        upB.attr("id", "upB");
        upB.css("position", "relative");
        upB.text("$"+b);
        upB.appendTo("body");
        upB.animate({
            top: "-="+dY,
            'opacity': 0,
            }, animateTime,
            function() {upB.remove();});
    }


    // Final page after game is complete

    function gameOver() {
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
