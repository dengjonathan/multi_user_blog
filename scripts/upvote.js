$('button.upvote').click(function() {
  var key = $(this).parent().attr('id');
  var data = {key: key, action: 'add_like', data:[]};
  var likes = $(this).next().find('span');
  $.post('/post', data)
    .success(function(response) {
      $(likes).html(JSON.parse(response).data);
    })
    .fail(function(error) {
      //TODO: do stuff on fail
    });
});

$('button.downvote').click(function() {
  var key = $(this).parent().attr('id');
  var data = {key: key, action: 'unlike', data:[]};
  var likes = $(this).prev().find('span');
  $.post('/post', data)
    .success(function(response) {
      $(likes).html(JSON.parse(response).data);
    })
    .fail(function(error) {
      //TODO: do stuff on fail
    });
})
