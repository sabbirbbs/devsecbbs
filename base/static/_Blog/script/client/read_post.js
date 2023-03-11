console.log("Hello from blog script")

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

//Manually update jdenticon after page load
function loadJicon() {
    // Select all elements with the class "jdenticon"
    const elements = document.querySelectorAll('.jdenticon');
  
    // Loop through the elements
    elements.forEach(function(element) {
      // Set the JDenticon for the element
      jdenticon.update(element);
    });
  };

//Create new element

function createReplyTo(comment_id,commenter_name){
    return `
    <div id="alert-border-1" class="flex p-4 mb-4 text-blue-800 border-t-4 border-blue-300 bg-blue-50 dark:text-blue-400 dark:bg-gray-800 dark:border-blue-800" role="alert">
        <svg aria-hidden="true" class="flex-shrink-0 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path></svg>
        <div class="ml-3 text-sm font-medium">
          You are replying to ${commenter_name}'s <a href="#${comment_id}" class="font-semibold underline hover:no-underline">comment</a>.
        </div>
        <button type="button" onclick="dismissReplier()" class="text-blue-800 ml-auto bg-transparent border border-blue-800 hover:bg-blue-900 hover:text-white focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-xs px-3 py-1.5 text-center dark:hover:bg-blue-600 dark:border-blue-600 dark:text-blue-400 dark:hover:text-white dark:focus:ring-blue-800" aria-label="Close">
          Cancel reply
        </button>
    </div>`
}

function createAlert(type,message){
    if(type === "success"){
        bg = "bg-green-100"
    }
    else{
        bg = "bg-blue-100"
    }
    return `<div class="${bg} rounded-lg py-5 px-6 mb-4 text-base text-blue-700 mb-3" role="alert">
    ${message}
    </div>`
}

//Additional function

function dismissReplier(){
    reply_to = $("#reply-to")
    comment_form = $("#comment-form")
    comment_form.attr('action',comment_form.data('default-action'))
    reply_to.html('')

};


//Document on ready
$(document).ready(function(){
    //Load jdenticon
    loadJicon()

    $(".reply-comment").on('click',function(e){
        //Remove border bottom from all article first
        article = $('#comment-section').find('article')
        article.each(function(){
            $(this).css({
                'border-bottom':''
            })
        })
        //getting all the required value & element
        commenter_name = $(this).closest('article').data('commenter-name');
        comment_url = $(this).closest('article').data('comment-url')
        comment_id = $(this).closest('article').attr('id')
        reply_to = $("#reply-to")
        comment_form = $("#comment-form")
        comment_form.attr('action',comment_url)
        reply_to.html(createReplyTo(comment_id,commenter_name))
        
        $(this).closest('article').css({
            'border-bottom':'5px solid green'
        })
        
        $('html, body').animate({ //Scroll to the comment box
            scrollTop: $("#reply-to").offset().top-200
        });
    })

})