$(document).ready(function() {

    // increases number of likes for Post object in datastore
    $('button.like-btn').click(function() {
        var post_id = this.id;
        $.post('/', {
            'key': post_id,
            'action': 'add_like',
            'data': ''
        }).done(function(response) {
            response = $.parseJSON(response);
            $('div#' + post_id + '> p').text(response['num_likes'] + ' people like this!');
            console.log(this);
            $('button#' + post_id + '.like-btn').addClass("hidden");
            $('button#' + post_id + '.unlike').removeClass("hidden");
        }).fail(function() {
            alert('Failed to reach server');
        });
    });

    // decrements num of likes by 1 and shows like button
    // TODO: fix unlike button logic
    $('button.unlike').click(function() {
        var post_id = this.id;
        $.post('/', {
            'key': post_id,
            'action': 'unlike',
            'data': ''
        }).done(function(response) {
            response = $.parseJSON(response);
            $('div#' + post_id + '> p').text(response['num_likes'] + ' people like this!');
            $('button#' + post_id + '.unlike').addClass("hidden");
            $('button#' + post_id + '.like-btn').removeClass("hidden");
        }).fail(function() {
            alert('Failed to reach server');
        });
    });

    // new comment button inserts comment in database and updates homepage
    $('button.new_comment').click(function() {
        var username = $('#session-username').text();
        var post_id = this.id;
        var comment = $('div.new_comment input:text').val();
        $.post('/', {
            'key': post_id,
            'action': 'new_comment',
            'data': comment
        }).done(function(response) {
            response = $.parseJSON(response);
            var comment = response['comment'];
            var time_stamp = response['time_stamp'];
            var input = '<li>' + username + ' says ' + comment + ' ' +
                time_stamp + '</li>';
            $('#' + post_id + 'comments').append(input);
            $('input').val('');
        }).fail(function() {
            alert('Failed to reach server');
        });
    });

    // when click on edit post button shows input field for editing and edit button
    $('button.edit_article').click(function() {
        $('form#' + this.id + '.edit_article').toggleClass('hidden');
        $(this).text($(this).text() == 'Edit Post' ? 'Cancel' : 'Edit Post');
        $('button#' + this.id + '.delete_article').toggleClass('hidden');
    });

    // when click delete button deletes article
    $('button.delete_article').click(function() {
        var post_id = this.id;
        $.post('/', {
            'key': post_id,
            'action': 'delete_article'
        }).done(function(response) {
            window.location.replace('/');
            $('div#' + post_id + '.article').replaceWith('');
        }).fail(function() {
            alert('Failed to reach server');
        });
    });

    // Edit comment form
    $('button.edit_comment').click(function() {
        $('form#' + this.id + '.edit_comment').toggleClass('hidden');
        $(this).text($(this).text() == 'Edit' ? 'Cancel' : 'Edit');
        $('button#' + this.id + '.delete_comment').toggleClass('hidden');
    });

    // Edit comment post to server
    $('input.submit_edit_comment').click(function() {
        var comment = $(this).parent()[0];
        console.log(comment)
        var post_id = comment.id;
        console.log(post_id)
        var edit_comment = $('input[name="edit_comment"]').val()
        console.log(edit_comment)
        $.post('/', {
            'key': post_id,
            'action': 'edit_comment',
            // TODO: this is a nightmare heere - how to reference comments?j
            'data': {'comment_id': comment.attr('id'), 'edit_comment': edit_comment}
        }).done(function(response) {
            console.log(response);
            comment.replaceWith('');
        }).fail(function(error) {
            alert(error);
        });
    });

    // Delete comment
    $('button.delete_comment').click(function() {
        var post_id = this.id;
        var comment = $(this).parent();
        $.post('/', {
            'key': post_id,
            'action': 'delete_comment',
            'data': comment.attr('id')
        }).done(function(response) {
            comment.replaceWith('');
        }).fail(function() {
            alert('Failed to reach server');
        });
    });
    return false;
});
