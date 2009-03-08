var svgNS = "http://www.w3.org/2000/svg";

ajaxSensorStatus = setInterval("loadXMLDoc('http://localhost/sensorStatus.json')", 5000);

function createBadge(sensorId, sensorStatus)
{
       
    var centerX = Math.abs(parseInt(document.getElementById(sensorId).getAttributeNS(null,"y")));
    var centerY = Math.abs(parseInt(document.getElementById(sensorId).getAttributeNS(null,"x")));
    var radius = 13;
   
    switch (sensorStatus)
    {
        case "normal":
            fillColor="green";
            break;
        case "alert":
            fillColor="red";
            break;
        default:
            fillColor="black";
    }

    //create a new circle element and set the attributes
    var circle = document.createElementNS(svgNS,"circle");
        circle.setAttributeNS(null,"id",fillColor + "Badge");
    	circle.setAttributeNS(null,"cx",centerX);
    	circle.setAttributeNS(null,"cy",centerY);
    	circle.setAttributeNS(null,"r",radius);
    	circle.setAttributeNS(null,"fill",fillColor);
        circle.setAttributeNS(null,"style","visibility:hidden;");
        
    document.getElementById("layer1").appendChild(circle);
    document.getElementById('layer1').setAttribute("transform", "scale(0.79)"); 
}
            
var xmlhttp;
            
function loadXMLDoc(url)
{
    xmlhttp=null;
    xmlhttp=new XMLHttpRequest();
            
    if (xmlhttp!=null)
    {
        xmlhttp.onreadystatechange=state_Change;
        xmlhttp.open("GET",url,true);
        xmlhttp.send(null);
    }
    else
    {
        alert("Get Firefox, Tool!");
        window.location = "http://www.mozilla.com/firefox/";
    }
}

function badgeStatus(sensorStatus)
{ 
    switch (sensorStatus)
    {
        case "normal":
            document.getElementById('redBadge').style.visibility = 'hidden';
            document.getElementById('greenBadge').style.visibility = 'visible';
            break;
        case "alert":
            document.getElementById('greenBadge').style.visibility = 'hidden';
            document.getElementById('redBadge').style.visibility = 'visible';
            break;
        default:
            alert("Sensor Should NOT Be Sending A Status Of: " + sensorStatus);
    }
}

            
                
function state_Change()
{
    if (xmlhttp.readyState==4)
    {// 4 = "loaded"
        responseJSON = eval("(" + xmlhttp.responseText + ")");
                    
        sensorId = responseJSON.sensor.jsId;
        sensorStatus =  responseJSON.sensor.sensorStatus;

        badgeStatus(sensorStatus);
    }
}            
