$(document).ready(function(){
    $('select#id_occurrence_type').change(function(event)
    {
        if ($(this).val()==0)
        //TODO: this can be done better but I lack the resources
            $('input[type=checkbox]').parent().hide();
        else
            $('input[type=checkbox]').parent().show();
    }).change();
});