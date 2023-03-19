document.getElementById("file").onchange = function() {
    document.getElementById("form").submit();
    document.getElementById('first').innerHTML='';
    document.getElementById('loading').innerHTML='<img id="load_gif" src="static/processing.gif" width="20%">';
    document.getElementById('loading').style.margin='80px auto';
    setTimeout(() => {
        document.getElementById('charts').innerHTML='<div class="what">charts</div><img src="/static/temp.png" class="chart-image" id="chart-image" alt="my plot">';
        document.getElementById('chart-image').style.display='flex';
        data()
    }, 3000);
    // console.log("working!");
};

function data() {
    $.ajax({
        type: 'POST',
        url: '/temp',
        success: function(result) {
            document.getElementById('loading').style.display='none';
            document.getElementById('general_analysis').innerHTML='<div class="what">general analysis</div><div class="inside-anomaly" id="anomaly"></div>';
            document.getElementById('anomaly').innerHTML='<p>'+result.what_type+'</p><p>'+result.what+'</p><p>'+result.analysis1+'</p><p>'+result.analysis2+'</p><p>'+result.controlSay+'</p>';
            document.getElementById('trend_analysis').innerHTML='<div class="what">trend analysis</div><div class="inside-trend" id="trend"></div>';
            if (result.trend=='cyclic') {
                document.getElementById('trend').innerHTML='<p>'+result.trend+'</p><p>Cyclic pattern occasionally appears on the control charts. Such a pattern on the X chart may result from systematic environmental changes such as temperature, operator fatigue, regular rotation of operators and/or machine, or fluctuation in voltage or pressure or some other variable in the production equipment. R chart will sometimes reveal cycles because of maintenance schedule, operator fatigue, tool wear resulting in excessive variability.</p>';
            }
            if (result.trend=='increasing_trend' || result.trend=='decreasing_trend') {
                document.getElementById('trend').innerHTML='<p>'+result.trend+'</p><p>Trends are usually due to a gradual wearing out or deterioration of a tool or some other critical process components. They may also be caused by worker fatigue, accumulation of waste products, and deterioration of environmental conditions.</p>';
            }
            if (result.trend=='upward_shift' || result.trend=='downward_shift') {
                document.getElementById('trend').innerHTML='<p>'+result.trend+'</p><p>These shifts may result from the introduction of new workers, methods, raw materials, or machine, a change in the inspection method or standards, or change in either the skill, attentiveness, or motivation of the operators. Sometimes an improvement in the process performance is noted following introduction of a control chart program, simply because of motivational factors influencing the workers.</p>';
            }
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
    doc.fromHTML($('#content').html(), 10, 15, {
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