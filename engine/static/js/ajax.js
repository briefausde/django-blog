var $ = jQuery.noConflict();
    $(function() {
        $('#activator').click(function(){
            $('#box').animate({'top':'0px'},500);
        });
        $('#boxclose').click(function(){
            $('#box').animate({'top':'-700px'},500);
        });
    });
    $(document).ready(function(){
        $(".toggle_container").hide();
        $(".trigger").click(function(){
            $(this).toggleClass("active").next().slideToggle("slow");
                return false;
        });
    });

function unsubscribe_from_author(author){
    // var author = $(this).data('author');
    $.ajax({
        url: "/notifications/author/unsubscribe/",
        type: 'POST',
        data: {
            csrfmiddlewaretoken: tokens.csrf_token,
            author: author
        },
        success: function(){
            $('#subscribe').html("Subscribe to "+author+" updates").attr('onclick', "subscribe_on_author('"+author+"')");
        }
    });
}
function subscribe_on_author(author){
    $.ajax({
        url: "/notifications/author/subscribe/",
        type: 'POST',
        data: {
            csrfmiddlewaretoken: tokens.csrf_token,
            author: author
        },
        success: function(){
            $('#subscribe').html("Unsubscribe from "+author+" updates").attr('onclick', "unsubscribe_from_author('"+author+"')");
        }
    });
}
function notifications_count(){
    $.ajax({
        url: "/notifications/count/",
        type: 'POST',
        data: {
            csrfmiddlewaretoken: tokens.csrf_token,
        },
        success: function(html){
            if (html > 0) {
                $('#notifications').html(html);
            }
            else {
                $('#notifications').html("");
            }
        }
    });
}
function feedback_answered(pk){
    $.ajax({
        url: "/feedback/answered/",
        type: 'POST',
        data: {
            csrfmiddlewaretoken: tokens.csrf_token,
            pk: pk
        },
        success: function() {
            if($('#' + pk).attr('data') == "True") {
                $('#' + pk).html("Close feedback");
                $('#' + pk).attr('data', 'False');
            } else {
                $('#' + pk).html("Viewed");
                $('#' + pk).attr('data', "True");
            }
        }
    });
}
function notifications_viewed(pk){
    $.ajax({
        url: "/notifications/viewed/",
        type: 'POST',
        data: {
            csrfmiddlewaretoken: tokens.csrf_token,
            pk: pk
        },
        success: function() {
            $('#' + pk).css('color', 'darkgray').removeAttr('onclick');
            notifications_count();
        }
    });
}
function notification_delete(pk){
    $.ajax({
        url: "/notifications/delete/",
        type: 'POST',
        data: {
            csrfmiddlewaretoken: tokens.csrf_token,
            pk: pk
        },
        success: function() {
            $('#' + pk).remove();
            notifications_count();
        }
    });
}
function subscribe_on_post(pk){
    $.ajax({
        url: "/notifications/post/subscribe/",
        type: 'POST',
        data: {
            csrfmiddlewaretoken: tokens.csrf_token,
            pk: pk
        },
        success: function(){
            $('#subscribe').html("Unsubscribe from updates");
            $('#subscribe').attr('onclick', "unsubscribe_from_post('"+pk+"')");
        }
    });
}
function unsubscribe_from_post(pk){
    $.ajax({
        url: "/notifications/post/unsubscribe/",
        type: 'POST',
        data: {
            csrfmiddlewaretoken: tokens.csrf_token,
            pk: pk
        },
        success: function(){
            $('#subscribe').html("Subscribe on updates");
            $('#subscribe').attr('onclick', "subscribe_on_post('"+pk+"')");
        }
    });
}
function remove_comment(comment_id){
    $.ajax({
        url: "/comments/remove/",
        type: 'POST',
        data: {
            csrfmiddlewaretoken: tokens.csrf_token,
            id: comment_id
        },
        success: function(){
            updateComments();
        }
    });
}
//прописать полный путь, данные передавать в data-tag, csrf-токен через куки, доставать данные через $(this).data
