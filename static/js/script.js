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

var doc = new jsPDF();
var specialElementHandlers = {
    '#editor': function (element, renderer) {
        return true;
    }
};

$('#cmd').click(function () {
    doc.fromHTML($('#content').html(), 15, 15, {
        'width': 800,
            'elementHandlers': specialElementHandlers
    },
    function(bla) {
        const today = new Date();
        name = today.toLocaleString(); // 5/12/2020, 6:50:21 PM
        doc.save(name+'.pdf');
    });
    // setTimeout(function () {
    //     doc.save(name+'.pdf');
    // }, 5);

    // doc.save(name+'.pdf');
    // var element = document.getElementById('content');
    // element.style.width = '800px';
    // element.style.height = '1000px';
    // var opt = {
    //     margin: 0.5,
    //     filename: 'sample.pdf',
    //     image: {type: 'jpeg', quality: 1},
    //     html2canvas: {scale: 1},
    //     jspdf: {unit: 'in', format: 'letter', orientation: 'portrait', precision: '12'}
    // };
    // html2pdf().set(opt).from(element).save();
});