$(function() {  // on page load
    let progress = 0;
    let maxProgress = 9;
    let fadeTime = 1000;
    updateProgress();
    updateMain();  // Fade in first page

    // Redirect on click
    $('#next').click(function(e) {
        updateMain();
        updateProgress();
    });
    $('#back').click(function(e) {
        progress = Math.max(0, progress-1);
        updateMain();
        updateProgress();
    });

    // update progress bar
    function updateProgress(e) {
        let width = Math.min(100, Math.max(0, 100*progress/maxProgress));
        $("#progress-bar-fg").width(width+"%");
    }

    // load new minipage
    function updateMain(e) {    
        $('#m1').hide();
        $('#m2').hide();
        $('#m3').hide();
        $('#m4').hide();
        $('#m5').hide();
        $('#m6').hide();
        $('#m7').hide();
        $('#m8').hide();
        $('#m9').hide();
        $('#m1').children().fadeOut(0);
        $('#m2').children().fadeOut(0);
        $('#m3').children().fadeOut(0);
        $('#m4').children().fadeOut(0);
        $('#m5').children().fadeOut(0);
        $('#m6').children().fadeOut(0);
        $('#m7').children().fadeOut(0);
        $('#m8').children().fadeOut(0);
        $('#m9').children().fadeOut(0);
        resetVals("m2");
        resetVals("m3");
        resetVals("m4");
        // $("#back").prop("disabled", true);
        $("#next").prop("disabled", true);
        if (progress<=0) {main1();}
        if (progress==1) {main2();}
        if (progress==2) {main3();}
        if (progress==3) {main4();}
        if (progress==4) {main5();}
        if (progress==5) {main6();}
        if (progress==6) {main7();}
        if (progress==7) {main8();}
        if (progress==8) {main9();}
    }

    // display and timing of main content
    function main1(e) {
        $('#m1').show();
        $('#m1a').fadeIn(fadeTime);
        setTimeout(function(){$('#m1b').fadeIn(fadeTime);}, fadeTime);
        setTimeout(function(){$('#m1c').fadeIn(fadeTime);}, 2*fadeTime);
        enableNavigation(3*fadeTime, 1);
    }

    function main2(e) {
        let capital = 10;
        let giveA = 7;
        let keepA = 3;
        let giveB = 10;
        let keepB = 20;
        $('#m2').show();
        $('#m2a').fadeIn(fadeTime);
        $('.center').fadeIn(0);        
        $('.center').children().fadeOut(0);
        $('.total').fadeIn(0);
        $('.available').fadeIn(0);
        $('.player').fadeIn(0);
        animateCapital(2*fadeTime, "m2",capital);
        setTimeout(function(){$("#m2b1").fadeIn(fadeTime);}, fadeTime);
        animateAToBTutor(4*fadeTime, "m2", giveA, keepA);
        setTimeout(function(){$("#m2b2").fadeIn(fadeTime);}, 3*fadeTime);
        animateAToB(6*fadeTime, "m2", giveA, keepA);
        setTimeout(function(){$("#m2b3").fadeIn(fadeTime);}, 5*fadeTime);
        animateBToA(8*fadeTime, "m2", keepA, giveB, keepB);
        setTimeout(function(){$("#m2b4").fadeIn(fadeTime);}, 7*fadeTime);
        animateTotal(10*fadeTime, "m2", keepA, giveB, keepB)
        setTimeout(function(){$("#m2b5").fadeIn(fadeTime);}, 9*fadeTime);
        setTimeout(function(){$('#m2c').fadeIn(fadeTime);}, 11*fadeTime);
        enableNavigation(12*fadeTime, 2);
    }

    function main3(e) {
        let capital = 10;
        let giveA = 10;
        let keepA = 0;
        let giveB = 15;
        let keepB = 15;
        let giveA2 = 10;
        let keepA2 = 0;
        let giveB2 = 0;
        let keepB2 = 30;
        $('#m3').show();
        $('#m3a').fadeIn(fadeTime);
        $('.center').fadeIn(0);        
        $('.center').children().fadeOut(0);
        $('.total').fadeIn(0);
        $('.available').fadeIn(0);
        $('.player').fadeIn(0);
        setTimeout(function(){$("#m3c").fadeIn(fadeTime);}, 1*fadeTime);
        animateCapital(2*fadeTime, "m3", capital);
        animateAToB(3*fadeTime, "m3", giveA, keepA);
        animateBToA(4*fadeTime, "m3", keepA, giveB, keepB);
        animateTotal(5*fadeTime, "m3", keepA, giveB, keepB)
        setTimeout(function(){$("#m3c2").fadeIn(fadeTime);}, 5*fadeTime);
        setTimeout(function(){
            resetVals("m3");
            $("#m3c").css('color', 'gray');
            $("#m3d").fadeIn(fadeTime);},
        6*fadeTime);
        animateCapital(7*fadeTime, "m3", capital);
        animateAToB(8*fadeTime, "m3", giveA2, keepA2);
        animateBToA(9*fadeTime, "m3", keepA2, giveB2, keepB2);
        setTimeout(function(){$("#m3d2").fadeIn(fadeTime);}, 10*fadeTime);
        animateTotal(10*fadeTime, "m3", keepA2, giveB2, keepB2)
        setTimeout(function(){
            resetVals("m3");
            $("#m3d").css('color', 'gray');
            $("#m3c").fadeOut(fadeTime);
            $("#m3d").fadeOut(fadeTime);},
        11*fadeTime);
        setTimeout(function(){$("#m3e").fadeIn(fadeTime);}, 12*fadeTime);
        enableNavigation(13*fadeTime, 3);
    }

    function main4(e) {
        $('#m4').show();
        $('#m4a').fadeIn(fadeTime);
        $('.total').fadeIn(0);
        $('.available').fadeIn(0);
        $('.player').fadeIn(0);

        let capital = 10;
        let maxUser = capital;
        $("#slider").attr('max', maxUser);
        $("#slider").attr('value', maxUser/2);
        $("#slider").prop("disabled", false);
        $("#submit").prop('disabled', true);
        $("#slider").on('change', function () {
            // let preA = (userRole=="A") ? "Send $" : "Keep $";
            // let preB = (userRole=="A") ? "Send $" : "Keep $";
            let max = maxUser;
            let val = $("#slider").val();
            $("#submit").prop('disabled', false);
            $("#sendA").css('visibility', 'visible');
            $("#sendB").css('visibility', 'visible');
            $("#sendA").text("Keep $"+(max-val));
            $("#sendB").text("Send $"+val);
        });
        $("#slider").on('input', function () {
            let max = maxUser;
            let val = $("#slider").val();
            $("#submit").prop('disabled', false);
            $("#sendA").css('visibility', 'visible');
            $("#sendB").css('visibility', 'visible');
            $("#sendA").text("Keep $"+(max-val));
            $("#sendB").text("Send $"+val);
        });
        $("#submit").css('visibility', 'hidden');
        $("#sendA").css('visibility', 'hidden');
        $("#sendB").css('visibility', 'hidden');
        animateCapital(fadeTime, "m4", capital);
        setTimeout(function(){
            $("#cash").fadeIn(fadeTime);
            $("#form").fadeIn(fadeTime);
            $("#submit").fadeIn(fadeTime);
            $("#submit").css('visibility', 'visible');
            $("#submit").prop('disabled', true);
            $("#m4a").fadeOut(fadeTime/2);
            $("#m4c").fadeIn(fadeTime);},
        2*fadeTime);
        $("#submit").click(function () {
            let giveA = Number($("#slider").val());
            let keepA = maxUser - giveA;
            let giveB = 0;
            let keepB = 3*giveA;
            $("#m4c").fadeOut(fadeTime/2);
            $("#m4d").fadeIn(fadeTime);
            $("#submit").prop('disabled', true);
            $("#submit").css('visibility', 'hidden');
            $("#slider").css('visibility', 'hidden');
            $("#sendA").css('visibility', 'hidden');
            $("#sendB").css('visibility', 'hidden');
            $("#cash").fadeOut(fadeTime/2);
            $("#form").fadeOut(fadeTime/2);
            $("#submit").fadeOut(fadeTime/2);
            $("#loading").fadeIn(fadeTime);
            // $("#transfer").fadeOut(fadeTime/2);
            animateAToB(0, "m4", giveA, keepA);
            setTimeout(function() {
                $("#loading").fadeOut(fadeTime/2);
                $("#slider").prop("disabled", true);
                $("#cash").fadeIn(fadeTime);
                $("#form").fadeIn(fadeTime);
                $("#submit").fadeIn(fadeTime);
                $("#sendA").css('visibility', 'visible');
                $("#sendB").css('visibility', 'visible');
                $("#sendA").text(giveB);
                $("#sendB").text(keepB);
                $("#slider").prop('max', keepB);
                $("#slider").prop('value', keepB);
                $("#form").css('visibility', 'visible');            
                $("#slider").css('visibility', 'visible');      
                $("#submit").css('visibility', 'hidden');
                }, 2*fadeTime); 
            animateBToA(2*fadeTime, "m4", keepA, giveB, keepB);
            animateTotal(3*fadeTime, "m4", keepA, giveB, keepB);
            setTimeout(function() {$("#m4d").fadeOut(fadeTime/2);}, 2*fadeTime);
            setTimeout(function() {$("#m4e").fadeIn(fadeTime);}, 2*fadeTime);
            setTimeout(function() {$("#m4e").fadeOut(fadeTime/2);}, 4*fadeTime);
            setTimeout(function() {$("#m4f").fadeIn(fadeTime);}, 4*fadeTime);
            // setTimeout(function() {$("#transfer").fadeOut(fadeTime/2);}, 4*fadeTime);
            setTimeout(function() {$("#cash").fadeOut(fadeTime/2);}, 4*fadeTime);
            setTimeout(function() {$("#form").fadeOut(fadeTime/2);}, 4*fadeTime);
            setTimeout(function() {$("#submit").fadeOut(fadeTime/2);}, 4*fadeTime);
            setTimeout(function() {$("#m4g").fadeIn(fadeTime);}, 5*fadeTime);
            enableNavigation(6*fadeTime, 4);
        });
    }


    function main5(e) {
        $('#m5').show();
        $('#m5a').fadeIn(fadeTime);
        $('#img5').fadeIn(fadeTime);
        setTimeout(function(){$('#m5b').fadeIn(fadeTime);}, fadeTime);
        setTimeout(function(){$('#m5c').fadeIn(fadeTime);}, 2*fadeTime);
        setTimeout(function(){$('#m5d').fadeIn(fadeTime);}, 2*fadeTime);
        enableNavigation(3*fadeTime, 5);
    }

    function main6(e) {
        $('#m6').show();
        $('#m6a').fadeIn(fadeTime);
        $('#img6').fadeIn(fadeTime);
        setTimeout(function(){$('#m6b').fadeIn(fadeTime);}, fadeTime);
        setTimeout(function(){$('#m6c').fadeIn(fadeTime);}, 2*fadeTime);
        setTimeout(function(){$('#m6d').fadeIn(fadeTime);}, 2*fadeTime);
        enableNavigation(3*fadeTime, 6);
    }

    function main7(e) {
        $('#m7').show();
        $('#m7a').fadeIn(fadeTime);
        $('#img7').fadeIn(fadeTime);
        setTimeout(function(){$('#m7b').fadeIn(fadeTime);}, fadeTime);
        setTimeout(function(){$('#m7c').fadeIn(fadeTime);}, 2*fadeTime);
        setTimeout(function(){$('#m7d').fadeIn(fadeTime);}, 2*fadeTime);
        enableNavigation(3*fadeTime, 7);
    }

    function main8(e) {
        $('#m8').show();
        $('#m8a').fadeIn(fadeTime);
        $('#img8').fadeIn(fadeTime);
        setTimeout(function(){$('#m8b').fadeIn(fadeTime);}, fadeTime);
        setTimeout(function(){$('#m8c').fadeIn(fadeTime);}, 2*fadeTime);
        setTimeout(function(){$('#m8d').fadeIn(fadeTime);}, 2*fadeTime);
        enableNavigation(3*fadeTime, 8);
    }

    function main9(e) {
        $('#m9').show();
        $('#m9a').fadeIn(fadeTime);
        $('#img9').fadeIn(fadeTime);
        setTimeout(function(){$('#m9b').fadeIn(fadeTime);}, fadeTime);
        setTimeout(function(){$('#m9c').fadeIn(fadeTime);}, 2*fadeTime);
        enableNavigation(3*fadeTime, 9);
    }

    // Functions

    function animateCapital(timeout, addTo, capital) {
        setTimeout(function(){
            $("#aNow"+addTo).text("$"+capital+" — Available A");
            $("#bNow"+addTo).text("Available B — $0");
            let cap = $("#aNow"+addTo).clone();
            cap.attr("id", "cap");
            cap.text("$"+capital)
            cap.appendTo("#"+addTo);
            cap.css("position", "relative");
            cap.css("left", "-=10%");
            cap.animate({
                left : "+=10%",
                'opacity': 0,
                }, fadeTime,
                function() {cap.remove();});
        }, timeout);
    }
    function animateAToBTutor(timeout, addTo, giveA, keepA) {
        setTimeout(function(){
            $("#aNow"+addTo).text("$"+keepA+" — Available A");
            $("#bNow"+addTo).text("Available B — $"+giveA);
            let toB = $("#aNow"+addTo).clone();
            let width = $("#bNow"+addTo).width();
            toB.attr("id", "toB");
            toB.text("$"+giveA);
            toB.css("position", "relative");
            // toB.width("5%");
            toB.appendTo("#"+addTo);
            toB.animate({
                left: "+="+width,
                width: "-="+width, // prevent empty space on right
                'color': $("#bNow"+addTo).css('color'),
                'opacity': 0,
                }, fadeTime,
                function() {toB.remove();});
        }, timeout);
    }
    function animateAToB(timeout, addTo, giveA, keepA) {
        setTimeout(function(){
            let toB = $("#aNow"+addTo).clone();
            let width = $("#bNow"+addTo).width();
            let matchB = $("#bNow"+addTo).clone();
            $("#aNow"+addTo).text("$"+keepA + " — Available A");
            $("#bNow"+addTo).text("Available B — $"+3*giveA);
            toB.text("$"+giveA);
            toB.attr("id", "toB2");
            toB.css("position", "relative");
            // toB.width("5%");
            toB.appendTo("#"+addTo);
            toB.animate({
                left: "+="+width,
                width: "-="+width, // prevent empty space on right
                'color': $("#bNow"+addTo).css('color'),
                'opacity': 0,
                }, fadeTime,
                function() {toB.remove()});
            matchB.attr("id", "matchB");
            matchB.css("position", "relative");
            matchB.css("left", "+=10%");
            // matchB.width("5%");
            matchB.text("$"+2*giveA);
            matchB.appendTo("#"+addTo);
            matchB.animate({
                left: "-=10%",
                'opacity': 0,
                }, fadeTime,
                function() {matchB.remove();});
        }, timeout);
    }
    function animateBToA(timeout, addTo, keepA, giveB, keepB) {
        setTimeout(function(){
            let width = $("#bNow"+addTo).width();
            $("#aNow"+addTo).text("$"+(keepA+giveB)+" — Available A");
            let toA = $("#bNow"+addTo).clone();
            $("#bNow"+addTo).text("Available B — $"+keepB);
            toA.attr("id", "toA2");
            toA.text("$"+giveB);
            toA.css("position", "relative");
            toA.appendTo("#"+addTo);
            toA.animate({
                left: "-="+width,
                // width: "-="+width, // prevent empty space on left
                'color': $("#aNow"+addTo).css('color'),
                'opacity': 0,
                }, fadeTime,
                function() {toA.remove();});
        }, timeout);
    }
    function animateTotal(timeout, addTo, keepA, giveB, keepB){
        setTimeout(function(){
            $("#aTotal"+addTo).text("$"+(keepA+giveB)+" — Total A");
            $("#bTotal"+addTo).text("Total B — $"+keepB);
            let upA = $("#aNow"+addTo).clone();
            let upB = $("#bNow"+addTo).clone();
            let mTotal = parseInt($("#aTotal"+addTo).offset().top);
            let mNow = parseInt($("#aNow"+addTo).offset().top);
            let dY = mNow - mTotal;
            $("#aNow"+addTo).text("$0 — Available A");
            $("#bNow"+addTo).text("Available B — $0");
            upA.attr("id", "upA");
            upA.css("position", "relative");
            upA.text("$"+(keepA+giveB));
            upA.appendTo("#"+addTo);
            upA.animate({
                top: "-="+dY,
                'opacity': 0,
                }, fadeTime,
                function() {upA.remove();});        
            upB.attr("id", "upB");
            upB.css("position", "relative");
            upB.text("$"+keepB);
            upB.appendTo("#"+addTo);
            upB.animate({
                top: "-="+dY,
                'opacity': 0,
                }, fadeTime,
                function() {upB.remove();});
        }, timeout);
    }



    function resetVals(addTo) {
        $("#aNow"+addTo).text("$0 — Available A");
        $("#bNow"+addTo).text("Available B — $0");
        $("#aTotal"+addTo).text("$0 — Total A");
        $("#bTotal"+addTo).text("Total B — $0");
    }

    function enableNavigation(timeout, prog) {
         setTimeout(function(){
            $("#back").prop("disabled", false);
            if (prog < 9) {
                $("#next").prop("disabled", false);
            }
            progress = prog;
        }, timeout);
    }

});  // document load end