/*
This script allows app to reflect CRUD updates asynchronously without
reloading page after database updates.
*/
$(document).ready(function() {

  // hide all buttons if user not logged in
  if (!$('p#session-username').text()) {
    $('button').addClass('hidden');
    $('div.login-reminder').removeClass('hidden');
  }

  function alertError(error) {
    error = error.responseText.split('raise Exception(error)')[1]
      .split('</pre>')[0];
      console.log(error);
    $('.error').text(error);
  }

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
        alertError();
      });
  });

  $('button.downvote').click(function() {
    var key = $(this).parents('.article-container').attr('id');
    var data = {
      key: key,
      action: 'unlike',
      data: ''
    };
    var likes = $(this).parent().prev().find('span');
    $.post('/post', data)
      .success(function(response) {
        $(likes).html(JSON.parse(response).data);
      })
      .fail(function(error) {
        alertError(error);
      });
  });

  (function() {
    // preserve JQuery selectors for both functions
    var edit_form, edit_form_btn, delete_form_btn;

    $('button.edit_comment_form').unbind('click').click(function() {
      edit_form = $(this).prevAll('div.edit_comment');
      $(edit_form).toggleClass('hidden');
      edit_form_btn = $(this);
      $(edit_form_btn).text($(edit_form_btn).text() == 'Edit' ? 'Cancel' : 'Edit');
      delete_form_btn = $(this).next('button.delete_comment_form')
      delete_form_btn.toggleClass('hidden');
    });

    $('button.update-comment').click(function() {
      var key = $(this).parents('div.article-container').attr('id');
      var comment_index = $(this).parents('li.comment-container').attr('id');
      var new_comment = $(this).prev('input').val();
      var data = {
        key: key,
        action: 'edit_comment',
        data: comment_index,
        new_comment: new_comment,
      };
      var comment_text = $(this).parents('li.comment-container').find('span.comment');
      $(this).next('button.delete_comment_form').toggleClass('hidden');
      $.post('/post', data)
        .success(function(response) {
          $(comment_text).text(new_comment);
          $(edit_form).toggleClass('hidden');
          $(edit_form_btn).text($(edit_form_btn).text() == 'Edit' ? 'Cancel' : 'Edit');
          $(delete_form_btn).toggleClass('hidden');
        })
        .fail(function(error) {
          alertError(error);
          $(edit_form).toggleClass('hidden');
          $(edit_form_btn).text($(edit_form_btn).text() == 'Edit' ? 'Cancel' : 'Edit');
          $(delete_form_btn).toggleClass('hidden');
        });
    });

  })();

  (function() {
    // preserve JQuery selectors for both functions
    var delete_form, delete_form_btn, edit_form_btn;

    // show delete comment form
    $('button.delete_comment_form').unbind('click').click(function() {
      delete_form = $(this).prevAll('div.delete-comment');
      delete_form_btn = $(this);
      edit_form_btn = $(this).prev('button.edit_form')
      $(delete_form).toggleClass('hidden');
      $(delete_form_btn).text($(delete_form_btn).text() == 'Delete' ? 'Cancel' : 'Delete');
      $(edit_form_btn).toggleClass('hidden');
    });

    $('button.delete_comment').click(function() {
      var key = $(this).parents('div.article-container').attr('id')
      var comment_index = $(this).parents('li.comment-container').attr('id')
      var comment = $(this).parents('li.comment-container');
      var data = {
        key: key,
        action: 'delete_comment',
        data: comment_index
      }
      $.post('/post', data)
        .success(function(response) {
          $(comment).remove();
        })
        .fail(function(error) {
          alertError(error);
        });
    });
  })();

  (function() {
    // preserve JQuery selectors for both functions
    var edit_form, edit_form_btn, delete_form_btn;

    $('button.edit_article_form').click(function() {
      edit_form = $(this).prevAll('div.edit_article_form');
      edit_form_btn = $(this);
      delete_form_btn = $(this).next('delete_article_form');
      $(edit_form).toggleClass('hidden');
      $(edit_form_btn).text($(edit_form_btn).text() == 'Edit Post' ? 'Cancel' : 'Edit Post');
      $(delete_form_btn).toggleClass('hidden');
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
      $.post('/post', data)
        .success(function(response) {
          art_title.text(title);
          art_msg.text(message);
          $(edit_form).toggleClass('hidden');
          $(edit_form_btn).text($(edit_form_btn).text() == 'Edit Post' ? 'Cancel' : 'Edit Post');
          $(delete_form_btn).toggleClass('hidden');
        })
        .fail(function(error) {
          alertError(error);
          $(edit_form).toggleClass('hidden');
          $(edit_form_btn).text($(edit_form_btn).text() == 'Edit Post' ? 'Cancel' : 'Edit Post');
          $(delete_form_btn).toggleClass('hidden');
        });
    });
  })();

  // shows form for deleting article
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
      .fail(function(error) {
        alertError(error);
      });
  });

  $('button.new_comment').click(function() {
    var key = $(this).parents('div.article-container').attr('id');
    var comment = $(this).prev().val();
    var input = $(this).prev();
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
        // FIXME: when adding comment template, none of buttons work
        $(list).append(JSON.parse(response).data);
        $(input).val('');
      })
      .fail(function(error) {
        alertError(error);
      });
  });
});
