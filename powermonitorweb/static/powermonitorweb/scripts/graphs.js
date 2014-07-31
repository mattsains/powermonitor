google.load("visualization", "1", {packages:["corechart"]});
google.setOnLoadCallback(drawChart);
function drawChart() {


   var get_dataset=function(url, form_data, success_func){
      var identifiedData = form_data + (form_data.length == 0 ? "" : "&") + "identifier=" + "whatever";
      var request = $.ajax({
         url: url,
         type: "POST",
         data: identifiedData,
         processData: false,
         dataType:"json",
         success: success_func
      });
   };
   var options = {
      lines: {
         show: true
      },
      points: {
         show: true
      },
      xaxis: {
         tickDecimals: 0,
         tickSize: 1
      }
   };
   var data;
   var $id_period=$("#id_period");
   $id_period.change(function(e){
      get_dataset("/powermonitorweb/graphs/", "period="+$id_period.val(),
         function(response_data){
            
            for (var i=0; i<response_data.length;i++)
                response_data[i][0]=new Date(response_data[i][0]);
            data=jQuery.merge([['Time','Reading']],response_data);
            var dataView=new google.visualization.DataView(google.visualization.arrayToDataTable(data));
            dataView.setColumns([{calc: function(data, row) { return data.getFormattedValue(row, 0); }, type:'string'}, 1]);
            var chart = new google.visualization.AreaChart(document.getElementById('chart_div'));
            
            var options = {
               title: 'Electricity usage'
            };
            chart.draw(dataView, options);
            setInterval(function(){
               
               get_dataset("/powermonitorweb/graphs/", "period="+$id_period.val(), function(response_data){
               for (var i=0; i<response_data.length;i++)
                response_data[i][0]=new Date(response_data[i][0]);
            data=jQuery.merge([['Time','Reading']],response_data);
               var dataView=new google.visualization.DataView(google.visualization.arrayToDataTable(data));
               dataView.setColumns([{calc: function(data, row) { return data.getFormattedValue(row, 0); }, type:'string'}, 1]);
                  chart.draw(dataView, options);
               });
            }, 2000);
         }
      );
      
   }).change();   
}