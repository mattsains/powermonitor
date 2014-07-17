$(document).ready(function(){
    //Some aliases for our functions
    var createPOSTFunction = ecoberry.ajax.createPOSTFunction;
    var createFieldFiller = ecoberry.ajax.createFieldFiller;

    /*Change the details in the fields to match the selected entry */
    $("#id_report_type").change(
	createPOSTFunction("/powermonitorweb/manage_reports/", "#id_report_type",
			   createFieldFiller("occurrence_type", "datetime", "report_daily", "report_weekly", "report_monthly")));

    /* save changes to an enabled entry */
    $("#save").click(
	createPOSTFunction("/powermonitorweb/manage_reports/", "#manage_reports_form",
			  function(){alert("TEST!");}));

    /* enable a disabled entry */
    $("#enable").click(
	createPOSTFunction("/powermonistorweb/manage_reports/", "#id_report_type",
			  function(){alert("TEST2!");}));

    /* disable an enabled entry */
    $("#disable").click(
	createPOSTFunction("/powermonistorweb/manage_reports/", "#id_report_type",
			   function(){alert("TEST3!");}));
    
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
            $("input#disable").show();
            $("input#save").show();
        }
        else
            $("input#enable").show();
    });

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
