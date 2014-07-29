$(document).ready(function() {
    //Some aliases for our functions
    var createPOSTFunction = ecoberry.ajax.createPOSTFunction;

    /*
      We'll have each POST identify itself so the server can easily tell what to code to run.
      I think a convention for this could be something like:
      id_function
      Example:
      id_users_change  
    */

    /* tell the backend we are changing the graph that we are displaying and then display the new graph */
    $("#id_period").change(
	createPOSTFunction("/powermonitorweb/graphs/", "#id_period", "period_select",
			   function(response){
			   console.log(response);
					var json = $.parseJSON(response);
					$("#graphdiv").html(json.graph);
				}));
});