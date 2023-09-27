////Additional function
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

//Highlight code syntax by prismjs
function highlight_code(){
    $('pre').addClass('bg-white dark:bg-gray-800');
    $('code').each(function(){
        var data = $(this).html()
        data = data.replace(/<br>/g,'\n')
        $(this).html(data)
    })
    Prism.highlightAll()
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
//Create replie info alert
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

//Create edit comment info alert
function editcomment(comment_id,commenter_name){
    return `
    <div id="alert-border-1" class="flex p-4 mb-4 text-blue-800 border-t-4 border-blue-300 bg-blue-50 dark:text-blue-400 dark:bg-gray-800 dark:border-blue-800" role="alert">
        <svg aria-hidden="true" class="flex-shrink-0 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path></svg>
        <div class="ml-3 text-sm font-medium">
          Hey, ${commenter_name}, you are gonna edit your <a href="#${comment_id}" class="font-semibold underline hover:no-underline">comment</a>.
        </div>
        <button type="button" onclick="dismissEditor()" class="text-blue-800 ml-auto bg-transparent border border-blue-800 hover:bg-blue-900 hover:text-white focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-xs px-3 py-1.5 text-center dark:hover:bg-blue-600 dark:border-blue-600 dark:text-blue-400 dark:hover:text-white dark:focus:ring-blue-800" aria-label="Close">
          Cancel edit
        </button>
    </div>`
}


//Add & remove hidden input inside from : written by chatgpt
function addHiddenInputToForm(formId, inputName, inputValue) {
    $('#' + formId).append('<input type="hidden" name="' + inputName + '" value="' + inputValue + '">');
  }

function removeHiddenInputFromForm(formId, inputName) {
    $('#' + formId + ' input[name="' + inputName + '"]').remove();
}
  
//Dismiss comment replier
function dismissReplier(){
    reply_to = $("#reply-to")
    comment_form = $("#comment-form")
    comment_form.attr('action',comment_form.data('default-action'))
    removeBorderBottom()
    reply_to.html('')
};

//Dismiss comment editor
function dismissEditor(){
    reply_to = $("#reply-to")
    comment_form = $("#comment-form")
    $('#comment').val('')
    comment_form.attr('action',comment_form.data('default-action'))
    removeBorderBottom()
    removeHiddenInputFromForm('comment-form','comment_edit')
    reply_to.html('')
};


//Remove border bottom from all article comments
function removeBorderBottom(){
    article = $('#comment-section').find('article')
    article.each(function(){
        $(this).css({
            'border-bottom':''
        })
    })
}



//Document on ready
$(document).ready(function(){
    //Load jdenticon
    loadJicon()
    highlight_code()

    //Render blog post
    post = $("#post")
    $.ajax({
        url : post.attr("data-post"),
        method : "POST",
        data : {"csrfmiddlewaretoken":getCookie("csrftoken")},
        success : function(response){
            xss_check = DOMPurify.sanitize(response)
            post.html(xss_check)
            post.css('opacity',1)
            $("#post-loader").hide()
            //Manually update pre code prismjs
            highlight_code()
        },
        error : function(response){
            post.html("Something went wrong.No post found!")
            $("#post-loader").hide()
            post.css('opacity',1)
        }
    })

    //Handling replie action
    $(".reply-comment").on('click',function(e){

        //getting all the required value & element
        commenter_name = $(this).closest('article').data('commenter-name');
        comment_url = $(this).closest('article').data('comment-url')
        comment_id = $(this).closest('article').attr('id')
        reply_to = $("#reply-to")
        comment_form = $("#comment-form")
        comment_form.attr('action',comment_url)
        removeBorderBottom()
        reply_to.html(createReplyTo(comment_id,commenter_name))
        
        $(this).closest('article').css({
            'border-bottom':'5px solid green'
        })
        
        $('html, body').animate({ //Scroll to the comment box
            scrollTop: $("#reply-to").offset().top-200
        });
    })

    //Handling edit comment
    $(".edit-comment").on('click',function(e){
        
        removeBorderBottom() //Remove border bottom from comments
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
        comment_content = $(this.closest('article')).find('#comment-content').text()
        
        // Remove substrings starting with "@" and ending with "..." at the beginning of the string
        comment_content = comment_content.replace(/^@[^.]*\.{3}/, '');

        
        $("#comment").val(comment_content)
        addHiddenInputToForm('comment-form','comment_edit','true')
        reply_to.html(editcomment(comment_id,commenter_name))
        
        $(this).closest('article').css({
            'border-bottom':'5px solid green'
        })
        
        $('html, body').animate({ //Scroll to the comment box
            scrollTop: $("#reply-to").offset().top-200
        });
    })

    //Funcion to handle like button
    $('#like-form').submit(function(e) {
        console.log('like form tiggered')
        e.preventDefault();  // Prevent default form submission
        var likeCount = $('#like-count').text(); // Get the current like count
        likeCount = likeCount.trim() !== "" ? parseInt(likeCount, 10) : 0; // If it's nothing, set it to 0

        $.ajax({
            url: $(this).attr('action'),  // Action URL
            method: $(this).attr('method'),  // Form method
            data: $(this).serialize(),  // Form data
            success: function(response) {
                feadback = JSON.parse(response)
                if (feadback['success']) {
                    if (feadback['status'] === 'liked') {
                        $('#like-status').attr('name','disliked')
                        $('.like-btn').css('background-color', 'green');
                        likeCount++;
                        $('#like-count').text(likeCount); // Update the like count in the div
                    } else if (feadback['status'] === 'disliked') {
                        $('#like-status').attr('name','liked')
                        $('.like-btn').css('background-color', 'white');
                        likeCount--;
                        $('#like-count').text(likeCount); // Update the like count in the div
                    }
                }
                else if(feadback['success'] == false){
                    console.log(response.msg)
                }
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
    
    

})