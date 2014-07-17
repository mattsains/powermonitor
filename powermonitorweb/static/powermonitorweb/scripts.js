/* A javascript 'namespace' as explained at http://en.wikipedia.org/wiki/Unobtrusive_JavaScript#Namespaces */

var ecoberry;
if (!ecoberry) //main namespace
    ecoberry = {};
else if (typeof ecoberry != 'object'){
    throw new Error("ecoberry already exists and is not an object.");
}
if (!ecoberry.security) //for csrf related stuff
    ecoberry.security = {};
else if (typeof ecoberry.security != 'object'){
    throw new Error("ecoberry.security already exists and is not an object.");
}
if (!ecoberry.ajax)
    ecoberry.ajax = {};
else if (typeof ecoberry.ajax != 'object'){
    throw new Error("ecoberry.ajax already exists and is not an object.");
}

ecoberry.security.passCSRFtoken = function() {
    // Define private data and functions here

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
  
    /* More csrf stuff */
    function csrfSafeMethod(method) {
	// these HTTP methods do not require CSRF protection
	return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    // Return public pointers to functions or properties
    // that are to be public.
    return function()
    {
	var csrftoken = getCookie('csrftoken');
	$.ajaxSetup({
	    beforeSend: function(xhr, settings) {
		if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
		    xhr.setRequestHeader("X-CSRFToken", csrftoken);
		}
	    }
	});
    };}();

 /* Generates an ajax POST function */
ecoberry.ajax.createPOSTFunction = function (pageUrl, formID, successFunction)
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
        });
    };
};

/* Generates a function that fills in appropriate fields */
ecoberry.ajax.createFieldFiller = function(/* names, of, fields */)
{
    /* "arguments" gives a list of arguments passed into the function.
       I needed to refer to the outer function's arguments from within the inner function
       hence the creation of "args". Probably a better way to do this. */
    
    var args = arguments;
    return function(response)
    {
	var json = $.parseJSON(response);
	for (var i = 0; i < args.length; i++)
            $("#id_" + args[i]).val(json.fields[args[i]]);
    };
};

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
	
	/* START manage users in page menu */
	/* show and hide manage users/add user forms */
	$("#manage_users").click(function() {
		showAndHide("#manage_form", "#add_form");
		$("#manage_users").css('color', '#f00');
		$("#add_users").css('color', '#00f');
	});
	$("#add_users").click(function() {
		showAndHide("#add_form", "#manage_form");
		$("#add_users").css('color', '#f00');
		$("#manage_users").css('color', '#00f');
	});

	function showAndHide(idToShow, idToHide) {
		$(idToHide).css('display', 'none');
		$(idToShow).css('display', 'block');
	}
	/* END manage users in page menu */

    /*START ajax code for dynamic fields and posting without refreshing*/
    /*=================================================================*/
    ecoberry.security.passCSRFtoken();

    //Some aliases for our functions
    var createPOSTFunction = ecoberry.ajax.createPOSTFunction;
    var createFieldFiller = ecoberry.ajax.createFieldFiller;

	/* Where the magic happens - Now known as the Mnet method */
	$("#id_users").change(
	    createPOSTFunction("/powermonitorweb/manage_users/","#id_users",
	        createFieldFiller("username","first_name", "last_name", "email")));

	/* Update the user, then update the list with the new username */
	$("#update_user").click(createPOSTFunction("/powermonitorweb/manage_users/", "#manage_users_form",
	    function(response){
		    var json = $.parseJSON(response);
			$('#id_users [value="'+json.pk+ '"]').text(json.fields.username);}));
			
	/* Send the user a password reset email */
    $("#reset_password").click(createPOSTFunction("/powermonitorweb/manage_users/", "#id_email",
        function(response) {
		    var json = $.parseJSON(response);
		    if(json.email_sent) {
				alert("Email sent");
			} else {
				alert("There was a problem sending the email.");}}));
				
	/* Delete the user, and update the list so their name doesn't show any more */
	/* Tried fitting this in with the createPOSTFunction but it was stubborn as hell...so here's a horrible big function */
	$("#delete_user").click(function() {
		var request = $.ajax({
			url: "/powermonitorweb/manage_users/",
                type: "POST",
                data: $("#id_users").serialize() + "&delete=True", // Add extra data to serialized form
                processData: false,
                dataType:"text",
                success: function(response){
							var json = $.parseJSON(response);
							if(json.deleted) {
								alert("User Deleted");
								$("#id_users option:selected").remove(); // Delete the user from the list
								$("#id_users").val($("#id_users option:first").val()).change(); //Select the first user
							} else { alert("There was a problem deleting the user"); }
						 }});});
	/*END of ajax code*/

	/*START Add a datetime picker to page*/
    $('#id_datetime').datetimepicker({
        formatTime:'H:i',
        formatDate:'d.m.Y'
    });
	/*END datetimepicker code*/
});
