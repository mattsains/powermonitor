$(document).ready(function() {
    var messageAsBootStrapAlert = ecoberry.ajax.messageAsBootStrapAlert;
    
    var $accounts = $("#id_account_type");

    $accounts.change(
    function () {
	var $selected = $("select#id_account_type option:selected");	
        var $display = $("#display"); 
        $display.find("h2").text("Selected Account: " + $selected.text());
	$display.show();
    });
    
    $("#delete_account").click(function() {
        var request = $.ajax({
            url: "/powermonitorweb/manage_social_media/",
            type: "POST",
            data: $("#id_account_type").serialize() + "&delete=True" + "&identifier=delete_account_click", // Add extra data to serialized form
            processData: false,
            dataType:"text",
            success: function(response){
                console.log(response);
                var json = $.parseJSON(response);
		
                if(json.deleted) {
                    messageAsBootStrapAlert('{"heading":"Account removed","success":true,"message":"The social media account was removed."}', $("#error-container"));
		    $("#id_account_type option:selected").remove(); // Delete the account from the list
                    $("#id_account_type").val($("#id_account_type option:first").val()).change(); //Select the first account
                } else {  messageAsBootStrapAlert('{"heading":"Acount Not Removed","success":false,"message":"An error prevented the account from being removed."}', $("#error-container")); }
            }
	});
    });
});
