
//Functions
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
        url : post.attr("data-post_api"),
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
    
})