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
        state.loaded = true;
        check_state_machine();
    });
}
