$('button.upvote').click(function() {
  var key = $(this).parents('.article-container').attr('id');
  var data = {
    key: key,
    action: 'add_like',
    data: ''
  };
  var likes = $(this).parent().next().find('span');
  $.post('/post', data)
    .success(function(response) {
      $(likes).html(JSON.parse(response).data);
    })
    .fail(function(error) {
      //TODO: do stuff on fail
    });
});

$('button.downvote').click(function() {
  var key = $(this).parents('.article-container').attr('id');
  var data = {
    // key: key,
    action: 'unlike',
    data: ''
  };
  var likes = $(this).parent().prev().find('span');
  $.post('/post', data)
    .success(function(response) {
      $(likes).html(JSON.parse(response).data);
    })
    .fail(function(error) {
      //TODO: do stuff on fail
    });
});

// show edit comment form
$('button.edit_form').click(function() {
  console.log($(this).prevAll('div.edit_comment'));
  $(this).prevAll('div.edit_comment').toggleClass('hidden');
  $(this).text($(this).text() == 'Edit' ? 'Cancel' : 'Edit');
  $(this).next('button.delete_form').toggleClass('hidden');
});

$('button.update-comment').click(function() {
  var key = $(this).parents('div.article-container').attr('id');
  var comment_index = $(this).parents('li.comment-container').attr('id');
  console.log(comment_index);
  var comment = $(this).prev('input');
  var data = {
    key: key,
    action: 'edit_comment',
    data: $(comment).val(),
    comment_index: comment_index
  };
  var comment_text = $(this).parents('li.comment').find('span.comment');
  console.log(comment_text);
  console.log(key, comment_index, comment);
  $.post('/post', data)
    .success(function(response) {
      console.log(response);
      $(comment_text).text(JSON.parse(response).data);
    })
    .fail(function(error) {
      //TODO: do stuff on fail
    });
});

// show delete comment form
$('button.delete_form').click(function() {
  var form = $(this).prev().prev();
  $(form).toggleClass('hidden');
  $(this).text($(this).text() == 'Delete' ? 'Cancel' : 'Delete');
  $('button#' + this.id + '.edit_comment').toggleClass('hidden');
  $(this).prev('button.edit_form').toggleClass('hidden');
});

// javascript handler for deleting comments
$('button.delete_comment').click(function() {
  var key = $(this).parents('div.article-container').attr('id')
  var comment_index = $(this).parents('li.comment-container').attr('id')
  var comment = $(this).parents('li.comment-container');
  console.log(comment);
  console.log(key, comment_index);
  var data = {
    key: key,
    action: 'delete_comment',
    data: comment_index
  }
  $.post('/post', data)
    .success(function(response) {
      console.log(response);
      $(comment).remove();
    })
    .fail(function(error) {
      //TODO: do stuff on fail
    });
});

$('button.edit_article_form').click(function() {
  $(this).prevAll('div.edit_article_form').toggleClass('hidden');
  $(this).text($(this).text() == 'Edit Post' ? 'Cancel' : 'Edit Post');
  //$('button#' + this.id + '.delete_article').toggleClass('hidden');
});

// handler for updating article
$('button.edit_article').click(function() {
  var key = $(this).parents('div.article-container').attr('id');
  var title = $(this).prevAll('input.new-title').val()
  var message = $(this).prevAll('textarea.new-message').val();
  // reference article title span
  var art_title = $(this).parents('div.article-container').children('div.post-title');
  var art_msg = $(this).parents('div.article-container').children('div.post-message');
  var data = {
    key: key,
    action: 'edit_article',
    data: title,
    message: message
  };
  console.log(data);
  $.post('/post', data)
    .success(function(response) {
      art_title.text(title);
      art_msg.text(message);
    })
    .fail(function(error) {
      //TODO: do stuff on fail
    });
});

// handler for deleting article
$('button.delete_article_form').click(function() {
  $(this).prevAll('div.delete_article_form').toggleClass('hidden');
  $(this).text($(this).text() == 'Delete Post' ? 'Cancel' : 'Delete Post');
});

$('button.delete_article').click(function() {
  var key = $(this).parents('div.article-container').attr('id');
  var data = {
    key: key,
    action: 'delete_article'
  };
  var article_node = $(this).parents('div.article-container');
  $.post('/post', data)
    .success(function(response) {
      $(article_node).remove();
    })
    .fail(function(error) {});
});

$('button.new_comment').click(function() {
  var key = $(this).parents('div.article-container').attr('id');
  var comment = $(this).prev().val();
  var data = {
    key: key,
    data: comment,
    action: 'new_comment'
  };
  var list = $(this).parent('div').prev('ul.comments-list');
  $.post('/post', data)
    .success(function(response) {
      // post method will return new comment html template as response
      // append template to ul.comment_list DOM node
      $(list).append(JSON.parse(response).data);
    })
    .fail(function(error) {});
});
