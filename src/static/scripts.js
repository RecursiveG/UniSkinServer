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
        var _=["Register Success","Login Name Occupied","Invalid Login/Pwd","Server Error"]
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
        if (a.errno!=0){
          $('#mgr-error').html('Profile Update Failed');
        }else{
          $('#mgr-error').html('Success');
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
    if(f.size>2*1024*1024){
      alert("File too large");
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
    $("#img-div").slideUp();
    document.getElementById("preview-img").setAttribute("src","/textures/"+s)
    $("#img-div").slideDown();
    console.log(s);
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


/*$(document).ready(function(){
  genPreferBtn=(function(pre,lis){
    if(pre=="cape")return "";
    s1='<input type="button" value="Prefer" onclick="return setPrefer(\'';
    s2='\')">';
    s3="";
    if(pre=='slim')
      s3="slim|default";
      else
        s3="default|slim";
        return s1+s3+s2;
      });

      refresh=(function(){
        var token=$("#token").val()
        $.ajax({
          url: "/data",
          type: "POST",
          data: {"token": token},
          dataType: "json",
          success: function(data,stat){
            var str="";
            str+="User Name:"+data.player_name+"<br/>";
            str+="User UUID:"+data.uuid+"<br/>";
            str+="User Preference:"+data.model_preference.join("|")+"<br/>";
            for (var model in data.models){
              str+=model+":<img src=\"textures\\"+data.models[model]+"\"/><input type=\"button\" value=\"Delete\" onclick='return removeModel(\""+model+"\")'>"+genPreferBtn(model,data.models)+"</br>"
            }
            $("#userinfo").html(str);
          }
        });
      });

      setPrefer=(function(prefer){
        console.log("update prefer "+prefer);
        var token=$("#token").val()
        $.ajax({
          url: "/update",
          type: "POST",
          data: {
            "preference": prefer,
            "token": token
          },
          dataType: "json",
          success: function(data,stat){
            alert(data.msg);
            refresh();
          }
        });
      });

      $("#reg").click(function(){
        var login_name=$("#login").val()
        var login_pwd=$("#pwd").val()
        $.ajax({
          url: "/reg",
          type: "POST",
          data: {
            "login": login_name,
            "passwd": login_pwd
          },
          dataType: "json",
          success: function(data,stat){
            alert(data.msg);
          }
        });
      });
      $("#doLogin").click(function(){
        var login_name=$("#login").val()
        var login_pwd=$("#pwd").val()
        $.ajax({
          url: "/login",
          type: "POST",
          data: {
            "login": login_name,
            "passwd": login_pwd
          },
          dataType: "json",
          success: function(data,stat){
            if (data.errno!=0){
              alert(data.msg);
            }else{
              $("#token").val(data.msg)
              refresh()
            }
          }
        });
      });

      uploadFile=function(){
        $.ajaxFileUpload({
          url: "/upload",
          secureurl: false,
          fileElementId: "file",
          data: {
            "token": $("#token").val(),
            "type": $('input:radio[name=type]:checked').val()
          },
          dataType: "json",
          success: function(data,stat){
            alert(data.msg);
            refresh()
          }
        })
      };

      removeModel=function(modelName){
        console.log("Model Remove "+modelName);
        var token=$("#token").val()
        $.ajax({
          url: "/upload",
          type: "DELETE",
          data: {
            "type": modelName,
            "token": token
          },
          //dataType: "json",
          successcd: function(data,stat){
            alert(stat);
            refresh();
          }
        });
      }
    });*/
