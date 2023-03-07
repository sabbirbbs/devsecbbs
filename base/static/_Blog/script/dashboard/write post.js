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
                status = feadback['status']
                message = feadback['message']
                $("#alert").html(createAlert(status,message))
                $("#submit_post").text("Submit")
            },
            error: function(response){
                $('#alert').html(createAlert("error","Something went wrong!"))
                $("#submit_post").text("Submit")
            }
        })
        console.log("submitting data by ajax")
    })
})