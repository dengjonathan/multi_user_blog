var user_session = {
  logged_in : false,
  username : '',
  user_likes : [],
  user_comments : []
};

$(function(){
  // hide all CRUD buttons if user not logged in


  $.getScript('scripts/like_comment.js');
});
