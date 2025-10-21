function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

function getHeaders() {
    return {
        // add your MISP auth key here
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

    let requestData = data;
    if (!requestData && $("#requestData").val().trim()) {
        try {
            requestData = JSON.parse($("#requestData").val());
        } catch (e) {
            $("#outputSpace").html("<pre>invalid request</pre>");
            return;
        }
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
        data: requestData ? JSON.stringify(requestData) : undefined,
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
    const method = $("#requestData").val().trim() ? "POST" : "GET";
    send_request(undefined, method);
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
    
    const identity_uuid = generateUUID();
    const grouping_uuid = generateUUID();
    const indicator_uuid = generateUUID();
    const bundle_uuid = generateUUID();

    const taxii_envelope = {
        "objects": [
            {
                "type": "identity",
                "spec_version": "2.1",
                "id": `identity--${identity_uuid}`,
                "created": "2025-10-10T00:00:00.000Z",
                "modified": "2025-10-10T00:00:00.000Z",
                "name": "MISP-Project",
                "identity_class": "organization"
            },
            {
                "type": "grouping",
                "spec_version": "2.1",
                "id": `grouping--${grouping_uuid}`,
                "created_by_ref": `identity--${identity_uuid}`,
                "created": "2025-10-10T00:00:00.000Z",
                "modified": "2025-10-10T00:00:00.000Z",
                "name": "MISP-STIX-Converter test event",
                "context": "suspicious-activity",
                "object_refs": [`indicator--${indicator_uuid}`],
                "labels": ["Threat-Report", 'misp:tool="MISP-STIX-Converter"']
            },
            {
                "type": "indicator",
                "spec_version": "2.1",
                "id": `indicator--${indicator_uuid}`,
                "created_by_ref": `identity--${identity_uuid}`,
                "created": "2025-10-10T00:00:00.000Z",
                "modified": "2025-10-10T00:00:00.000Z",
                "pattern": "[autonomous-system:number = '174']",
                "pattern_type": "stix",
                "pattern_version": "2.1",
                "valid_from": "2025-10-10T00:00:00Z",
                "kill_chain_phases": [
                    {"kill_chain_name": "misp-category", "phase_name": "Network activity"}
                ],
                "labels": [
                    'misp:type="AS"',
                    'misp:category="Network activity"',
                    'misp:to_ids="True"'
                ]
            }
        ]
    };

    $("#requestUrl").val(url);
    $("#requestData").val(JSON.stringify(taxii_envelope, null, 2));
    send_request(url, "POST", taxii_envelope);
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