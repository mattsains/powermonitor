$(document).ready(function(){
    //Some aliases for our functions
    var createPOSTFunction = ecoberry.ajax.createPOSTFunction;
    var createFieldFiller = ecoberry.ajax.createFieldFiller;

    /* Where the magic happens - Now known as the Mnet method */
    $("#id_users").change(
	createPOSTFunction("/powermonitorweb/manage_users/","#id_users",
			   createFieldFiller("username","first_name", "last_name", "email")));

    /* Update the user, then update the list with the new username */
    $("#update_user").click(
	createPOSTFunction("/powermonitorweb/manage_users/", "#manage_users_form",
			   function(response){
			       var json = $.parseJSON(response);
			       $('#id_users [value="'+json.pk+ '"]').text(json.fields.username);}));
    
    /* Send the user a password reset email */
    $("#reset_password").click(
	createPOSTFunction("/powermonitorweb/manage_users/", "#id_email",
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
};
