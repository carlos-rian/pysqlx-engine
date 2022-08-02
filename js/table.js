// Table
document$.subscribe(function() {
    var tables = document.querySelectorAll("article table")
    tables.forEach(function(table) {
      new Tablesort(table)
    })
  })


// keyboard 
keyboard$.subscribe(function(key) {
    if (key.mode === "global" && key.type === "x") {
      /* Add custom keyboard handler here */
      key.claim()
    }
  })
  