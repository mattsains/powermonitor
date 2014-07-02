$(document).ready(function() {
	/*	Functions for add and removing items from a select listbox	*/
	$("#add_to_chosen").click(function() {
        if ( $("#chosen_list option[value='"+$("#option_list option:selected").val()+"'").length == 0 ){
            $('#chosen_list')[0].options.add(new Option($("#option_list option:selected").text(), $("#option_list option:selected").val()));
        } else {
            alert("Report already chosen!");
        }
	});
	$("#remove_from_chosen").click(function() {
		$('#chosen_list')[0].options.remove($("#chosen_list option:selected"));
	});
	/* END listbox functions */
	
	/* Function for enabling and disabling options in manage reports screen */
	$("input[name=occurrence_type]:radio").change(function() {
		if ($('input[name="occurrence_type"]:radio').val() == "onceoff") {
			$("#report_time").prop("disabled", false);
			$('input[type="checkbox"]').prop("disabled", true);
		} else if ($('input[name="occurrence_type"]:radio').val() == "recurring") {
			$("#report_time").prop("disabled", true);
			$('input[type="checkbox"]').prop("disabled", false);
		}
	});
	/* END manage reports functions */

    /*Hide the user's menu*/
	$("#usermenu").css("display", "none");

	/*Set up the function to display and hide the menu*/
	$("#username").click(function() {
	    var menu = $("#usermenu");

	    if(menu.css("display") === "none")
	 	    menu.css("display", "block");
	 	else
	 	    menu.css("display", "none");
	 });

	 /* hide the menu if they click on the page?*/
	 $(document).click(function (e) {
	     var menu = $("#usermenu");
	     var clicked = e.target.id;
	     if(menu.css("display") === "block" && (clicked != "username" && clicked != "downarrow"))
	 	     menu.css("display", "none");});

});