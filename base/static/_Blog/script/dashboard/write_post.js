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
    $("#alert-success").addClass('hidden')
    $("#alert-error").addClass('hidden')
    if(type === "success"){
        $('#alert-success-msg').html(message)
        $('#alert-success').css('opacity',1)
        $('#alert-success').removeClass('hidden')
    }
    else{
        $('#alert-error-msg').html(message)
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
        $('#post_editor').val(DOMPurify.sanitize(editor.getContents()))

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
                    scrollTop: $("#post_notice").offset().top-200
                });

                if(feadback.hasOwnProperty('destination')){
                    $("#alert-success-msg").text(f_message+" You will be redirect to edit page within 3 second.")
                    setTimeout(function() {
                        window.location = feadback['destination']
                    }, 3000);
                }
            },
            error: function(response){
                createAlert("error","Something went wrong! Please contact administrator.")
                $("#submit_post").text("Submit")

                $('html, body').animate({ //Scroll to the feadback area
                    scrollTop: $("#post_notice").offset().top-200
                });
            }
        })
    })
})