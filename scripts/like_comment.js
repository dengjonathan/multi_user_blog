$(document).ready(function() {

  // show edit article form
  // TODO: why does this method post when clicked on?
    $('button.edit_article').click(function() {
        $('div#' + this.id + '.edit_article').toggleClass('hidden');
        $(this).text($(this).text() == 'Edit Post' ? 'Cancel' : 'Edit Post');
        $('button#' + this.id + '.delete_article').toggleClass('hidden');
    });

    // when click delete button deletes article
    $('button.delete_article').click(function() {
      $('div#' + this.id + '.delete_article').toggleClass('hidden');
      $(this).text($(this).text() == 'Delete Post' ? 'Cancel' : 'Delete Post');
      $('button#' + this.id + '.edit_article').toggleClass('hidden');
    });

    // show edit comment form
    $('button.edit_comment').click(function() {
        $('div#' + this.id + '.edit_comment').toggleClass('hidden');
        $(this).text($(this).text() == 'Edit' ? 'Cancel' : 'Edit');
        $('button#' + this.id + '.delete_comment').toggleClass('hidden');
    });

    // show delete comment form
    $('button.delete_comment').click(function() {
        $('form#' + this.id + '.delete_comment').toggleClass('hidden');
        $(this).text($(this).text() == 'Delete' ? 'Cancel' : 'Delete');
        $('button#' + this.id + '.edit_comment').toggleClass('hidden');
    });
});
