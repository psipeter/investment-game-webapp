initialize("/game/api/status/", "GET", (status) => {
    "use strict";

    let doneConsentBool = (status.doneConsent !== null);
    let doneSurveyBool = (status.doneSurvey !== null);
    let doneTutorialBool = (status.doneTutorial !== null);
    let doneRequiredBool = (status.doneRequired !== null);
    let doneMax = (status.doneMax !== null);
    let doneCashBool = (status.doneCash !== null);

    $("#ID").text(status.username);

    // Redirect on click
    $('#information-box').click(function(e) {window.location.href=$(this).attr("href");});
    $('#consent-box').click(function(e) {window.location.href=$(this).attr("href");});
    $('#survey-box').click(function(e) {window.location.href=$(this).attr("href");});
    $('#tutorial-box').click(function(e) {window.location.href=$(this).attr("href");});
    $('#game-box').click(function(e) {window.location.href=$(this).attr("href");});
    $('#stats-box').click(function(e) {window.location.href=$(this).attr("href");});
    $('#cash-box').click(function(e) {window.location.href=$(this).attr("href");});
    $('#feedback-box').click(function(e) {window.location.href=$(this).attr("href");});

    $('#information-text').text('Information [✔]');
    $('#consent-text').text('Consent [✔]');
    if (doneSurveyBool) {
        $('#survey-text').text('Survey [✔]');
    }
    if (doneTutorialBool) {
        $('#tutorial-box').hide();
        $('#game-box').show();
    }
    else {
        $('#tutorial-box').show();
        $('#game-box').hide();
        $('#stats-box').addClass('inactive');
        $('#stats-box').off('click');
        $('#stats-box').click(function(e) {alert("To view game statistics, finish the tutorial and play games");});
    }
    if (doneRequiredBool) {
        $('#games-text').text('Games [✔]');
        $('#games-box').addClass('inactive');
        $('#games-box').off('click');
    }
    else if (doneTutorialBool) {
        $('#required-text').text("Required Games ["+status.nGames+"/"+status.required+"]");
    }
    if (doneCashBool) {
        $('#cash-text').text('HIT Code / Cash Out [✔]');
    }
    else {
        if (doneSurveyBool & doneTutorialBool & doneRequiredBool) {
            $('#cash-text').text('HIT Code / Cash Out');
        }
        else {
            $('#cash-box').addClass('inactive');
            $('#cash-box').off('click');
            $('#cash-box').click(function(e) {alert("To cash out, first complete the survey and the "+status.required+" required games");});
        }
    }
});
