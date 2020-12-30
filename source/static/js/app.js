function getSum() {

  var url = `/stocks`
  // Select the panel with id of `#account-sum`
  var panel = d3.select("#account-sum");
  // Clear any existing metadata
  //table.html("");

  var accountSum = 0;

  d3.json(url).then(function(data) {
    // Get the entries for each object in the array
    
    Object.entries(data).forEach(([key, value]) => {
      //console.log(`Key: ${key} and Value ${value.company}`); 
      accountSum += value.equity;
      });
    console.log(accountSum);
    panel.append("h2").text(["$",accountSum.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,')].join(""));
    });
}

function buildCharts(sample) {
  var url = "/samples/" + sample;
  // Fetch the sample data for the plots
  d3.json(url).then(function(data) {
    // Get the entries for each object in the array
    var otu_ids = data['otu_ids'];
    var otu_labels = data['otu_labels'];
    var sample_values = data['sample_values'];

    piedata = [{
        "labels": otu_ids.slice(0,10),
        "values": sample_values.slice(0,10),
        "hovertext": otu_labels.slice(0,10),
        "type": "pie"}]

    var layout = {
      title: "Top 10 OTUs",
      height: 400,
      width: 500}
    // Plot the Pie Chart
    Plotly.newPlot("pie", piedata, layout);

    // Build bubble chart
    var trace1 = {
      x: otu_ids,
      y: sample_values,
      hovertext: otu_labels,
      mode: 'markers',
      marker: {
        size: sample_values,
        color: otu_ids
      }
    };
    
    var bubdata = [trace1];
    
    var bublayout = {
      title: 'OTUs Found',
      showlegend: false,
      height: 600,
      width: 1000
    };

    // Plot the Bubble Chart using the sample data
    Plotly.newPlot('bubble', bubdata, bublayout);
  });
}

function loadTable() {
  var url = `/stocks`
  var table = d3.select("#summary-table");

  var tbody = table.select("tbody");
  var trow;

  // Clear any existing metadata
  tbody.html("");
  
  d3.json(url).then(function(data) {
  // Get the entries for each object in the array
  
  Object.entries(data).forEach(([key, value]) => {
    //console.log(`Key: ${key} and Value ${value.company}`); 
    trow = tbody.append("tr");
    trow.append("td").text(value.company)
    trow.append("td").text(value.symbol)
    trow.append("td").text(value.units.toFixed(2))
    trow.append("td").text(["$",value.price.toFixed(2)].join(""))
    trow.append("td").text(["$",value.avg_cost.toFixed(2)].join(""))
    trow.append("td").text(["$",value.total_return.toFixed(2)].join(""))
    trow.append("td").text(["$",value.equity.toFixed(2)].join(""))
    trow.append("td").text([value.total_gain.toFixed(2),"%"].join(""))
    trow.append("td").text([value.allocation.toFixed(2),"%"].join(""))
    });
  
  });
}


function init() {
  loadTable();
  getSum();
}

function optionChanged(newSample) {
  // Fetch new data each time a new sample is selected
  //buildCharts(newSample);
  buildMetadata(newSample);
  buildPlot(newSample);
}

// Initialize the dashboard
init();


///////////////////////////////

function sortTable(n) {
  var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
  table = document.getElementById("summary-table");
  switching = true;
  // Set the sorting direction to ascending:
  dir = "asc";
  /* Make a loop that will continue until
  no switching has been done: */
  while (switching) {
    // Start by saying: no switching is done:
    switching = false;
    rows = table.rows;
    /* Loop through all table rows (except the
    first, which contains table headers): */
    for (i = 1; i < (rows.length - 1); i++) {
      // Start by saying there should be no switching:
      shouldSwitch = false;
      /* Get the two elements you want to compare,
      one from current row and one from the next: */
      x = rows[i].getElementsByTagName("TD")[n];
      y = rows[i + 1].getElementsByTagName("TD")[n];
      /* Check if the two rows should switch place,
      based on the direction, asc or desc: */
      if (x.innerHTML.includes(".")){
        //console.log(parseFloat(x.innerHTML.replace("$","").replace("%","")));
        if (dir == "asc") {
          if (parseFloat(x.innerHTML.replace("$","").replace("%","")) > parseFloat(y.innerHTML.replace("$","").replace("%",""))) {
            // If so, mark as a switch and break the loop:
            shouldSwitch = true;
            break;
          }
        } else if (dir == "desc") {
          if (parseFloat(x.innerHTML.replace("$","").replace("%","")) < parseFloat(y.innerHTML.replace("$","").replace("%",""))) {
            // If so, mark as a switch and break the loop:
            shouldSwitch = true;
            break;
          }
        }
      }
      else {
        if (dir == "asc") {
          if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
            //console.log(x.innerHTML.toLowerCase());
            //console.log(typeof(x.innerHTML.toLowerCase()))
            // If so, mark as a switch and break the loop:
            shouldSwitch = true;
            break;
          }
        } else if (dir == "desc") {
          if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
            // If so, mark as a switch and break the loop:
            shouldSwitch = true;
            break;
          }
        }
      }
    }
    if (shouldSwitch) {
      /* If a switch has been marked, make the switch
      and mark that a switch has been done: */
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
      // Each time a switch is done, increase this count by 1:
      switchcount ++;
    } else {
      /* If no switching has been done AND the direction is "asc",
      set the direction to "desc" and run the while loop again. */
      if (switchcount == 0 && dir == "asc") {
        dir = "desc";
        switching = true;
      }
    }
  }
}

/**
 * Helper function to select stock data
 * Returns an array of values
 * @param {array} rows
 * @param {integer} index
 * index 0 - Date
 * index 1 - Open
 * index 2 - High
 * index 3 - Low
 * index 4 - Close
 * index 5 - Volume
 */
function unpack(rows, index) {
  return rows.map(function(row) {
    return row[index];
  });
}


function buildPlot(coin) {
  var url = `/historic/` + coin;

  d3.json(url).then(function(data) {

    //console.log(data.Close);
    // Grab values from the response json object to build the plots
    var name = coin;
    var stock = coin;
    var startDate = Date.parse(data.Date.slice(-1)[0])
    var endDate = Date.parse(data.Date[0])
    var dates = data.Date.map(x => Date.parse(x))
    var openingPrices = data.Open;
    var highPrices = data.High;
    var lowPrices = data.Low;
    var closingPrices = data.Close;
    var Volume = data.Volume;

    //getMonthlyData();

    var trace1 = {
      type: "scatter",
      mode: "lines",
      name: name,
      x: dates,
      y: closingPrices,
      line: {
        color: "#17BECF"
      }
    };

    // Candlestick Trace
    var trace2 = {
      type: "candlestick",
      x: dates,
      high: highPrices,
      low: lowPrices,
      open: openingPrices,
      close: closingPrices
    };

    var plot_data = [trace1, trace2];

    var layout = {
      title: `${stock} closing prices`,
      xaxis: {
        range: [startDate, endDate],
        //autorange: true,
        type: "date"
      },
      yaxis: {
        autorange: true,
        type: "linear"
      },
      showlegend: false
    };

    console.log('Start Date: ' + startDate);
    console.log('End Date: ' + endDate);
    console.log(Date.parse(dates));

    Plotly.newPlot("plot", plot_data, layout);
    //buildTable(data.Date, openingPrices, highPrices, lowPrices, closingPrices, Volume);
  });
}