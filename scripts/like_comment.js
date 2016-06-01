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
            $('button#' + post_id + '.like-btn').addClass("hidden");
            $('button#' + post_id + '.unlike').removeClass("hidden");
        }).fail(function() {
            alert('Failed to reach server');
        });
    });

    // decrements num of likes by 1 and shows like button
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
    return false;
});
