function getHeaders() {
    return {
        "Authorization": "w35U4gMEzUl9TBox9kQcOQStIdAb4emdK1SoIY8K",
        "Accept": "application/taxii+json;version=2.1",
        "Content-Type": "application/taxii+json;version=2.1"
    };
}
$("#headers").val(JSON.stringify(getHeaders(), null, 2));

function send_request(customUrl, method = "GET", data = null) {
    const url = customUrl || $("#requestUrl").val();

    let headers;
    try {
        headers = JSON.parse($("#headers").val());
    } catch (e) {
        $("#outputSpace").html("<pre>invalid headers</pre>");
        return;
    }

    $("#outputSpace").html("loading...");
    if (!url) {
        $("#outputSpace").html("<pre>url empty</pre>");
        return;
    }
    $.ajax({
        url: url,
        method: method,
        headers: headers,
        data: data ? JSON.stringify(data) : undefined,
        contentType: headers["Content-Type"],
        success: function (data) {
            $("#outputSpace").html("<pre>" + JSON.stringify(data, null, 2) + "</pre>");
        },
        error: function (xhr) {
            $("#outputSpace").html("<pre>error " + xhr.status + ":\n" + xhr.responseText + "</pre>");
        }
    });
}

$("#sendRequest").click(function () {
    send_request();
});

$("#btnDiscovery").click(function() {
    const url = "http://127.0.0.1:8000/taxii2/";
    $("#requestUrl").val(url);
    send_request(url);
});

$("#btnRoot").click(function() {
    const url = "http://127.0.0.1:8000/taxii2/api1/";
    $("#requestUrl").val(url);
    send_request(url);
});

$("#btnListCol").click(function() {
    const url = "http://127.0.0.1:8000/taxii2/api1/collections/";
    $("#requestUrl").val(url);
    send_request(url);
});

$("#btnGetCol").click(function() {
    const url = "http://127.0.0.1:8000/taxii2/api1/collections/28dfa8c5-dff4-52ad-90df-e5112b2ade90";
    $("#requestUrl").val(url);
    send_request(url);
});

$("#btnListObj").click(function() {
    const url = "http://127.0.0.1:8000/taxii2/api1/collections/28dfa8c5-dff4-52ad-90df-e5112b2ade90/objects/?limit=2";
    $("#requestUrl").val(url);
    send_request(url);
});

$("#btnGetObj").click(function() {
    const url = "http://127.0.0.1:8000/taxii2/api1/collections/28dfa8c5-dff4-52ad-90df-e5112b2ade90/objects/report--59e9ec59-a888-48e4-afb4-441602de0b81";
    $("#requestUrl").val(url);
    send_request(url);
});

$("#btnAddObj").click(function() {
    const url = "http://127.0.0.1:8000/taxii2/api1/collections/f37b15ee-07ba-583f-bf65-03e4fd5e9d96/objects/";
    $("#requestUrl").val(url);
    send_request(url);
});

$("#btnManifests").click(function() {
    const url = "http://127.0.0.1:8000/taxii2/api1/collections/28dfa8c5-dff4-52ad-90df-e5112b2ade90/manifests?limit=2";
    $("#requestUrl").val(url);
    send_request(url);
});

$("#btnVersions").click(function() {
    const url = "http://127.0.0.1:8000/taxii2/api1/collections/28dfa8c5-dff4-52ad-90df-e5112b2ade90/objects/report--59e9ec59-a888-48e4-afb4-441602de0b81/versions";
    $("#requestUrl").val(url);
    send_request(url);
});