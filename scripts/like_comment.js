$(document).ready(function() {
  // increases number of likes for Post object in datastore
    $('button.like-btn').click(function() {
        var post_id = this.id;
        $.post('/', {
            'key': post_id,
            'like': true
        }).done(function(response) {
            response = $.parseJSON(response);
            $('div#' + post_id + '> p').text(response['num_likes'] + ' people like this!');
            $('button#' + post_id + '.like-btn').addClass("hidden");
            $('button#' + post_id + '.unlike-btn').removeClass("hidden");
        }).fail(function() {
            alert('Failed to reach server');
        });
    });

    // decrements num of likes by 1 and shows like button
    $('button.unlike-btn').click(function() {
        var post_id = this.id;
        $.post('/', {
            'key': post_id,
            'unlike': true
        }).done(function(response) {
            response = $.parseJSON(response);
            $('div#' + post_id + '> p').text(response['num_likes'] + ' people like this!');
            $('button#' + post_id + '.unlike-btn').addClass("hidden");
            $('button#' + post_id + '.like-btn').removeClass("hidden");
        }).fail(function() {
            alert('Failed to reach server');
        });
    });

    // new comment button inserts comment in database and updates homepage
    $('button.new_comment').click(function() {
        if ($('#session-username').text()) {
            var username = $('#session-username').text();
            var post_id = this.id;
            var comment = $('div.new_comment input:text').val();
            $.post('/', {
                'key': post_id,
                'comment': comment
            }).done(function(response) {
                response = $.parseJSON(response);
                var comment = response['comment'];
                var time_stamp = response['time_stamp'];
                console.log(time_stamp);
                var input = '<li>' + username + ' says ' + comment + ' ' +
                    time_stamp + '</li>';
                $('#' + post_id + 'comments').append(input);
            }).fail(function() {
                alert('Failed to reach server');
            });
        } else {
            $('p.error').text('You need to login or register to comment.');
        }
    });
    return false;
});
