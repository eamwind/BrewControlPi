<!DOCTYPE html>
<html>

<body>
Current Temp:  <output id="ctemp" display=inline></output>
<?php echo " °F<br>";?>
Set Temp:  <output id="stemp" display=inline></output>
<?php echo " °F<br>";?>

<script>
function loadTemps() {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      lines = this.responseText.split("\n");
      curtemp = lines[0];
      settemp = lines[1];
      document.getElementById("ctemp").innerHTML = curtemp;
      document.getElementById("stemp").innerHTML = settemp;
    }
  };
  xhttp.open("GET", "temps.txt", true);
  xhttp.send();
}
function constReload(){
   loadTemps()
   setInterval(loadTemps,1000)
}
constReload()
</script>

<?php
  if ((isset($_POST['sendbutton']) && (isset($_POST['newset'])))){
    $newfile = ("0.0\n".$_POST['newset']."\nweb");
    $handle = fopen("temps.txt", 'w'); 
    fwrite($handle,$newfile); 
    fclose($handle);
  }
?>

<form method="post"> 
   <input type="submit" name="sendbutton" value="Set Target Temp">
   <input type="text" name="newset" id="newset" value="<?php echo $settemp;?>">
</form>

</body>
</html>
