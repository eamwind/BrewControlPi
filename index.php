<!DOCTYPE html>
<html>

<body>
Current Temp: 
<output id="ctemp" display=inline value="150"></output>
 °
<output id="degcur" display=inline></output>
<br>Setpoint Temp:
<output id="stemp" display=inline></output>
 °
<output id="degset" display=inline></output>

<form method="post"> 
  <input type="submit" name="sendbutton" value=" Set ">
  <input type="text" name="newset" id="newset" value="<?php echo $settemp;?>">
  <br>
  <input  type="checkbox" id="onoff_toggle" name="onoff_toggle">
  Automation:
  <output id="onoffout" display = inline></output>
  <input type="hidden" id="downloaded" name="downloaded" value=" "></input>
</form>


<script>
function loadTemps() {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      allText = this.responseText
      lines = allText.split("\n");
      curtemp = lines[0];
      settemp = lines[1];
      celsius = lines[3];
      onoff = lines[4];
      document.getElementById("ctemp").innerHTML = curtemp;
      document.getElementById("stemp").innerHTML = settemp;
      if (celsius == "True") {
        document.getElementById("degcur").innerHTML = "C";
        document.getElementById("degset").innerHTML = "C";
      }
      else {
        document.getElementById("degcur").innerHTML = "F";
        document.getElementById("degset").innerHTML = "F";
      }
      if (onoff == "True"){
        document.getElementById("onoffout").innerHTML = "ON";
      }
      else {
        document.getElementById("onoffout").innerHTML = "OFF";
      }
      document.getElementById("downloaded").value = allText;
    }
  }
  xhttp.open("GET", "temps.txt", true);
  xhttp.send();
}
function constReload(){
   loadTemps();
   setInterval(loadTemps,1000);
}
constReload();
</script>



<?php
  if (isset($_POST["sendbutton"]) && (is_numeric($_POST["newset"])>0)) {
    $is_on = isset($_POST["onoff_toggle"]) ? "True" : "False";
    $froms = $_POST["downloaded"];
    $fromserver = explode("\n", $froms);
    $newfile = ($fromserver[0]."\n".$_POST["newset"]."\nweb\n".$fromserver[3]."\n".$is_on);
    $handle = fopen("temps.txt", "w");
    fwrite($handle,$newfile); 
    fclose($handle);
  }
?>

</body>
</html>
