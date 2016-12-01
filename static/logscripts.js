var data;
var view;
var tops;
var bottoms;
var mDateSlider;
var jsonData
var resizeTimer;




function updateSlider(slideAmount) {
//get the element
var display = document.getElementById("setpoint");
//show the amount
display.innerHTML=slideAmount;
}

/*function settemp()
{
        var display = document.getElementById("setpoint");
        var level = display.textContent;
        var wanted = parseFloat(level);
        var nd = document.getElementById("nodes");
        var theNode = nd.options[nd.selectedIndex].value;
	console.log("setting temp" + theNode);
        //window.alert(wanted);
        var my_json = "";
        $.getJSON("{{url_for('set')}}?node="+theNode,{ temp: wanted},function(json){
		console.log("doing json");
                my_json =json;
                $("#update").text(json.stat);
                $("#newwort").text(json.tmp);
                if(json.stat == "success")
                {
                        window.alert("temp set " + json.tmp.toString() + " node:" + theNode);
                }
		else
		{
			window.alert("problem " + json.stat.toString() + " node:" + theNode);
		}
        });

         //$("#update").text("doneisn");
}
*/
function drawVisualization() {

        //if ((window.innerWidth <= 800 || window.innerHeight <= 600)) {
        //top.location.href="mobchart.html";
        //}
	console.log("drawing");
        var e = document.getElementById("Period");
        var strUser = e.options[e.selectedIndex].value;
        var nd = document.getElementById("nodes");
        var theNode = nd.options[nd.selectedIndex].value;
        console.log("data?days=" + strUser+"&node=" + theNode);
       jsonData = $.ajax({
          //url: "index.py/data",
          url: "data?days=" + strUser+"&node=" + theNode,
          dataType:"json",
          async: false
          }).responseText;
      // this new DataTable object holds all the data
       data = new google.visualization.DataTable(jsonData,0.6);
        var el = document.getElementById('setp');
        var am = document.getElementById('amb');
      view = new google.visualization.DataView(data);
        var cols = [0,1];
        if(el.checked)
        {
                cols.push(3);
        }
        if(am.checked)
        {
                cols.push(2);
        }
	//cols.push(4);
	console.log(cols);
        view.setColumns(cols);
 // Create a dashboard.
         var dash_container = document.getElementById('dashboard_div'),
                myDashboard = new google.visualization.Dashboard(dash_container);
// Create a date range slider
        myDateSlider = new google.visualization.ControlWrapper({
          'controlType': 'DateRangeFilter',
          'containerId': 'control_div',

          'options': {
            'filterColumnLabel': 'minutes',
             backgroundColor: '#141414'         
          }
        });

      // CAPACITY - En-route ATFM delay - YY - CHART
      var chart = new google.visualization.ChartWrapper({
         chartType: 'LineChart',
         containerId: 'crt_ertdlyYY',
        options:{
            width: '90%', height: '80%',
            title: 'Brewing temperatures-(minutes since midnight)',
            curveType: 'function',
            titleTextStyle : {color: 'grey', fontSize: 11},
            backgroundColor: '#E4E4E4',
            vAxis: { 
              title: "Temperature", 
              viewWindowMode:'explicit',
              viewWindow:{
                max:30,
                min:5
              }
                

                },
            
            hAxis: {
                //format: "D HH:mm"

          gridlines: {
            count: -1,
            units: {
              days: {format: ['MMM dd']}//,
            }
          },
          minorGridlines: {
            units: {
              hours: {format: ['HH:mm']}//,
            }
          }
                
        }

         }
      });
        
        myDashboard.bind(myDateSlider,chart);
        myDashboard.draw(view);
        var my_json = "";
        $.getJSON("raw?node="+theNode,function(json){
                my_json =json;
                $("#curitem").text(my_json.wort);
                 $("#setpoint").text(my_json.setpoint);
                var input = document.getElementById("skill");
                input.value = parseFloat(my_json.setpoint)
                });
         window.addEventListener("resize", debounce);

 $("#up2").click(function(){
        $("#up").css("background-color","peru");
        
 })

   }


function debounce()
{
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(function() {

    redrawVisualization();
            
  }, 250);
}


function redrawVisualization() {
      // this new DataTable object holds all the data
       data = new google.visualization.DataTable(jsonData,0.6);
        var el = document.getElementById('setp');
        var am = document.getElementById('amb');
      view = new google.visualization.DataView(data);
        var cols = [0,1];
        if(el.checked)
        {
                cols.push(3);
        }
        if(am.checked)
        {
                cols.push(2);
        }
	console.log(cols);
        view.setColumns(cols);
 // Create a dashboard.
         var dash_container = document.getElementById('dashboard_div'),
                myDashboard = new google.visualization.Dashboard(dash_container);
// Create a date range slider 
        var stater =  myDateSlider.getState();
        tops = stater.highValue;
        bottoms = stater.lowValue;
        myDateSlider = new google.visualization.ControlWrapper({
          'controlType': 'DateRangeFilter',
          'containerId': 'control_div',
        'state': {'lowValue': bottoms, 'highValue': tops},
          'options': {
            'filterColumnLabel': 'minutes'
                
          }
        });

      // CAPACITY - En-route ATFM delay - YY - CHART
      var chart = new google.visualization.ChartWrapper({
         chartType: 'LineChart',
         containerId: 'crt_ertdlyYY',
        options:{
            width: '90%', height: '80%',
            title: 'Brewing temperatures-(minutes since midnight)',
            curveType: 'function',
            titleTextStyle : {color: 'grey', fontSize: 11},
            backgroundColor: '#E4E4E4',
            vAxis: { 
              title: "Temperature", 
              viewWindowMode:'explicit',
              viewWindow:{
                max:30,
                min:5
              }
            },
            hAxis: {
                //format: "D HH:mm"

          gridlines: {
            count: -1,
            units: {
              days: {format: ['MMM dd']}//,
            }
          },
          minorGridlines: {
            units: {
              hours: {format: ['HH:mm']}//,
            }
          }
                
        }


         }
      });
        
        myDashboard.bind(myDateSlider,chart);
        myDashboard.draw(view);
    /*    var my_json = "";
        $.getJSON("dbservice/raw",function(json){
                my_json =json;
                $("#curitem").text(my_json.wort);
                 $("#setpoint").text(my_json.setpoint);
                console.log("changed")
                });*/
      //window.addEventListener("resize", redrawVisualization);
   }


google.setOnLoadCallback(drawVisualization)

