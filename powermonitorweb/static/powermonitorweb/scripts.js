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

    /*Start top-right user menu code*/
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

	 /* hide the menu if they click on the page*/
	 $(document).click(function (e) {
	     var menu = $("#usermenu");
	     var clicked = e.target.id;
	     if(menu.css("display") === "block" && (clicked != "username" && clicked != "downarrow"))
	 	     menu.css("display", "none");});
	 /*END user menu code*/

	/*Start dropdown submenu code*/
	$("#bar > li").bind("mouseover", openSubMenu);
	function openSubMenu() {
		$(this).find('ul').css('visibility', 'visible');
	}
	$("#bar > li").bind("mouseout", closeSubMenu);
	function closeSubMenu() {
		$(this).find('ul').css('visibility', 'hidden');
	}
	/*END dropdown submenu code*/

    /*START ajax code for dynamic fields and posting without refreshing*/
    /*=================================================================*/
	/* check if a user was selected from the list and do some ajax magic stuff */
	/* first do some fancy stuff to ensure the csrf token is passed to the server so it knows the data is secure */

	function getCookie(name) {
		var cookieValue = null;
		if (document.cookie && document.cookie != '') {
			var cookies = document.cookie.split(';');
			for (var i = 0; i < cookies.length; i++) {
				var cookie = jQuery.trim(cookies[i]);
				// Does this cookie string begin with the name we want?
				if (cookie.substring(0, name.length + 1) == (name + '=')) {
					cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
					break;
				}
			}
		}
		return cookieValue;
	}
	var csrftoken = getCookie('csrftoken');
	/* More csrf stuff */
	function csrfSafeMethod(method) {
		// these HTTP methods do not require CSRF protection
		return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
	}
	$.ajaxSetup({
		beforeSend: function(xhr, settings) {
			if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
				xhr.setRequestHeader("X-CSRFToken", csrftoken);
			}
		}
	});

    /* Generates an ajax POST function */
	function ajaxPOSTFactory(pageUrl, formID, successFunction)
	{
        return function()
        {
            var request = $.ajax({
                url: pageUrl,
                type: "POST",
                data: $(formID).serialize(),
                processData: false,
                dataType:"text",
                success: successFunction
            })
        }
	}

    /* Generates a function that fills in appropriate fields */
	function changeFieldsFactory(/* names, of, fields */)
	{
	    var args = arguments;
	    return function(response)
	    {
	        var json = $.parseJSON(response);
	        for (var i = 0; i < args.length; i++)
                $("#id_" + args[i]).val(json.fields[args[i]]);
	    }
	}

	/* Where the magic happens - Now known as the Mnet method */
	$("#id_users").change(
	    ajaxPOSTFactory("/powermonitorweb/manage_users/","#id_users",
	        changeFieldsFactory("username","first_name", "last_name", "email")));

	/* Update the user, then update the list with the new username */
	$("#update_user").click(ajaxPOSTFactory("/powermonitorweb/manage_users/", "#manage_users_form",
	    function(response){
		    var json = $.parseJSON(response);
			$('#id_users [value="'+json.pk+ '"]').text(json.fields.username);}));

	/* Send the user a password reset email */
    $("#reset_password").click(ajaxPOSTFactory("/powermonitorweb/manage_users/", "#id_email",
        function(response) {
		    var json = $.parseJSON(response);
		    if(json.email_sent) {
				alert("Email sent");
			} else {
				alert("There was a problem sending the email.");}}));
	/*END of ajax code*/

	/*START Add a datetime picker to page*/
    $('#id_datetime').datetimepicker({
        formatTime:'H:i',
        formatDate:'d.m.Y',
    });
	/*END datetimepicker code*/
});