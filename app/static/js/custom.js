var lat,long;

/**
 * Sets the paramter coordinates to the global variables lat,long
 * Used to find the location in Google maps
 */
function setCoords(lat,long){
    window.lat = lat;
    window.long = long;
}
/**
 * Sets up the map using the global lat,long coordinates
 * Finds 'map-canvas' on the page to display the map
 */

function initialize() {
  var mapOptions = {
    zoom: 10,
    center: new google.maps.LatLng(window.lat,window.long)
  };

  var map = new google.maps.Map(document.getElementById('map-canvas'),
      mapOptions);

  var panoramioLayer = new google.maps.panoramio.PanoramioLayer();
  panoramioLayer.setMap(map);
}//initialize
/**
 * Pops up FB login dialog to log user in
 * Logged in user is redirected to popular streams page
 * If the user is not registered, he is logged out of facebook, and
 * alerted to sign up before signing in
 */
function fblogin() {
        FB.login(function(response) {
            if (response.authResponse) {
                FB.api('/me',function(response) {
                    $.ajax({
                        type: 'POST',
                        url: 'http://localhost:5000/login',
                        data: JSON.stringify({'username': response.username}),
                        dataType: 'json',
                        success: function(data){
                            if(data.msg == -1){
                                alert('You need to sign up before signing in.');
                                fblogout();
                            }else{
                                    window.location = 'http://localhost:5000/stream/popular';
                            }
                        }
                    });
                });
            } else {
                alert('Unable to log into facebook! Please try again.');
            }
        });
}//fbLogin
//Logs user out of facebook
function fblogout(){
    FB.logout(function(response) {
        window.location = "http://localhost:5000";
    });
}
/**
 * Pops up FB dialog for user to log into facebook
 * The user's location is queried via FQL query to get the coordinates of his current location, if available
 * Else dummy coordinates are used
 * User's info is saved in the DB via AJAX and the user is logged in the system
 * If user is already registered, user is alerted and logged in the system
 */
function register(){
            FB.login(function(response) {
                if (response.authResponse) {
                console.log('Welcome!  Fetching your information.... ');
                FB.api('/me',function(response) {
                    var lat,long;
                    lat=long=null;
                 FB.api(
                  {
                    method: 'fql.query',
                    query: 'SELECT current_location.latitude, current_location.longitude FROM user WHERE uid=' + response.id
                  },
                  function(location) {
                      if(location[0]['current_location'] != null){
                          lat = location[0]['current_location']['latitude'];
                          long = location[0]['current_location']['longitude'];
                      }else{
                          lat = 12.9715987;
                          long = 77.5945627;
                      }
                    $.ajax({
                        type: 'POST',
                        url: 'http://localhost:5000/register',
                        data: JSON.stringify({'fullname': response.name, 'username': response.username,'email': response.email, 'location': lat+","+long}),
                        dataType: 'json',
                        success: function(data){
                            if(data.msg == 1){
                                alert("Successfully registered!");
                                setTimeout(function(){
                                    window.location = 'http://localhost:5000/stream/popular'
                                },100);
                            }else{
                                alert(data.msg);
                                fblogin();
                            }
                        }
                    });
                 }
                );
                });
            } else {
                alert('Unable to log in! Please try again later.');
            }
        }, { scope: 'email' });
}//register
/**
 * Grabs the comment, photo id of the commented photo and
 * added to the comments for the particular photo via AJAX
 * @param e
 */
function addComment(e){
    var comment = (e.prev('.say').val()).trim();
    e.prev('.say').val('');
    if(comment != ''){
           var photoId = e.prevAll('input[type="hidden"]').val();
        $.ajax({
            type: 'POST',
            url: 'http://localhost:5000/comment',
            data: JSON.stringify({'photo_id': photoId, 'comment': comment}),
            dataType: 'json',
            success: function(data){
                var reply = $('<div class="photo-rep">' +
                    '<input type="hidden" name="cid" value="'+data.id+'" />'+
                    '<a class="username pull-left" href="javascript:void(0)"><img src="'+data.photo+'" /></a>'+
                    '<a class="del-super pull-right" href="javascript:void(0)"><img title="Remove Comment" alt="Remove Comment" src="/static/img/del.png"></a>'+
                    '<p><span>'+data.fullname+'</span>  '+comment+'<br /><i>a few seconds ago</i></p>'+
                    '</div>');
                reply.css('opacity','0.0');
                e.parent().prev('.photo-rep-cont').append(reply);
                reply.animate({'opacity':'1.0'}, 1000);
                commentHover();
                removeComment();
            }
        }); //ajax
    }//if
}//addComment
/**
 * Grab the comment id and send a DELETE request to delete the comment for the
 * particular photo
 * @param e
 */
function removeComment(){
    //Prepare to remove the comment when comment delete icon is clicked
    $('.photo-rep').find('.del-super>img').on('click', function(){
        var e = $(this);
        var cid = e.parent().prevAll('input[type="hidden"]').val();
        $.ajax({
            type: 'DELETE',
            url: 'http://localhost:5000/comment/'+cid,
            success: function(data){
                if(data.msg == -1){
                    alert('An error occured!');
                }else{
                    e.parent().parent().animate({'opacity':'0.0'}, 1000, function(){
                        $(this).remove();
                    });
                }
            }
        }); //ajax
    });
}//removeComment
//Show/Hide comment delete icon on hovering over comment
function commentHover(){
    $('.photo-rep').hover(function(){
        $(this).find('.del-super>img').css('opacity','1.0');
    },function(){
        $(this).find('.del-super>img').css('opacity','0');
    });
}//commentHover

$(function(){

    commentHover();
    removeComment();
    // Handle user registration
    $('.nav').find('li.signup').on('click', function(){register()});
    //Add photo comment when user hits reply in the comment section
    $('.cmt-cont').find('button').on('click', function(){addComment($(this));});
    //Log user out of the system and facebook
    $('.nav').find('.signout').on('click', function(){
        $.ajax({
            type: 'GET',
            url: 'http://localhost:5000/logout',
            success:function(data){
               fblogout();
            }
        });
    });

    //Handle user login
    $('.signin').on('click', function(){fblogin();});
});

