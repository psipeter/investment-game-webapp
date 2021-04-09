function initialize(url, method, cback) {
    "use strict";

    // The page needs to be loaded AND we must have received data from the API
    // call before we can call the callback
    let state = {
        "loaded": false,
        "data": null,
    };
    function check_state_machine() {
        if (state.loaded && state.data) {
            if (state.data.avatar==1){$("#imgI").attr('src', '/static/user1C.svg');}
            if (state.data.avatar==2){$("#imgI").attr('src', '/static/user2C.svg');}
            if (state.data.avatar==3){$("#imgI").attr('src', '/static/user3C.svg');}
            if (state.data.avatar==4){$("#imgI").attr('src', '/static/user4C.svg');}

            $("#headerU").text(state.data.username);
            $("#headerG").text("Games: "+state.data.nGames +"/" + state.data.required);
            $("#headerW").text("Winnings: $"+state.data.winnings);
            if (state.data.doneGames === null) {
                $('#cash-link').css('color', 'var(--myGray');
                $('#cash-link').css('cursor', 'not-allowed');
                $("#cash-link").removeAttr('href');
            }
            cback(state.data);
        }
    }

    // Perform the API call, extract the middleware token if we perform a POST
    // request
    let ajax_params = {
        "type": method,
        "url": url,
        "success": function (data) {
            state.data = data;
            check_state_machine();
        },
    };
    if (method == 'POST') {
        ajax_params["data"] = {
            "csrfmiddlewaretoken": 
                document.getElementsByName("csrfmiddlewaretoken")[0].value,
        };
    }
    $.ajax(ajax_params);

    // Wait for the document to be ready
    $(function() {
        // Populate header
        state.loaded = true;
        check_state_machine();
    });
}