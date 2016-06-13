// hide all buttons if user not logged in
$(function(){
  if (user_session.logged_in == false){
    $('button').addClass('hidden');
  }
});
