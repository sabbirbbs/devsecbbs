//Functions
//Get cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

//Create alert dialog
function createAlert(type,message){
    if(type === "success"){
        $('#alert-success-msg').text(message)
        $('#alert-success').css('opacity',1)
        $('#alert-success').removeClass('hidden')
    }
    else{
        $('#alert-error-msg').text(message)
        $('#alert-error').css('opacity',1)
        $('#alert-error').removeClass('hidden')
    }
}

//On page load
$(document).ready(function(){
    
    //Post writing section handler
    //post category
    $('.post-category').select2()
    //post tags input
    $('.post-tags').select2({
        tags:true,
        tokenSeparators: [',']
    })

    //Submit post form
    $('#post_form').on('submit',function(e){
        e.preventDefault();
        //adding sun-editor context as textarea value
        $('#post_editor').val(editor.getContents())

        $.ajax({
            url: $("#post_form").attr("action"),
            method: "POST",
            data: new FormData(this),
            contentType: false,
            cache: false,
            processData:false,
            beforeSend : function(){
                $("#submit_post").text("Submitting...")

            },
            success: function(response){
                feadback = JSON.parse(response)
                f_status = feadback['status']
                f_message = feadback['message']
                createAlert(f_status,f_message)
                $("#submit_post").text("Submit")

                $('html, body').animate({ //Scroll to the feadback area
                    scrollTop: $("#feadback").offset().top-200
                });

                if(f_status === 'success'){
                    $("#alert-success-msg").text(f_message+" You will be redirect to edit page within 3 second.")
                    setTimeout(function() {
                        window.location = 'http://127.0.0.1/dashboard'
                    }, 3000);
                }
            },
            error: function(response){
                createAlert("error","Something went wrong!")
                $("#submit_post").text("Submit")
            }
        })
        console.log("submitting data by ajax")
    })
})