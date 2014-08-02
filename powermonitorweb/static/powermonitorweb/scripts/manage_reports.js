$(document).ready(function(){
    //Some aliases for our functions
    var createPOSTFunction = ecoberry.ajax.createPOSTFunction;
    var createFieldFiller = ecoberry.ajax.createFieldFiller;
    var messageAsAlert = ecoberry.ajax.messageAsAlert;
    
    /*Change the details in the fields to match the selected entry */
    var $reports = $("#id_report_type"); 
    
    $reports.change(
	createPOSTFunction("/powermonitorweb/manage_reports/", "#id_report_type", "id_report_type_change",
			   createFieldFiller("occurrence_type", "datetime", "report_daily", "report_weekly", "report_monthly")));

    /* save changes to an enabled entry */
    $("#enable_report").click(
	createPOSTFunction("/powermonitorweb/manage_reports/", "#manage_reports_form", "enable_report_click",
			  function(response) { if (messageAsAlert(response))
					       {
						   var $newlyenabled = $reports.find(":selected").detach();
						   $newlyenabled.attr("data-enabled", "true");						
						   if ($("#id_report_type option[data-enabled=true]").length)
						       $newlyenabled.insertAfter($("#id_report_type option[data-enabled=true]").last());
						   else
						       $newlyenabled.insertBefore($("#id_report_type option").first());						   
						   $reports.change();
					       }}));

    /* enable a disabled entry */
    $("#save_report").click(
	createPOSTFunction("/powermonitorweb/manage_reports/", "#manage_reports_form", "save_report_click",
			  messageAsAlert));

    /* disable an enabled entry */
    $("#disable_report").click(
	createPOSTFunction("/powermonitorweb/manage_reports/", "#id_report_type", "disable_report_click",
			   function(response) {if (messageAsAlert(response))
			      {
				  var $newlydisabled = $reports.find(":selected").detach();
				  $newlydisabled.removeAttr("data-enabled");
				  if ($("#id_report_type option[data-enabled=true]").length)
				      $newlydisabled.insertAfter($("#id_report_type option[data-enabled=true]").last());
				  else
				      $newlydisabled.insertBefore($("#id_report_type option").first());						   
				  $reports.change();
			      }}));
    
    hideButtons();

    $('select#id_occurrence_type').change(function(event)
    {
        if ($(this).val()==0)
        //TODO: this can be done better but I lack the resources
            $('input[type=checkbox]').parent().hide();
        else
            $('input[type=checkbox]').parent().show();
    }).change();

    $reports.change(
    function () {
	var $selected = $("select#id_report_type option:selected");	
        var enabled = $selected.attr("data-enabled");
	var $display = $("#display"); 
        hideButtons();
	$display.find("h2").text("Selected Report: " + $selected.text());
	
        if (enabled)
        {
	    $display.addClass("panel-success-success");
	    $display.removeClass("panel-primary");
            $("input#disable_report").show();
            $("input#save_report").show();
        }
        else
	{
	    $display.removeClass("panel-success-success");
	    $display.addClass("panel-primary");
	    $("input#enable_report").show();
	}
    }).change();

    function hideButtons()
    {
       $("input[type=button]").hide();
    }

    /*Add a datetime picker to page*/
    $('#id_datetime').datetimepicker({
        formatTime:'H:i',
        formatDate:'d.m.Y'
    });
});
