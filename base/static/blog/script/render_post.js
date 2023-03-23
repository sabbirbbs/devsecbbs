
//Functions
//Get csrf token
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



//Highlight code syntax by prismjs
function highlight_code(){
    $('code').each(function(){
        var data = $(this).html()
        data = data.replace(/<br>/g,'\n')
        $(this).html(data)
    })
    Prism.highlightAll()
}


$(document).ready(function(){
    //Render blog post
    post = $("#post")
    $.ajax({
        url : post.attr("data-post"),
        method : "POST",
        data : {"csrfmiddlewaretoken":getCookie("csrftoken")},
        success : function(response){
            xss_check = DOMPurify.sanitize(response)
            post.html(xss_check)
            $("#post-page").show()
            $("#load").hide()
            //Manually update pre code prismjs
            highlight_code()
        },
        error : function(response){
            post.html(createAlert("error"," Something went wrong.No post found!"))
            $("#load").hide()
            $("#post-page").show()
        }
    })

    //Handling comment section
    $("#comment_form").on("submit",function(e){
        e.preventDefault();
        
        $.ajax({
            url: $("#comment_form").attr("action"),
            method: "POST",
            data: new FormData(this),
            contentType: false,
            cache: false,
            processData:false,
            beforeSend : function(){
                $("#submit_comment").text("Submitting...")

            },
            success: function(response){
                feadback = JSON.parse(response)
                notice_type = feadback['status']
                message = feadback['message']
                $("#alert").html(createAlert(notice_type,message))
                $("#submit_comment").text("Submit")
            },
            error: function(response){
                $('#alert').html(createAlert("error","Something went wrong!"))
                $("#submit_post").text("Submit")
            }
        })
    })
    //Handling reply action
    $(".reply_btn").on("click", function(){
        $("article").each(function(){
            $(this).addClass("bg-white")
        })
        $(this).closest("article").removeClass("bg-white");
        $(this).closest("article").css("background-color","ghostwhite");
        $(this).closest('.reply_form').css("display","block")
    });
    
})