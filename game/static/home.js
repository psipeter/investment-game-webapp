initialize("/game/api/status/", "GET", (status) => {
    "use strict";

    let doneConsentBool = (status.doneConsent !== null);
    let doneSurveyBool = (status.doneSurvey !== null);
    let doneTutorialBool = (status.doneTutorial !== null);
    let doneRequiredBool = (status.doneRequired !== null);
    let doneBonusBool = (status.doneBonus !== null);
    let doneCashBool = (status.doneCash !== null);

    $("#ID").text(status.username);

    // Redirect on click
    $('#information-box').click(function(e) {
        window.location.href=$(this).attr("href");
    });

    $('#consent-box').click(function(e) {
        window.location.href=$(this).attr("href");
    });

    $('#survey-box').click(function(e) {
        window.location.href=$(this).attr("href");
    });

    $('#tutorial-box').click(function(e) {
        window.location.href=$(this).attr("href");
    });

    $('#required-box').click(function(e) {
        window.location.href=$(this).attr("href");
    });

    $('#bonus-box').click(function(e) {
        window.location.href=$(this).attr("href");
    });

    $('#stats-box').click(function(e) {
        window.location.href=$(this).attr("href");
    });

    $('#cash-box').click(function(e) {
        window.location.href=$(this).attr("href");
    });

    $('#feedback-box').click(function(e) {
        window.location.href=$(this).attr("href");
    });

    $('#information-text').text('Information [✔]');
    $('#consent-text').text('Consent [✔]');
    if (doneSurveyBool) {
        $('#survey-text').text('Survey [✔]');
    }
    if (doneTutorialBool) {
        $('#tutorial-text').text('Tutorial [✔]');
    }
    if (doneRequiredBool) {
        $('#required-text').text('Required Games [✔]');
        $('#required-box').addClass('inactive');
        $('#required-box').off('click');
        $('#required-box').click(function(e) {
            alert("You have already played the required games - try playing some bonus games!");
        });
    }
    else {
        $('#stats-box').addClass('inactive');
        $('#stats-box').off('click');
        $('#stats-box').click(function(e) {
            alert("To view game statistics, first play more bonus games");
        });
        if (doneTutorialBool) {
            $('#required-text').text(
                "Required Games ["+status.nRequired+"/"+status.N_REQUIRED+"]");
            }
        else {
            $('#required-box').addClass('inactive');
            $('#required-box').off('click');
            $('#required-box').click(function(e) {
                alert("To play required games, first complete the tutorial");
            });
        }
    }
    if (doneBonusBool) {
        $('#bonus-text').text('Bonus Games [✔]');
        $('#bonus-box').addClass('inactive');
        $('#bonus-box').off('click');
        $('#bonus-box').click(function(e) {
            alert("You have played the maximum number of bonus games");
        });
    }
    else {
        if (doneRequiredBool) {
            $('#bonus-text').text(
                "Bonus Games ["+status.nBonus+"/"+status.N_BONUS+"]");
            if (status.nBonus==0) {
                $('#stats-box').addClass('inactive');
                $('#stats-box').off('click');
                $('#stats-box').click(function(e) {
                    alert("To view game statistics, first play at least one bonus game");
                });
            }
            if (doneCashBool) {
                $('#bonus-box').addClass('inactive');
                $('#bonus-box').off('click');
                $('#bonus-box').click(function(e) {
                    alert("You may not play games after cashing out");
                });
            }
        }
        else {
            $('#bonus-box').addClass('inactive');
            $('#bonus-box').off('click');
            $('#bonus-box').click(function(e) {
                alert("To play bonus games, first complete required games");
            });
        }
    }
    if (doneCashBool) {
        $('#cash-text').text('Cash Out [✔]');
    }
    else {
        if (doneSurveyBool & doneTutorialBool & doneRequiredBool) {
            $('#cash-text').text('Cash Out ($'+(Number(fixedReward)+Number(bonusReward))+")");
        }
        else {
            $('#cash-box').addClass('inactive');
            $('#cash-box').off('click');
            $('#cash-box').click(function(e) {
                alert("To cash out, first complete the survey and required games, then play bonus games to earn more rewards");
            });
        }
    }
});
