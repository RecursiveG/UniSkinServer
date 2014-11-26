<?php 
require 'config.inc.php';
if (!$con)
{
Header("HTTP/1.1 403 Forbidden");
die('Could not connect: ' . mysql_error());
}
mysql_select_db("dbname", $con);
if ($_GET['legacy']=='1') {
  $result = mysql_query("SELECT * FROM users WHERE name='" . filename . "'");
  if ($result){$row = mysql_fetch_array($result);}
  else {
  Header("HTTP/1.1 301 Moved Permanently");
  Header("Location: http://skins.minecraft.net/Minecraft" . $_GET['type'] . "/" . filename . ".png");
  exit(0);
  }
  if (!$row){
    Header("HTTP/1.1 404 Not Found");
    exit('{"errno": 4,"msg": "无可用皮肤"}');
  }
  switch ($_GET['type']) {
case 'Skins':
  Header("HTTP/1.1 301 Found");
  Header("Location: textures/" . $row['HASH_steve']);
  break;  
case 'Cloaks':
  Header("HTTP/1.1 301 Found");
  Header("Location: textures/" . $row['HASH_cape']);
  break;
default:
  Header("HTTP/1.1 400 Bad Request");
  echo '{"errno": 4,"msg": "Bad Request"}';
  break;
  }
  exit(0);
}
?>