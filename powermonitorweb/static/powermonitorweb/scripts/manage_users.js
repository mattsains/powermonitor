$(document).ready(function() {
    //Some aliases for our functions
    var createPOSTFunction = ecoberry.ajax.createPOSTFunction;
    var createFieldFiller = ecoberry.ajax.createFieldFiller;
    var messageAsBootStrapAlert = ecoberry.ajax.messageAsBootStrapAlert;
    /*
      We'll have each POST identify itself so the server can easily tell what to code to run.
      I think a convention for this could be something like:
      id_function
      Example:
      id_users_change  
    */

    /* Where the magic happens - Now known as the Mnet method */
    $("#id_users").change(function(){
	$('#display').show();
	createPOSTFunction("/powermonitorweb/manage_users/","#id_users", "id_users_change",
			   createFieldFiller("username","first_name", "last_name", "email"))();});

    /* Update the user, then update the list with the new username */
    $("#update_user").click(
	createPOSTFunction("/powermonitorweb/manage_users/", "#manage_users_form", "update_user_click",
			   function(response){
			       var json = $.parseJSON(response);
			       messageAsBootStrapAlert('{"heading":"User Successfully Updated","success":true,"message":"User '+json.fields.username+' was successfully updated."}', $("#error-container"));
			       $('#id_users [value="'+json.pk+ '"]').text(json.fields.username);}));
    
    /* Send the user a password reset email */
    $("#reset_password").click(
	createPOSTFunction("/powermonitorweb/manage_users/", "#id_email", "reset_password_click",
			   function(response) {
			       var json = $.parseJSON(response);
			       if(json.email_sent) {
				   messageAsBootStrapAlert('{"heading":"Email Sent","success":true,"message":"Sent a password reset email to '+json.fields.username+'"}', $("#error-container"));
			       } else {
				   messageAsBootStrapAlert('{"heading":"Email Not Sent","success":false,"message":"There was a problem sending a password reset email to '+json.fields.username+'"}', $("#error-container"));
			       }}));
    
    /* Delete the user, and update the list so their name doesn't show any more */
    /* Tried fitting this in with the createPOSTFunction but it was stubborn as hell...so here's a horrible big function */
    $("#delete_user").click(function() {
	var request = $.ajax({
	    url: "/powermonitorweb/manage_users/",
            type: "POST",
            data: $("#id_users").serialize() + "&delete=True" + "&identifier=delete_user_click", // Add extra data to serialized form
            processData: false,
            dataType:"text",
            success: function(response){
			console.log(response);
		var json = $.parseJSON(response);
		
		if(json.deleted) {
		     messageAsBootStrapAlert('{"heading":"User Removed","success":true,"message":"The user was removed."}', $("#error-container"));
		    $("#id_users option:selected").remove(); // Delete the user from the list
		    $("#id_users").val($("#id_users option:first").val()).change(); //Select the first user
		} else {  messageAsBootStrapAlert('{"heading":"User Not Removed","success":false,"message":"An error prevented the user from being removed."}', $("#error-container")); }
	    }});});
    
    form_submit_modal=function(){
        $("form#add_users_form").submit(function(event){
            //load in the result using ajax
            $("div#add_form_body").load("/powermonitorweb/add_user/", $("form#add_users_form").serializeArray(), function(){
                added=$("div#add_form_body").find("input[type='hidden']#added");
                if (added && (added.val()=="true"))
                    location.reload();
                else
                    form_submit_modal();
            });
            event.preventDefault();
        });
    };
    // This event dynamically loads the add form and makes sure it is submitted via ajax
    $("#add_user").click(function() {
        $("div#add_form_body").load("/powermonitorweb/add_user/", function(){
            form_submit_modal();
        });
    });
});
