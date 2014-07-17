$(document).ready(function(){
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
