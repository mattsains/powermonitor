$(document).ready(function() {
    var createPOSTFunction = ecoberry.ajax.createPOSTFunction;
    var createFieldFiller = ecoberry.ajax.createFieldFiller;
    var messageAsAlert = ecoberry.ajax.messageAsAlert;
    var messageAsBootStrapAlert = ecoberry.ajax.messageAsBootStrapAlert;
    
    var $alerts = $("#id_alert_type");

    function hideButtons()
    {$("input[type=button]").hide();}

    hideButtons();

    $alerts.change(
    function () {
	var $selected = $("select#id_alert_type option:selected");	
        var enabled = $selected.attr("data-enabled");
	var $display = $("#display"); 
        hideButtons();
	$display.show();
	$display.find("h2").text("Selected Alert: " + $selected.text());
	
        if (enabled)
        {
	    $display.addClass("panel-success-success");
	    $display.removeClass("panel-primary");
            $("input#disable_alert").show();
        }
        else
	{
	    $display.removeClass("panel-success-success");
	    $display.addClass("panel-primary");
	    $("input#enable_alert").show();
	}
    });

     $("#enable_alert").click(
	createPOSTFunction("/powermonitorweb/manage_alerts/", "#manage_reports_form", "enable_alert_click",
			  function(response) { if (messageAsBootStrapAlert(response, $("#error-container")))
					       {
						   var $newlyenabled = $alerts.find(":selected").detach();
						   $newlyenabled.attr("data-enabled", "true");						
						   if ($("#id_alert_type option[data-enabled=true]").length)
						       $newlyenabled.insertAfter($("#id_alert_type option[data-enabled=true]").last());
						   else
						       $newlyenabled.insertBefore($("#id_alert_type option").first());						   
						   $alerts.change();
					       }}));


    /* disable an enabled entry */
    $("#disable_alert").click(
	createPOSTFunction("/powermonitorweb/manage_alerts/", "#id_alert_type", "disable_alert_click",
			   function(response) { if (messageAsBootStrapAlert(response, $("#error-container")))
			      {
				  var $newlydisabled = $alerts.find(":selected").detach();
				  $newlydisabled.removeAttr("data-enabled");
				  if ($("#id_alert_type option[data-enabled=true]").length)
				      $newlydisabled.insertAfter($("#id_alert_type option[data-enabled=true]").last());
				  else
				      $newlydisabled.insertBefore($("#id_alert_type option").first());						   
				  $alerts.change();
			      }}));

       $alerts.change(
	createPOSTFunction("/powermonitorweb/manage_alerts/", "#id_alert_type", "id_alert_type_change",
			   createFieldFiller("alert_description")));

}
);
