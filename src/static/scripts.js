var session_token="";
var target_model="";
var local_data={};

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

function fillPair(model, isOff, isDyn, dynHash, staticHash) {
  if (isOff) {
    $('#remove-'+model+'-model').hide();
    $('#upload-'+model+'-model').hide();
    $('#switch-'+model+'-model').show();
    $('#'+model+'-model-hash').html('Model off');
    $('#remove-'+model+'-dynamic-model').hide();
    $('#upload-'+model+'-dynamic-model').hide();
    $('#interval-'+model+'-dynamic-model').hide();
    $('#'+model+'-dynamic-model-hash').html('Model off');
    return
  }
  if (isDyn == true) {
    $('#remove-'+model+'-model').hide();
    $('#upload-'+model+'-model').hide();
    $('#switch-'+model+'-model').show();
    $('#'+model+'-model-hash').html('Using dynamic skin.');

    $("#upload-"+model+"-dynamic-model").show();
    if (dynHash == undefined || dynHash.hashes == undefined || dynHash.hashes.length == 0) {
      $("#"+model+"-dynamic-model-hash").html('Not Uploaded');
      $("#interval-"+model+"-dynamic-model").hide();
      $("#remove-"+model+"-dynamic-model").hide();
    } else {
      var str = "Interval: "+dynHash.interval;
      for (var i=0; i< dynHash.hashes.length; i++) {
        str += '<br/>\n'+dynHash.hashes[i];
      }
      $("#"+model+"-dynamic-model-hash").html(str);
      $("#interval-"+model+"-dynamic-model").show();
      $("#remove-"+model+"-dynamic-model").show();
    }
  } else {
    $("#upload-"+model+"-dynamic-model").hide();
    $("#interval-"+model+"-dynamic-model").hide();
    $("#remove-"+model+"-dynamic-model").hide();
    $("#"+model+"-dynamic-model-hash").html('Using static skin.');

    $('#switch-'+model+'-model').show();
    if(staticHash != undefined && staticHash != ""){
      $('#'+model+'-model-hash').html(staticHash);
      $('#remove-'+model+'-model').show();
      $('#upload-'+model+'-model').hide();
    } else {
      $('#'+model+'-model-hash').html("Not Uploaded");
      $('#remove-'+model+'-model').hide();
      $('#upload-'+model+'-model').show();
    }
  }
}

$(document).ready(function(){
  refresh=(function(){
    $("#login-error").html('');
    $("#mgr-error").html('');
    $.ajax({
      url: "/userdata",
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
        local_data=data;
        $("#player-name").html(data.username);

        fillPair("steve", data.type_preference.skin=="off", data.type_preference.skin=="dynamic", data.textures.skin_default_dynamic, data.textures.skin_default_static)
        fillPair("alex", data.type_preference.skin=="off", data.type_preference.skin=="dynamic", data.textures.skin_slim_dynamic, data.textures.skin_slim_static)
        fillPair("cape", data.type_preference.cape=="off", data.type_preference.cape=="dynamic", data.textures.cape_dynamic, data.textures.cape_static)
        fillPair("elytra", data.type_preference.elytra=="off", data.type_preference.elytra=="dynamic", data.textures.elytra_dynamic, data.textures.elytra_static)

        $("#prefered-model").html(data.model_preference=='slim'?"Alex":"Steve");

        $('#login-name').val('');
        $('#pwd').val('');
        $('#current-passwd').val('');
        $('#new-passwd').val('');
        $('#mgr-error').html('');
        $("#login-div").slideUp();
        $("#info-div").slideDown();
        $("#img-div").slideUp();
        $("#manage-div").slideDown();
      })
    });
  });

  doLogin=(function(login,pwd){
    //console.log("Ready to login with "+login+"/"+pwd);
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
          //console.log("Login Success with token: "+token);
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
    var login=$("#login-name").val();
    var pwd=$("#pwd").val();
    $.ajax({
      url: "/register",
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
        if(data.errno==0){
          //console.log("Register Success, ready to login with "+login+"/"+pwd);
          setTimeout(function(){doLogin(login,pwd);},1000);
        }else{
          $("#login-error").html(data.msg);
        }
      })
    });
  });

  $("#logBtn").click(function(){
    $("#login-error").html('');
    var login=$("#login-name").val();
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
        $('#login-name').val('');
        $('#pwd').val('');
      })
    });
  });

  $("#change-passwd").click(function(){
    $('#mgr-error').html('');
    var old_pwd=$("#current-passwd").val();
    var new_pwd=$("#new-passwd").val();
    $.ajax({
      url: '/chpwd',
      type: "POST",
      data: {
        'token': session_token,
        'new_passwd': new_pwd,
        'current_passwd': old_pwd,
        'login': $('#player-name').html()
      },
      dataType: 'json',
      success: (function(a,b){
        if (a.errno==0){
          $('#mgr-error').html('Success');
        }else{
          $('#mgr-error').html(a.msg);
        }
      })
    });
  });

  function set_dynamic_prefer(model) {
    var t= ""
    if (local_data.type_preference[model]=="static") t = "dynamic";
    if (local_data.type_preference[model]=="dynamic") t = "off";
    if (local_data.type_preference[model]=="off") t = "static";
    $.ajax({
      url: '/type_preference',
      type: "POST",
      data: {
        'token': session_token,
        'type': model,
        'preference': t,
      },
      dataType: 'json',
      success: (function(a,b){
        if(a.errno!=0)
          alert("Error: "+a.msg);
        else
          setTimeout(refresh,500);
      })
    });
  }
  $("#switch-steve-model").click(function(){set_dynamic_prefer("skin")});
  $("#switch-alex-model").click(function(){set_dynamic_prefer("skin")});
  $("#switch-cape-model").click(function(){set_dynamic_prefer("cape")});
  $("#switch-elytra-model").click(function(){set_dynamic_prefer("elytra")});

  $(document).on('change','#filechoose',function(e){
    e.preventDefault();
    //console.log('changed');
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
      url: "/upload_texture",
      secureurl: false,
      fileElementId: "filechoose",
      data: {
        "token": session_token,
        'model': m.model,
        "type": m.type
      },
      dataType: "json",
      success: function(data,stat){
        //alert(data.msg);
        $('#filechoose').val(null);
        if(data.errno!=0)
          alert("Error Happened: "+data.msg);
        else
          setTimeout(refresh,500);
      }
    });
    return false;
  });
  uploadModel=(function(model, type){
    target_model={'model':model, 'type': type};
    $('#filechoose').val(null);
    $('#filechoose').click();
  });
  $('#upload-steve-model').click(function(){uploadModel('skin_default','static')});
  $('#upload-alex-model').click(function(){uploadModel('skin_slim','static')});
  $('#upload-cape-model').click(function(){uploadModel('cape','static')});
  $('#upload-elytra-model').click(function(){uploadModel('elytra','static')});
  $('#upload-steve-dynamic-model').click(function(){uploadModel('skin_default','dynamic')});
  $('#upload-alex-dynamic-model').click(function(){uploadModel('skin_slim','dynamic')});
  $('#upload-cape-dynamic-model').click(function(){uploadModel('cape','dynamic')});
  $('#upload-elytra-dynamic-model').click(function(){uploadModel('elytra','dynamic')});

  removeModel=(function(model, type){
    //console.log("Model Remove "+modelName);
    var token=$("#token").val()
    $.ajax({
      url: "/delete_texture",
      type: "POST",
      data: {
        "model": model,
        "token": session_token,
        "type": type
      },
      dataType: "json",
      success: function(data,stat){
        if (data.errno==0){
          setTimeout(refresh,500);
        } else {
          alert("Error: " +data.msg);
        }
      }
    });
  });
  $('#remove-steve-model').click(function(){removeModel('skin_default','static')});
  $('#remove-alex-model').click(function(){removeModel('skin_slim','static')});
  $('#remove-cape-model').click(function(){removeModel('cape','static')});
  $('#remove-elytra-model').click(function(){removeModel('elytra','static')});
  $('#remove-steve-dynamic-model').click(function(){removeModel('skin_default','dynamic')});
  $('#remove-alex-dynamic-model').click(function(){removeModel('skin_slim','dynamic')});
  $('#remove-cape-dynamic-model').click(function(){removeModel('cape','dynamic')});
  $('#remove-elytra-dynamic-model').click(function(){removeModel('elytra','dynamic')});

  setInter=(function(model){
    var token=$("#token").val()
    var new_interval = prompt("New Interval?");
    if (new_interval==null) return;
    $.ajax({
      url: "/dynamic_interval",
      type: "POST",
      data: {
        "token": session_token,
        "type": model,
        "interval": new_interval
      },
      dataType: "json",
      success: function(data,stat){
        if (data.errno==0){
          setTimeout(refresh,500);
        } else {
          alert("Error: " +data.msg);
        }
      }
    });
  });
  $('#interval-steve-dynamic-model').click(function(){setInter('skin_default')});
  $('#interval-alex-dynamic-model').click(function(){setInter('skin_slim')});
  $('#interval-cape-dynamic-model').click(function(){setInter('cape')});
  $('#interval-elytra-dynamic-model').click(function(){setInter('elytra')});

  $('#switch-prefered-model').click(function(){
    var x=$('#prefered-model').html();
    $.ajax({
      url: "/model_preference",
      type: "POST",
      data: {
        "prefered_model": x=="Alex"?"default":"slim",
        "token": session_token
      },
      dataType: "json",
      success: function(data,stat){
        //alert(data.msg);
        if(data.errno!=0)
          alert("Error: "+data.msg);
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

  $("#delete-account").click(function(){
    $('#mgr-error').html('');
    if(confirm('Do you really want to delete your account?')){
      $.ajax({
        url: "/delete_account",
        type: "POST",
        data: {
          "current_passwd": $("#current-passwd").val(),
          "token": session_token,
          'login': $('#player-name').html()
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
