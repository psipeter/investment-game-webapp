initialize("/game/api/status/", "GET", (status) => {
    "use strict";

    let doneConsentBool = (status.doneConsent !== null);
    let doneSurveyBool = (status.doneSurvey !== null);
    let doneTutorialBool = (status.doneTutorial !== null);
    let doneGamesBool = (status.doneGames !== null);
    let doneCashBool = (status.doneCash !== null);

    $("#ID").text(status.username);

    // Redirect on click
    $('#information-box').click(function(e) {window.location.href=$(this).attr("href");});
    $('#consent-box').click(function(e) {window.location.href=$(this).attr("href");});
    $('#survey-box').click(function(e) {window.location.href=$(this).attr("href");});
    $('#tutorial-box').click(function(e) {window.location.href=$(this).attr("href");});
    $('#game-box').click(function(e) {window.location.href=$(this).attr("href");});
    $('#cash-box').click(function(e) {window.location.href=$(this).attr("href");});
    $('#feedback-box').click(function(e) {window.location.href=$(this).attr("href");});

    $('#information-text').text('Information [✔]');
    $('#consent-text').text('Consent [✔]');
    if (doneSurveyBool) {
        $('#survey-text').text('Survey [✔]');
    }
    if (doneTutorialBool) {
        $('#tutorial-text').text('Tutorial [✔]');
    }
    if (doneSurveyBool & doneTutorialBool) {
        $('#game-text').text('Play Games');
    }
    else {
        $('#game-box').addClass('inactive');
        $('#game-box').off('click');
        $('#game-box').click(function(e) {alert("To play games, first complete the tutorial and the survey");});
    }
    if (doneGamesBool) {
        $('#game-text').text('Play Games [✔]');
        $('#game-box').addClass('inactive');
        $('#game-box').off('click');
    }
    if (doneCashBool) {
        $('#cash-text').text('HIT Code / Cash Out [✔]');
    }
    else {
        // if (doneSurveyBool & doneTutorialBool & doneGamesBool) {
        if (doneSurveyBool & doneTutorialBool & status.nGames > 0) {
            $('#cash-text').text('HIT Code / Cash Out');
        }
        else {
            $('#cash-box').addClass('inactive');
            $('#cash-box').off('click');
            $('#cash-box').click(function(e) {alert("Complete at least one game");});
        }
    }
});
