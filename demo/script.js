const headers = {
    "Authorization": "w35U4gMEzUl9TBox9kQcOQStIdAb4emdK1SoIY8K",
    "Accept": "application/taxii+json;version=2.1",
    "Content-Type": "application/taxii+json;version=2.1"
};

function send_request(customUrl) {
    const url = customUrl || $("#requestUrl").val();

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

$("#sendRequest").click(send_request);

$("#btnDiscovery").click(function () {
    send_request("http://127.0.0.1:8000/taxii2/");
    $("#requestUrl").val("http://127.0.0.1:8000/taxii2/");
});

$("#btnRoot").click(function () {
    send_request("http://127.0.0.1:8000/taxii2/api1/");
    $("#requestUrl").val("http://127.0.0.1:8000/taxii2/api1/");
});

$("#btnListCol").click(function () {
    send_request("http://127.0.0.1:8000/taxii2/api1/collections/");
    $("#requestUrl").val("http://127.0.0.1:8000/taxii2/api1/collections/");
});

$("#btnGetCol").click(function () {
    send_request("http://127.0.0.1:8000/taxii2/api1/collections/1883fdfb-249b-58f5-b445-87dff6eabc06");
    $("#requestUrl").val("http://127.0.0.1:8000/taxii2/api1/collections/1883fdfb-249b-58f5-b445-87dff6eabc06");
});

$("#btnListObj").click(function () {
    send_request("http://127.0.0.1:8000/taxii2/api1/collections/d6ed313e-533a-55a6-aa06-4c00bc132812/objects/");
    $("#requestUrl").val("http://127.0.0.1:8000/taxii2/api1/collections/d6ed313e-533a-55a6-aa06-4c00bc132812/objects/");
});

$("#btnGetObj").click(function () {
    send_request("http://127.0.0.1:8000/taxii2/api1/collections/d6ed313e-533a-55a6-aa06-4c00bc132812/objects/identity--7f4e0b2a-1f7b-41f4-9e76-a18fa1ce86e8");
    $("#requestUrl").val("http://127.0.0.1:8000/taxii2/api1/collections/d6ed313e-533a-55a6-aa06-4c00bc132812/objects/identity--7f4e0b2a-1f7b-41f4-9e76-a18fa1ce86e8");
});

$("#btnManifests").click(function () {
    send_request("http://127.0.0.1:8000/taxii2/api1/collections/d6ed313e-533a-55a6-aa06-4c00bc132812/manifests");
    $("#requestUrl").val("http://127.0.0.1:8000/taxii2/api1/collections/d6ed313e-533a-55a6-aa06-4c00bc132812/manifests");
});

$("#btnVersions").click(function () {
    send_request("http://127.0.0.1:8000/taxii2/api1/collections/d6ed313e-533a-55a6-aa06-4c00bc132812/objects/grouping--28f673f6-074f-484a-9a22-e89b786a5671/versions");
    $("#requestUrl").val("http://127.0.0.1:8000/taxii2/api1/collections/d6ed313e-533a-55a6-aa06-4c00bc132812/objects/grouping--28f673f6-074f-484a-9a22-e89b786a5671/versions");
});
