var session_token="";
var target_model="";

if (typeof String.prototype.endsWith != 'function') {
  String.prototype.endsWith = function(suffix) {
    return this.indexOf(suffix, this.length - suffix.length) !== -1;
  };
}

function fillModelStatus(n1,l,n2){
  if(n1 in l){
    var ll='<a href="#'+l[n1]+'" class="texture-preview">Display Texture</a>';
    $('#remove'+n2+'Model').show();
    $('#upload'+n2+'Model').hide();
    $('#'+n2+'model').html("");
    $('#'+n2+'model').append(ll);
  }else{
    $('#'+n2+'model').html("Not Uploaded");
    $('#remove'+n2+'Model').hide();
    $('#upload'+n2+'Model').show();
  }
}

$(document).ready(function(){
  refresh=(function(){
    $("#login-error").html('');
    $("#mgr-error").html('');
    $.ajax({
      url: "/data",
      type: "POST",
      data: {"token": session_token},
      dataType: "json",
      success: (function(data,stat){
        if(stat!="success"){
          alert("Server Down. Please try later");
          return;
        }
        if('errno' in data){
          alert('Failed to refresh data');
          return;
        }
        $("#playername").html(data.player_name);
        $("#playeruuid").html(data.uuid)
        var p=data.model_preference[0]
        $("#preferedmodel").html(p=='slim'?"Alex":"Steve");

        fillModelStatus('slim',data.models,'Alex');
        fillModelStatus('default',data.models,'Steve');
        fillModelStatus('cape',data.models,'Cape');

        $('#loginname').val('');
        $('#pwd').val('');
        $('#currentpwd').val('');
        $('#newpassword').val('');
        $('#mgr-error').html('');
        $("#login-div").slideUp();
        $("#info-div").slideDown();
        $("#img-div").slideUp();
        $("#manage-div").slideDown();
      })
    });
  });

  doLogin=(function(login,pwd){
    console.log("Ready to login with "+login+"/"+pwd);
    $.ajax({
      url: "/login",
      type: "POST",
      data: {
        "login": login,
        "passwd": pwd
      },
      dataType: "json",
      success: (function(data,stat){
        if(stat!="success"){
          $("#login-error").html("Login fail. Please try later.");
          return;
        }
        var result=data.errno;
        if(result==0){
          token=data.msg;
          console.log("Login Success with token: "+token);
          session_token=token;
          setTimeout(refresh,500);
        }else{
          $("#login-error").html("Invalid Login");
        }
      })
    });
  });

  $("#regBtn").click(function(){
    $("#login-error").html('');
    var login=$("#loginname").val();
    var pwd=$("#pwd").val();
    $.ajax({
      url: "/reg",
      type: "POST",
      data: {
        "login": login,
        "passwd": pwd
      },
      dataType: "json",
      success: (function(data,stat){
        if(stat!="success"){
          $("#login-error").html("Register fail. Please try later.");
          return;
        }
        var result=data.errno;
        var _=["Register Success","Login Name Occupied","Invalid Login/Pwd","Server Error","Register not allowed"]
        if(result==0){
          console.log("Register Success, ready to login with "+login+"/"+pwd);
          setTimeout(function(){doLogin(login,pwd);},1000);
        }else{
          $("#login-error").html(_[result]);
        }
      })
    });
  });

  $("#logBtn").click(function(){
    $("#login-error").html('');
    var login=$("#loginname").val();
    var pwd=$("#pwd").val();
    doLogin(login,pwd);
  });

  $("#logout").click(function(){
    $.ajax({
      url: "/logout",
      type: "POST",
      data: {'token': session_token},
      complete: (function(a,b){
        $('#login-error').html('');
        $("#login-div").slideDown();
        $("#info-div").slideUp();
        $("#manage-div").slideUp();
        $("#img-div").slideUp();
        $('#loginname').val('');
        $('#pwd').val('');
      })
    });
  });

  $("#changepasswd").click(function(){
    $('#mgr-error').html('');
    var old_pwd=$("#currentpwd").val();
    var new_pwd=$("#newpassword").val();
    $.ajax({
      url: '/update',
      type: "POST",
      data: {
        'token': session_token,
        'new_passwd': new_pwd,
        'current_passwd': old_pwd
      },
      dataType: 'json',
      success: (function(a,b){
        if (a.errno==0){
          $('#mgr-error').html('Success');
        }else if(a.errno==3){
          $('#mgr-error').html('New pwd too short');
        }else if(a.errno==1){
          $('#mgr-error').html('current pwd required');
        }else if(a.errno==2){
          $('#mgr-error').html('pwd incorrect');
        }else{
          $('#mgr-error').html('Profile Update Failed');
        }
      })
    });
  });

  $(document).on('change','#filechoose',function(e){
    e.preventDefault();
    console.log('changed');
    if(target_model=="")return;
    var f=$('#filechoose')[0].files[0];
    var m=target_model;target_model="";
    if(!f.name.endsWith('.png')){
      alert("Only png files are acceptable");
      $('#filechoose').val(null);
      return;
    }
    if(f.size>1024*1024){
      alert("File too large. Max: 1MB");
      $('#filechoose').val(null);
      return;
    }
    $.ajaxFileUpload({
      url: "/upload",
      secureurl: false,
      fileElementId: "filechoose",
      data: {
        "token": session_token,
        "type": m
      },
      dataType: "json",
      success: function(data,stat){
        //alert(data.msg);
        $('#filechoose').val(null);
        if(data.errno!=0)
          alert("Error Happened!");
        else
          setTimeout(refresh,500);
      }
    });
    return false;
  });
  uploadModel=(function(m){
    target_model=m
    $('#filechoose').val(null);
    $('#filechoose').click();
  });
  $('#uploadAlexModel').click(function(){uploadModel('slim')});
  $('#uploadSteveModel').click(function(){uploadModel('default')});
  $('#uploadCapeModel').click(function(){uploadModel('cape')});

  removeModel=(function(modelName){
    console.log("Model Remove "+modelName);
    var token=$("#token").val()
    $.ajax({
      url: "/upload",
      type: "DELETE",
      data: {
        "type": modelName,
        "token": session_token
      },
      //dataType: "json",
      success: function(data,stat){
        //alert(stat);
        setTimeout(refresh,500);
      }
    });
  });
  $('#removeAlexModel').click(function(){removeModel('slim')});
  $('#removeSteveModel').click(function(){removeModel('default')});
  $('#removeCapeModel').click(function(){removeModel('cape')});

  $('#switchPreferedModel').click(function(){
    var x=$('#preferedmodel').html();
    $.ajax({
      url: "/update",
      type: "POST",
      data: {
        "preference": x=="Alex"?"default|slim":"slim|default",
        "token": session_token
      },
      dataType: "json",
      success: function(data,stat){
        //alert(data.msg);
        if(data.errno!=0)
          alert("Error Happened!");
        else
          setTimeout(refresh,500);
      }
    });
  });

  $(document).on('click','.texture-preview',function(e){
    s=e.currentTarget.getAttribute('href').substr(1);
    $("#img-div").slideUp('normal',function(){
      document.getElementById("preview-img").setAttribute("src","/textures/"+s);
      $("#img-div").slideDown('normal');
    });
  });

  $("#deleteaccount").click(function(){
    $('#mgr-error').html('');
    if(confirm('Do you really want to delete your account?')){
      $.ajax({
        url: "/reg",
        type: "DELETE",
        data: {
          "pwd": $("#currentpwd").val(),
          "token": session_token
        },
        dataType: "json",
        success: function(data,stat){
          //alert(data.msg);
          if(data.errno==0){
            setTimeout(function(){$('#logout').click();},500);
          }else{
            $('#mgr-error').html('Account not deleted');
          }
        }
      });
    }
  });
});
