function startSession(){
    var username = $("#username").val();
    var customerType = $("#customer-type").val();
    sessionStorage.setItem("username", username);
    postSession(username, customerType);
}

$( "#btnProfile" ).click(function( event ) {
  event.preventDefault();
  var user = sessionStorage.getItem("username");
  var profileData = { "address": $("#inputAddress").val(), "city": $("#inputCity").val(), "state": $("#inputState").val(), "zip": $("#inputZip").val()  }
  postProfile(user, profileData);
});

$( "#btnOrder" ).click(function( event ) {
  event.preventDefault();
  var user = sessionStorage.getItem("username");
  var orderData = { "user": user, "location": $("#location").val(), "total": $("#total").val() }
  postOrder(user, orderData);
});


function postSession(user, session){
    
    $.ajax({
      type: "POST",
      url: "/postSession/" + user,
      data:  JSON.stringify({ "name": user, "type": session  }),
      success: function (data) {
            sessionSuccess("/profile/" + user);
      },
      contentType: "application/json"
    });
}

function getSession(user){
    $.ajax({
        type:"GET",
        url: "/getSession/" + user,
        success: sessionSuccess("/profile/" + user)
    })
}

function sessionSuccess(url){
    window.location.href = url;
}

function postProfile(user, profile){
    $.ajax({
      type: "POST",
      url: "/postProfile/" + user,
      data:  JSON.stringify(profile),
      success: function (data) {
            sessionSuccess("/order/" + user);
      },
      contentType: "application/json"
    });
}

function getProfile(user){
    $.ajax({
        type:"GET",
        url: "/getProfile/" + user,
        success: function (data) {
            sessionSuccess("/order/" + user);
      }
    })
}

function reloadSession(){
if (sessionStorage.getItem("username") != null){
        getSession(sessionStorage.getItem("username"));
    }
}

function postOrder(user, order){
    $.ajax({
      type: "POST",
      url: "/postOrder/" + user,
      data:  JSON.stringify(order),
      success: function (data) {
            var parsedJson = $.parseJSON(data);
            sessionSuccess("/orders/" +  user );
      },
      contentType: "application/json"
    });
}

function loadOrders(user){
        $.ajax({
        type:"GET",
        url: "/getOrders/" + user,
        success: function (data) {
            console.log(data);
            var parsedJson = $.parseJSON(data);
            var tbl = $("#orders > tbody");
            $.each(parsedJson, function(i, item) {
                var row = $.parseJSON(item.replace(/\'/g, "\""));
                $("#orders > tbody").append("<tr>" +
                "<td>" + "ID" + row.id +  "</td>" +
                "<td>"  + row.total + "</td>" +
                "<td>"  + row.location + "</td>" +
                "<td>" + row.status + "</td>"
                + "</tr>");
                });
        }
    });
}
    