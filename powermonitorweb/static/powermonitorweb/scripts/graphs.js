google.load("visualization", "1", {packages:["corechart"]});
google.setOnLoadCallback(drawChart);

function drawChart() {
    var options = {
        title: "Electricity Usage",
        lines: {
            show: true
        },
        points: {
            show: true
        },
        legend: {
            position: 'none'
        },
        vAxis: {
            title: "Watts",
            format: "# W",
            viewWindowMode: 'explicit',
            viewWindow:{
                min: 0
            }
        }
    };
    
    var chart;
    
    var get_data=function(url, form_data){
        var identifiedData = form_data + (form_data.length == 0 ? "" : "&") + "identifier=" + "whatever";
        
        var request = $.ajax({
            url: url,
            type: "POST",
            data: identifiedData,
            processData: false,
            dataType:"json",
            success: function(response_data)
            {
                for (var i=0; i<response_data.graph.length;i++)
                    response_data.graph[i][0]=new Date(response_data.graph[i][0]);
                data=response_data.graph;
                
                var dataView=new google.visualization.DataTable();
                dataView.addColumn('datetime', 'Date');
                dataView.addColumn('number', 'Reading');
                dataView.addRows(data);
                if (chart==null)
                    chart = new google.visualization.AreaChart(document.getElementById('chart_div'));
                
                chart.draw(dataView, options);
                
                //TODO: update stats
            }
        });
    };
    
    var data;
    var $id_period=$("#id_period");    
    
    $id_period.change(function(){ get_data("/powermonitorweb/graphs/", "period="+$id_period.val());}).change();
    
    var do_populate=function(){ 
        get_data("/powermonitorweb/graphs/", "period="+$id_period.val()); 
        setTimeout(do_populate, 5000);
    };
    
    do_populate();
}