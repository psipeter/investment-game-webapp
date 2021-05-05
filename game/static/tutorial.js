initialize("/game/api/startTutorial/", "POST", (game) => {

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
    let turn = 1;
    let complete = false
    let userGive;
    let userKeep;
    let userGives = game.userGives;
    let userKeeps = game.userKeeps;
    let userRewards = game.userRewards;
    let agentGives = game.agentGives;
    let agentKeeps = game.agentKeeps;
    let agentRewards = game.agentRewards;
    let isSliding = false;
    maxUser = game.capital;
    maxAgent = 0;  // updated after user moves
    $("#loadGame").fadeOut(quickTime).children().fadeOut(quickTime);
    setTimeout(function() {$("#loadGame").remove();}, quickTime);
    $("#bar-area").show().children().fadeIn(quickTime);
    $("#imgA").fadeIn(quickTime)
    $("#imgB").fadeIn(quickTime)
    $("#imgA").attr('src', `/static/user${game.avatar}A.svg`);
    // $("#imgB").css('opacity', '0.5')
    $("#ts-box").css('background-color', 'var(--myPink)');
    $("#ys-box").css('background-color', 'var(--myTeal)');
    $(window).on('beforeunload', function(e) {return false;});
    $(window).resize(resizeSlider);
    $(document).mousemove(function(e) {moveSlide(e);});
    $(document).mouseup(function(e) {stopSlide(e);});
    let sliderLeft = document.getElementById("slider-left");
    let sliderThumb = document.getElementById("slider-thumb");
    let sliderRight = document.getElementById("slider-right");

    // Add navigation
    linkNotes();
    function linkNotes() {
        let notes = $(".note");
        for (let n=0; n<notes.length; n++) {
            notes.eq(n).hide();
            notes.eq(n).append(`<div id='n-nav${n}' class='n-nav'> </div>`);
            $(`#n-nav${n}`).append(`<p id='n-back${n}' class="back">back</p>`);
            $(`#n-nav${n}`).append(`<p id='n-next${n}'class="next">next</p>`);
            addNav(n);
        }
    }
    function addNav(n){
        $(`#n-back${n}`).addClass('back')
        $(`#n-back${n}`).removeClass('inactive')
        $(`#n-back${n}`).click(function() {$(`#n${n}`).fadeOut(quickTime); $(`#n${n-1}`).fadeIn(quickTime);})
        $(`#n-next${n}`).addClass('next')
        $(`#n-next${n}`).removeClass('inactive')
        $(`#n-next${n}`).click(function() {$(`#n${n}`).fadeOut(quickTime); $(`#n${n+1}`).fadeIn(quickTime);})
    }
    function removeNav(element){element.off('click'); element.addClass('inactive');}
    removeNav($(`#n-back0`));
    removeNav($("#n-next4"));

    // Tutorial Sequence
    $("#turn-box").hide();
    $("#ts-box").hide();
    $("#ys-box").hide();
    $("#bonus-box").hide();
    $("#n-area").show();
    $("#n4_2").hide();
    $("#n0").fadeIn(quickTime);
    $("#n-next0").click(function() {$("#sendA").text("Investor").fadeIn(quickTime); $("#sendB").text("Trustee").fadeIn(quickTime);});
    $("#n-next1").click(function() {
        $("#turn-box").show().children().fadeIn(quickTime);
        $("#turn-box1").css('visibility', 'visible');
        animateTurn();});
    $("#n-next2").click(function() {
        $("#ys-box").show().children().fadeIn(quickTime);
        $("#ts-box").show().children().fadeIn(quickTime);
        $("#bonus-box").show().children().fadeIn(quickTime);
        executeMove('capital');
    });
    $("#n-back3").click(function() {fastCoins(0, "a");});
    $("#n-next3").click(function() {switchToUser();});
    $("#n-back4").click(function() {$("#n4_2").fadeOut(quickTime); hideSlider(); fastCoins(0, "a"); executeMove('capital');});
    $("#submit").click(function () {
        userGive = Number($("#slider-wrapper").attr('val'));
        userKeep = maxUser - userGive;
        if (userGive==0){
            hideSlider();
            $("#warning").fadeIn(animateTime);
            setTimeout(function() {$("#warning").fadeOut(); showSlider(game.userRole, 0, maxUser, true);}, animateTime+waitTime);
        }
        else {
            $("#submit").hide();
            userGives.push(userGive);
            userKeeps.push(userKeep);
            if (game.userRole == "A") {maxAgent = userGive * game.match} // update global
            executeMove(game.userRole, userGive, userKeep);
            $("#n4").fadeOut(quickTime);
            $("#n4_2").fadeOut(quickTime);
            $("#n5").fadeIn(quickTime);
            // setTimeout(function() {hideSlider();}, animateTime+waitTime);
            hideSlider();
            removeNav($("#n-next5"));
            removeNav($("#n-back5"));
            setTimeout(function() {addNav(5); addN5Back(); addN5Next();}, animateTime+waitTime);
        }
    });
    function addN5Back(){
        $("#n-back5").click(function() {

            fastCoins(game.capital, "a");
            fastCoins(0, "b");
            currentA = game.capital;
            currentB = 0;
            hideSlider();
            switchToUser();
        });
    }
    function addN5Next() {
        $("#n-next5").click(function() {
            // code from callUpdate() and switchToAgent(), minus extra waiting and switching
            let userTime = 0;
            removeNav($("#n-next6"));
            removeNav($("#n-back6"));
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
                timeout: 7000,
                error: function() {
                    $("#loading").hide();
                    $("#slider-wrapper").hide();
                    $("#submit").hide();
                    $("#sendA").hide();
                    $("#sendB").hide();
                    $("#serverError").fadeIn(animateTime);
                },
                success: function (returnData) {
                    // update globals
                    userGives = returnData.userGives;
                    userKeeps = returnData.userKeeps;
                    userRewards = returnData.userRewards;
                    agentGives = returnData.agentGives;
                    agentKeeps = returnData.agentKeeps;
                    agentRewards = returnData.agentRewards;
                    complete = returnData.complete;
                    instructorMove();
                }
            });
        });
    }
    function instructorMove() {
        removeNav($("#n-next6"));
        removeNav($("#n-back6"));
        let agentGive = agentGives[agentGives.length-1];
        let agentKeep = agentKeeps[agentKeeps.length-1];
        let skip = (agentGive==0);
        $("#loading").fadeIn(quickTime);
        setTimeout(function() {
            $("#loading").fadeOut(quickTime);
            showSlider(game.agentRole, agentGive, agentKeep, false);
            executeMove(game.agentRole, agentGive, agentKeep, skip);
        }, agentTime);
        // setTimeout(function() {hideSlider();}, animateTime+agentTime+waitTime);
        setTimeout(function() {
            addNav(6);
            addN6Back();
            addN6Next();
        }, animateTime+agentTime+waitTime);
    }
    function addN6Back() {
        $("#n-back6").click(function() {
            fastCoins(userKeep, "a");
            fastCoins(userGive*game.match, "b");
            currentA = userKeep;
            currentB = userGive*game.match;
            hideSlider();
        });
    }
    function addN6Next() {
        // from finishTurn()
        $("#n-next6").click(function() {
            hideSlider();
            removeNav($("#n-next7"));
            removeNav($("#n-back7"));
            setTimeout(function() {addNav(7); addN7Back(); addN7Next();}, animateTime+waitTime);
            scoreA += currentA;
            scoreB += currentB;
            updateLog("score", currentA, currentB);
            animateCoins(0, currentA, -currentA, 'out', 'a');
            animateCoins(0, currentB, -currentB, 'out', 'b');
            $("#ts-box").fadeIn(quickTime);
            $("#ys-box").fadeIn(quickTime);
            animateScoreA();
            animateScoreB();
            currentA = 0;
            currentB = 0;
            turn++;
            animateTurn();
        });
    }
    function addN7Back() {
        $("#n-back7").click(function() {
            fastCoins(userKeep, "a");
            fastCoins(userGive*game.match, "b");
            currentA = userKeep;
            currentB = userGive*game.match;
            scoreA = 0;
            scoreB = 0;
            turn = 1;
            animateScoreA();
            animateScoreB();
            animateTurn();
            instructorMove();
        });        
    }
    function addN7Next() {
        $("#n-next7").click(function() {
            $("#bonus-box").css('visibility', 'visible');
            $("#bonus-box").show().children().fadeIn(quickTime);
            animateBonus();
            $(window).off('beforeunload');
            $("#n-next8").text("Tutorial Part 2");
            $("#n-next8").click(function() {window.location.href=$("#tut2").attr("href");});
        });
    }


    // Functions

    // slider 
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
        if ($("#slider-wrapper").hasClass('flipped')) {
            let leftEdge = $("#slider-wrapper").offset().left + wT/2;
            let rightEdge = $("#slider-wrapper").offset().left + wW + wT/2;
            if (x <= leftEdge) {return 1;}
            else if (x >= rightEdge) {return 0;}
            else {return 1 - (x-leftEdge)/wW;}
        }
        else {
            let leftEdge = $("#slider-wrapper").offset().left - wT/2;
            let rightEdge = $("#slider-wrapper").offset().left + wW - wT/2;
            if (x <= leftEdge) {return 0;}
            else if (x >= rightEdge) {return 1;}
            else {return (x-leftEdge)/wW;}            
        }
    }
    let updateSliderMouse = function(e) {
        let x = getX(e);
        let f = absToRel(x);
        updateSlider(f, maxUser, game.userRole);
        $("#n4_2").fadeIn(quickTime);
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
            for (let i = 0; i<=game.capital*game.match; i++) {
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

    function switchToUser() {
        startTime = performance.now();
        showSlider("A", 0, maxUser, true);
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

    // Animate top bars increasing width and counting up
    function animateTurn() {
        let box = $("#turn-box"+turn);
        box.animate({'opacity': "1"}, animateTime);
    }
    function animateScoreA() {
        let box = (game.userRole=="A") ? $("#ys-box") : $("#ts-box");
        let num = (game.userRole=="A") ? $("#ys-num") : $("#ts-num");
        // let f = scoreA / (game.turns*game.capital*game.match);  // theoretical max is never achieved
        let f = scoreA / (30);
        let w = f * parseInt($(":root").css('--boxWidth'))
        let wMin = parseInt($(":root").css('--boxWidthMin'));
        let wMax = parseInt($(":root").css('--boxWidth'));
        if (w>wMin & w<wMax) {box.animate({'width': w+"vw"}, animateTime);}
        else if (w>wMax) {box.animate({'width': wMax+"vw"}, animateTime);}
        $({count: num.text()}).animate(
                {count: scoreA},
                {duration: animateTime, step: function () {num.text(Number(this.count).toFixed());}}
        );
        setTimeout(function() {num.text(scoreA)}, animateTime); // fallback
    }
    function animateScoreB() {
        let box = (game.userRole=="B") ? $("#ys-box") : $("#ts-box");
        let num = (game.userRole=="B") ? $("#ys-num") : $("#ts-num");
        // let f = scoreA / (game.turns*game.capital*game.match);  // theoretical max is never achieved
        let f = scoreB / (30);
        let w = f * parseInt($(":root").css('--boxWidth'))
        let wMin = parseInt($(":root").css('--boxWidthMin'));
        let wMax = parseInt($(":root").css('--boxWidth'));
        if (w>wMin & w<wMax) {box.animate({'width': w+"vw"}, animateTime);}
        else if (w>wMax) {box.animate({'width': wMax+"vw"}, animateTime);}
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
        // let f = scoreA / (game.turns*game.capital*game.match);  // theoretical max is never achieved
        let f = score / (30);
        let w = f * parseInt($(":root").css('--boxWidth'))
        let wMin = parseInt($(":root").css('--boxWidthMin'));
        let wMax = parseInt($(":root").css('--boxWidth'));
        box.css('marginLeft', w+"vw");
        $({count: oldBonus}).animate(
                {count: newBonus},
                {duration: animateTime, step: function () {num.text(Number(this.count).toFixed()+"₵");}}
        );
        setTimeout(function() {num.text(newBonus+"₵")}, animateTime); // fallback
    }


});
