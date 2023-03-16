document.getElementById("file").onchange = function() {
    document.getElementById("form").submit();
    data()
    console.log("working!");
};

function data() {
    $.ajax({
        type: 'POST',
        url: '/temp',
        success: function(result) {
            document.getElementById('anomaly').innerHTML='<p>'+result.what_type+'</p><p>'+result.what+'</p><p>'+result.analysis+'</p><p>'+result.controlSay+'</p>';
            console.log(result);
        },
        error: function(err) {
            console.log(err);
        }
    });
}