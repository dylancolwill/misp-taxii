const headers = {
    "Authorization": "w35U4gMEzUl9TBox9kQcOQStIdAb4emdK1SoIY8K",
    "Accept": "application/taxii+json;version=2.1",
    "Content-Type": "application/taxii+json;version=2.1"
};

function send_request(customUrl) {
    const url = customUrl || $("#requestUrl").val();

     $("#outputSpace").html("loading...");
    if (!url) {
        $("#outputSpace").html("<pre>url empty</pre>");
        return;
    }
    $.ajax({
        url: url,
        method: "GET",
        headers: headers,
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
    const url = "http://127.0.0.1:8000/taxii2/api1/collections/d6ed313e-533a-55a6-aa06-4c00bc132812/objects/identity--7f4e0b2a-1f7b-41f4-9e76-a18fa1ce86e8";
    $("#requestUrl").val(url);
    send_request(url);
});

$("#btnManifests").click(function() {
    const url = "http://127.0.0.1:8000/taxii2/api1/collections/d6ed313e-533a-55a6-aa06-4c00bc132812/manifests?limit=2";
    $("#requestUrl").val(url);
    send_request(url);
});

$("#btnVersions").click(function() {
    const url = "http://127.0.0.1:8000/taxii2/api1/collections/d6ed313e-533a-55a6-aa06-4c00bc132812/objects/grouping--28f673f6-074f-484a-9a22-e89b786a5671/versions";
    $("#requestUrl").val(url);
    send_request(url);
});