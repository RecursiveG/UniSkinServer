<?php
$con = mysql_connect("localhost","username","password");
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
  switch ($_GET['type'])
  {
case 'Skins':
  Header("HTTP/1.1 301 Found");
  Header("Location: http://skins.minecraft.net/Minecraft" . $_GET['type'] . "/" . filename . ".png");
  break;  
case 'Cloaks':
  code to be executed if expression = label2;
  break;
default:
  Header("HTTP/1.1 403 Forbidden");
  echo "some err code";
}
?>