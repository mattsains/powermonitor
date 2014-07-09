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
	/* Where the magic happens - Now know as the Mnet method */
	$("#id_users").change(function () {
		var request = $.ajax({
			url: "/powermonitorweb/manage_users/",
			type: "POST",
			data: $("#id_users").serialize(),
			processData: false,
			dataType: 'text',
			success: function(response){
				var json = $.parseJSON(response);
				$("#id_username").val(json.fields.username);
				$("#id_first_name").val(json.fields.first_name);
				$("#id_last_name").val(json.fields.last_name);
				$("#id_email").val(json.fields.email);
			}
		});
	});
	/* Update the user, then update the list with the new username */
	$("#update_user").click(function() {
		var request = $.ajax({
			url: "/powermonitorweb/manage_users/",
			type: "POST",
			data: $("#manage_users_form").serialize(),
			processData: false,
			dataType: 'text',
			success: function(response){
				var json = $.parseJSON(response);
				$('#id_users [value="'+json.pk+'"]').text(json.fields.username);
			}
		});
	});
});