$(document).ready(function(){
    //Some aliases for our functions
    var createPOSTFunction = ecoberry.ajax.createPOSTFunction;
    var createFieldFiller = ecoberry.ajax.createFieldFiller;
    var messageAsAlert = ecoberry.ajax.messageAsAlert;
    
    /*Change the details in the fields to match the selected entry */
    $("#id_report_type").change(
	createPOSTFunction("/powermonitorweb/manage_reports/", "#id_report_type", "id_report_type_change",
			   createFieldFiller("occurrence_type", "datetime", "report_daily", "report_weekly", "report_monthly")));

    /* save changes to an enabled entry */
    $("#save_report").click(
	createPOSTFunction("/powermonitorweb/manage_reports/", "#manage_reports_form", "save_report_click",
			  function(response) { if (messageAsAlert(response))
					       {
						   var $reports = $("#id_report_type");
						   var $newlyenabled = $reports.find(":selected").detach().attr("data-enabled", "true");
						   $reports.insertBefore($newlyenabled, $reports);
					       }}));

    /* enable a disabled entry */
    $("#enable_report").click(
	createPOSTFunction("/powermonitorweb/manage_reports/", "#manage_reports_form", "enable_report_click",
			  messageAsAlert));

    /* disable an enabled entry */
    $("#disable_report").click(
	createPOSTFunction("/powermonitorweb/manage_reports/", "#id_report_type", "disable_report_click",
			   messageAsAlert));
    
    hideButtons();

    $('select#id_occurrence_type').change(function(event)
    {
        if ($(this).val()==0)
        //TODO: this can be done better but I lack the resources
            $('input[type=checkbox]').parent().hide();
        else
            $('input[type=checkbox]').parent().show();
    }).change();

    $("select#id_report_type").change(
    function () {
        var enabled = $("select#id_report_type option:selected").attr("data-enabled");
        hideButtons();
        if (enabled)
        {
            $("input#disable_report").show();
            $("input#save_report").show();
        }
        else
            $("input#enable_report").show();
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
