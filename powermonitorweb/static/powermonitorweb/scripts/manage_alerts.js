$(document).ready(function() {
    var createPOSTFunction = ecoberry.ajax.createPOSTFunction;
    var createFieldFiller = ecoberry.ajax.createFieldFiller;
    var messageAsAlert = ecoberry.ajax.messageAsAlert;

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
			  function(response) { if (messageAsAlert(response))
					       {
						   var $newlyenabled = $reports.find(":selected").detach();
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
			   function(response) {if (messageAsAlert(response))
			      {
				  var $newlydisabled = $reports.find(":selected").detach();
				  $newlydisabled.removeAttr("data-enabled");
				  if ($("#id_alert_type option[data-enabled=true]").length)
				      $newlydisabled.insertAfter($("#id_alert_type option[data-enabled=true]").last());
				  else
				      $newlydisabled.insertBefore($("#id_alert_type option").first());						   
				  $alerts.change();
			      }}));

       $alerts.change(
	createPOSTFunction("/powermonitorweb/manage_reports/", "#id_report_type", "id_report_type_change",
			   createFieldFiller("alert_description")));

}
);
